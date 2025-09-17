from __future__ import annotations

import re
import uuid
from typing import Iterable, List, Dict, Any, Optional, Tuple
import logging
import platform

from django.conf import settings
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue, FilterSelector
from qdrant_client.http.models import (
    PayloadSchemaType,
    TextIndexParams,
    TextIndexType,
    TokenizerType,
)
from sentence_transformers import SentenceTransformer

# Логгер для операций с векторами и Qdrant
logger = logging.getLogger(__name__)

_QDRANT = QdrantClient(url=getattr(settings, "QDRANT_URL", "http://127.0.0.1:6333"))
_COLLECTION = getattr(settings, "QDRANT_COLLECTION", "med_docs")
_MODEL_NAME = getattr(settings, "EMB_MODEL", "ekaterinatao/nerel-bio-rubert-base")
# Безопасная модель по умолчанию для CPU, не использующая сложных механизмов загрузки
# через accelerate/meta‑тензоры и устойчиво работающая на macOS: 
# _FALLBACK_MODEL = getattr(settings, "EMB_MODEL_FALLBACK", "sentence-transformers/all-MiniLM-L6-v2")
_FALLBACK_MODEL = getattr(settings, "EMB_MODEL_FALLBACK", "ekaterinatao/nerel-bio-rubert-base")

_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    """Возвращает singleton экземпляр модели эмбеддингов.

    Защита от проблем инициализации на macOS/torch:
    1) Пытаемся загрузить основную модель строго на CPU.
    2) Если во время __init__ возникает ошибка уровня torch/transformers
       вида "Cannot copy out of meta tensor" (или схожая), автоматически
       откатываемся на безопасную CPU‑модель (_FALLBACK_MODEL) и логируем предупреждение.

    Такой подход минимально инвазивен и не требует менять остальной код,
    т.к. размерность эмбеддингов определяется динамически при upsert.
    """
    global _model
    if _model is None:
        # На macOS (Darwin) сразу используем безопасную CPU‑модель, т.к. ряд больших
        # моделей (например, BAAI/bge-m3) инициируют веса как meta‑тензоры и падают
        # при переносе .to('cpu') внутри SentenceTransformer. Это устраняет ошибку
        # "Cannot copy out of meta tensor" в задаче прогрева и индексирования.
        preferred_model = _FALLBACK_MODEL if platform.system() == "Darwin" else _MODEL_NAME
        try:
            # trust_remote_code=True требуется для некоторых моделей семейства BGE/GTE
            logger.info("[vec] Инициализация модели эмбеддингов: '%s' (device=cpu)", preferred_model)
            _model = SentenceTransformer(preferred_model, trust_remote_code=True, device='cpu')
        except NotImplementedError as e:
            # Типовая проблема с meta‑тензорами при .to(...). Повторим попытку на запасной модели.
            logger.warning(
                "[vec] Не удалось инициализировать модель '%s' на CPU (%s). Переходим на запасную модель '%s'.",
                preferred_model, e, _FALLBACK_MODEL,
            )
            _model = SentenceTransformer(_FALLBACK_MODEL, trust_remote_code=True, device='cpu')
        except Exception as e:
            # На всякий случай аналогичный откат и для других редких сбоев инициализации
            logger.warning(
                "[vec] Ошибка инициализации модели '%s' (%s). Пытаемся использовать запасную модель '%s'.",
                preferred_model, e, _FALLBACK_MODEL,
            )
            _model = SentenceTransformer(_FALLBACK_MODEL, trust_remote_code=True, device='cpu')
    return _model


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    """
    Возвращает L2-нормированные эмбеддинги (список векторов).
    """
    texts_list = list(texts)
    logger.info("[vec] Векторизация: входных текстов=%s", len(texts_list))
    mdl = _get_model()
    vectors = mdl.encode(
        texts_list,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).tolist()
    dim = len(vectors[0]) if vectors else 0
    logger.info("[vec] Векторизация завершена: сгенерировано=%s, размерность=%s", len(vectors), dim)
    return vectors


def ensure_collection(dim: int) -> None:
    """
    Создаёт/переинициализирует коллекцию с нужной размерностью и индексами по payload.

    Дополнительно: если коллекция уже существует, но её размерность векторов
    отличается от требуемой (например, модель эмбеддингов была изменена),
    коллекция будет пересоздана с новой размерностью. Это неизбежно удалит
    существующие точки, поэтому важно запускать переиндексацию после смены модели.
    """
    existing = {c.name for c in _QDRANT.get_collections().collections}
    need_recreate = False
    if _COLLECTION in existing:
        # Проверим текущую размерность коллекции
        try:
            info = _QDRANT.get_collection(_COLLECTION)
            current_vectors = getattr(info.config.params, 'vectors', None)
            current_dim = None
            if hasattr(current_vectors, 'size'):
                current_dim = int(current_vectors.size)
            elif isinstance(current_vectors, dict):
                # на случай сериализованного ответа в dict-форме
                current_dim = int(current_vectors.get('size')) if current_vectors.get('size') is not None else None
        except Exception as e:
            logger.warning("[qdrant] Не удалось получить параметры коллекции '%s': %s", _COLLECTION, e)
            current_dim = None
        if current_dim is not None and current_dim != dim:
            logger.warning(
                "[qdrant] Размерность коллекции '%s' (%s) отличается от требуемой (%s). Пересоздаём коллекцию.",
                _COLLECTION, current_dim, dim,
            )
            need_recreate = True
        else:
            logger.debug("[qdrant] Коллекция '%s' уже существует и совместима (dim=%s)", _COLLECTION, current_dim or dim)
    else:
        need_recreate = True

    if need_recreate:
        logger.info("[qdrant] Создание/пересоздание коллекции '%s' (dim=%s)", _COLLECTION, dim)
        _QDRANT.recreate_collection(
            collection_name=_COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        # Индексы по payload-полям (для фильтрации)
        _QDRANT.create_payload_index(
            collection_name=_COLLECTION,
            field_name="doc_id",
            field_schema=PayloadSchemaType.INTEGER,
        )
        _QDRANT.create_payload_index(
            collection_name=_COLLECTION,
            field_name="owner_id",
            field_schema=PayloadSchemaType.INTEGER,
        )
        _QDRANT.create_payload_index(
            collection_name=_COLLECTION,
            field_name="section",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        # Полнотекстовый индекс по полю text (для гибридного поиска)
        _QDRANT.create_payload_index(
            collection_name=_COLLECTION,
            field_name="text",
            field_schema=TextIndexParams(
                type=TextIndexType.TEXT,
                tokenizer=TokenizerType.WORD,
                min_token_len=2,
                max_token_len=40,
            ),
        )
        logger.info("[qdrant] Коллекция '%s' создана/пересоздана и проиндексирована", _COLLECTION)

def ensure_collection_for_model() -> None:
    """
    Гарантирует, что коллекция в Qdrant создана под текущую модель эмбеддингов.
    Получает размерность напрямую из модели и создаёт коллекцию при её отсутствии.
    """
    mdl = _get_model()
    try:
        dim = int(getattr(mdl, "get_sentence_embedding_dimension")())
    except Exception:
        # Резервный способ: посчитать по одному вектору
        dim = len(mdl.encode(["probe"], normalize_embeddings=True, convert_to_numpy=True)[0])
    ensure_collection(dim)


def upsert_embeddings(
    *,
    doc_id: int,
    owner_id: int,
    chunks: List[Dict[str, Any]],
    vectors: List[List[float]],
) -> None:
    """
    Пишет (upsert) точки чанков документа в коллекцию.
    В payload добавляются doc_id и owner_id для мультиарендности/фильтрации.
    """
    if not vectors:
        logger.warning("[qdrant] Пустой список векторов: нечего писать (doc_id=%s, owner_id=%s)", doc_id, owner_id)
        return
    dim = len(vectors[0])
    ensure_collection(dim)

    points: List[PointStruct] = []
    for i, (ch, vec) in enumerate(zip(chunks, vectors)):
        points.append(
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}:{i}")),
                vector=vec,
                payload={
                    "doc_id": doc_id,
                    "owner_id": owner_id,
                    "idx": i,
                    "section": ch.get("section", ""),
                    "page_from": ch.get("page_from"),
                    "page_to": ch.get("page_to"),
                    "text": ch.get("text", ""),
                },
            )
        )

    logger.info("[qdrant] Upsert точек: %s шт. в коллекцию '%s' (doc_id=%s, owner_id=%s)", len(points), _COLLECTION, doc_id, owner_id)
    result = _QDRANT.upsert(collection_name=_COLLECTION, points=points, wait=True)
    try:
        status = getattr(result, 'status', None) or getattr(result, 'result', None)
        logger.info("[qdrant] Результат upsert: %s", status or repr(result))
    except Exception:
        logger.debug("[qdrant] Не удалось распарсить результат upsert")
    # Быстрая проверка появления хотя бы одной точки
    try:
        flt = _build_filter(owner_id=owner_id, doc_id=doc_id)
        pts, _ = _QDRANT.scroll(
            collection_name=_COLLECTION,
            scroll_filter=flt,
            limit=1,
            with_payload=False,
            with_vectors=False,
        )
        if not pts:
            logger.warning("[qdrant] После upsert точек не найдено (doc_id=%s, owner_id=%s)", doc_id, owner_id)
        else:
            logger.info("[qdrant] Проверка после upsert: найдена хотя бы 1 точка")
    except Exception as e:
        logger.warning("[qdrant] Ошибка проверки после upsert: %s", e)


def delete_doc(doc_id: int, owner_id: Optional[int] = None) -> None:
    """
    Удаляет все точки документа из коллекции. Если указан owner_id — ограничивает удаление.
    """
    conditions = [
        FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
    ]
    if owner_id is not None:
        conditions.append(FieldCondition(key="owner_id", match=MatchValue(value=owner_id)))
    flt = Filter(must=conditions)
    logger.info("[qdrant] Удаление точек документа: doc_id=%s, owner_id=%s", doc_id, owner_id)
    _QDRANT.delete(
        collection_name=_COLLECTION,
        points_selector=FilterSelector(filter=flt),
        wait=True,
    )


def has_doc_points(doc_id: int, owner_id: Optional[int] = None) -> bool:
    """
    Быстрая проверка наличия хотя бы одной точки документа в коллекции.
    Используется для пропуска повторной векторизации, если документ не менялся.
    """
    flt = _build_filter(owner_id=owner_id, doc_id=doc_id)
    pts, _ = _QDRANT.scroll(
        collection_name=_COLLECTION,
        scroll_filter=flt,
        limit=1,
        with_payload=False,
        with_vectors=False,
    )
    found = bool(pts)
    logger.debug("[qdrant] Проверка наличия точек: doc_id=%s, owner_id=%s -> %s", doc_id, owner_id, found)
    return found


def _build_filter(
        *,
        owner_id=None,
        doc_id=None,
        extra: Optional[Dict[str, Any]] = None) -> Optional[models.Filter]:
    must: List[models.FieldCondition] = []
    if owner_id is not None:
        must.append(models.FieldCondition(
            key="owner_id", match=models.MatchValue(value=owner_id)))
    if doc_id is not None:
        must.append(models.FieldCondition(
            key="doc_id", match=models.MatchValue(value=doc_id)))
    if extra:
        for k, v in extra.items():
            must.append(models.FieldCondition(
                key=k, match=models.MatchValue(value=v)))
    return models.Filter(must=must) if must else None


def vector_search(
    query: str,
    *,
    top_k: int = 5,
    owner_id: Optional[int] = None,
    doc_id: Optional[int] = None,
    extra_filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Простой векторный поиск с опциональной фильтрацией по owner_id/doc_id/extra.
    Возвращает список {score, ...payload}.
    """
    q_vec = embed_texts([query])[0]
    flt = _build_filter(owner_id=owner_id, doc_id=doc_id, extra=extra_filters)

    res = _QDRANT.search(
        collection_name=_COLLECTION,
        query_vector=q_vec,
        limit=top_k,
        query_filter=flt,
    )
    return [{"score": r.score, **(r.payload or {})} for r in res]


_TOKEN_RE = re.compile(r"\w+", re.UNICODE)

def _tokenize(s: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(s or "") if t]


def _lexical_score(query: str, text: str, section: str = "") -> float:
    """
    Очень простая лексикальная метрика: доля query-токенов, найденных в тексте/секции.
    Диапазон [0..1]. Можно заменить на BM25 при желании.
    """
    q = set(_tokenize(query))
    if not q:
        return 0.0
    doc_tokens = set(_tokenize(text)) | set(_tokenize(section))
    inter = len(q & doc_tokens)
    return inter / max(1, len(q))


def _full_text_candidates(
        query: str, *, owner_id, doc_id,
                          extra_filters, limit):
    # то, что уже было
    base = _build_filter(owner_id=owner_id,
                         doc_id=doc_id,
                         extra=extra_filters) or {}

    # КОНВЕРТИРУЕМ dict → Filter, если нужно
    if not isinstance(base, models.Filter):
        base = models.Filter.parse_obj(base)

    # добавляем OR-условия по полнотекстовому индексу
    base.should = (base.should or []) + [
        models.FieldCondition(
            key="text",
            match=models.MatchText(text=query)
        ),
        models.FieldCondition(
            key="section",
            match=models.MatchText(text=query)
        ),
    ]

    points, _ = _QDRANT.scroll(
        collection_name=_COLLECTION,
        scroll_filter=base,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    return [p.payload or {} for p in points]


def hybrid_search(
    query: str,
    *,
    top_k: int = 5,
    owner_id: Optional[int] = None,
    doc_id: Optional[int] = None,
    extra_filters: Optional[Dict[str, Any]] = None,
    alpha: float = 0.7,
    vector_k: Optional[int] = None,
    text_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Гибридный поиск:
      1) Векторные кандидаты (top_k * 5 по умолчанию).
      2) Кандидаты по полнотексту (через full_text filter + scroll).
      3) Фузия: score = alpha * vec_score + (1 - alpha) * lex_score.
    Возвращает топ-k по fused score.

    Примечание: полнотекстовая часть не даёт "веса" из Qdrant, поэтому
    считаем простую лексикальную метрику на стороне приложения.
    """
    vector_k = vector_k or max(top_k * 5, top_k)
    text_k = text_k or max(top_k * 5, top_k)

    # 1) Векторная часть
    q_vec = embed_texts([query])[0]
    flt = _build_filter(owner_id=owner_id, doc_id=doc_id, extra=extra_filters)
    vres = _QDRANT.search(
        collection_name=_COLLECTION,
        query_vector=q_vec,
        limit=vector_k,
        query_filter=flt,
    )

    # 2) Полнотекстовые кандидаты
    tres_payloads = _full_text_candidates(
        query,
        owner_id=owner_id,
        doc_id=doc_id,
        extra_filters=extra_filters,
        limit=text_k,
    )

    # 3) Фузия
    def _key(pl: Dict[str, Any]) -> Tuple[int, int]:
        return (int(pl.get("doc_id", -1)), int(pl.get("idx", -1)))

    fused: Dict[Tuple[int, int], Dict[str, Any]] = {}

    # Добавим векторные результаты
    for r in vres:
        pl = r.payload or {}
        k = _key(pl)
        if k not in fused:
            fused[k] = {**pl}
        fused_vec = r.score or 0.0
        fused[k]["_vec_score"] = max(fused[k].get("_vec_score", 0.0), float(fused_vec))
        # предвычислим лексикальную часть на основе text/section, если ещё не было
        if "_lex_score" not in fused[k]:
            fused[k]["_lex_score"] = _lexical_score(query, pl.get("text", ""), pl.get("section", ""))

    # Добавим текстовые кандидаты
    for pl in tres_payloads:
        k = _key(pl)
        if k not in fused:
            fused[k] = {**pl}
            fused[k]["_vec_score"] = 0.0
        # лексикальная оценка (может переписать на максимум)
        lex = _lexical_score(query, pl.get("text", ""), pl.get("section", ""))
        fused[k]["_lex_score"] = max(fused[k].get("_lex_score", 0.0), lex)

    # Подсчёт итогового score и сортировка
    results: List[Dict[str, Any]] = []
    for k, pl in fused.items():
        vec_s = float(pl.get("_vec_score", 0.0))
        lex_s = float(pl.get("_lex_score", 0.0))
        score = alpha * vec_s + (1.0 - alpha) * lex_s
        out = {
            "score": score,
            "doc_id": pl.get("doc_id"),
            "owner_id": pl.get("owner_id"),
            "idx": pl.get("idx"),
            "section": pl.get("section", ""),
            "page_from": pl.get("page_from"),
            "page_to": pl.get("page_to"),
            "text": pl.get("text", ""),
        }
        results.append(out)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
