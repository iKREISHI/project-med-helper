import io, hashlib, logging
from celery import shared_task
from django.core.files.storage import default_storage
from django.db import transaction
from .models import Document, Chunk
from .text_utils import extract_text_with_layout, split_into_chunks
from .vectors import embed_texts, upsert_embeddings, delete_doc, _get_model, has_doc_points

# Логгер модуля задач индексирования
logger = logging.getLogger(__name__)

def _sha256(b:bytes)->str:
    h=hashlib.sha256(); h.update(b); return h.hexdigest()

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def pipeline_index_document(self, doc_id:int):
    """Индексирует документ по его идентификатору: парсинг, сохранение чанков в БД,
    вычисление эмбеддингов и загрузка точек в Qdrant.

    Параметры:
    - doc_id: int — идентификатор документа в БД.
    """
    logger.info("[index] Старт пайплайна индексирования: doc_id=%s", doc_id)
    doc = Document.objects.get(pk=doc_id)
    try:
        # Читаем файл и считаем хэш для определения, изменился ли документ
        with default_storage.open(doc.file.name, "rb") as f:
            raw = f.read()
        current_sha = _sha256(raw)
        logger.debug("[index] Вычислен sha256=%s для doc_id=%s", current_sha, doc_id)

        # Идемпотентность: если документ уже индексирован, хэш не изменился и
        # в Qdrant есть точки этого документа — пропускаем повторную векторизацию
        # Признак наличия уже сохранённых чанков в БД
        chunks_exist = Chunk.objects.filter(document=doc).exists()
        if (
            doc.status == Document.Status.INDEXED
            and (doc.meta or {}).get("sha256") == current_sha
            and has_doc_points(doc.id, owner_id=doc.owner_id)
            and chunks_exist
        ):
            logger.info(
                "[index] Пропуск индексирования: документ не менялся, точки и чанки уже существуют (doc_id=%s, owner_id=%s)",
                doc.id, doc.owner_id,
            )
            return "skipped: already indexed and unchanged"

        # Обновляем метаданные и переходим к парсингу/чанкингу
        base_meta = dict(doc.meta or {})
        base_meta["sha256"] = current_sha
        doc.meta = base_meta
        parsed = extract_text_with_layout(io.BytesIO(raw), content_type=doc.content_type or "")
        # Если по какой-то причине plain пустой, но страницы присутствуют — соберём plain из страниц
        if (not (parsed.get("plain") or "").strip()) and parsed.get("pages"):
            try:
                parsed["plain"] = "\n\n".join((p.get("text") or "") for p in parsed.get("pages") if (p.get("text") or "").strip()).strip()
                logger.info("[index] Применён фолбэк: plain реконструирован из pages (%s страниц)", len(parsed.get("pages", [])))
            except Exception:
                logger.warning("[index] Не удалось пересобрать plain из pages, продолжаем как есть")
        doc.title = doc.title or parsed.get("title") or doc.file.name
        doc.status = Document.Status.PARSED
        doc.meta["pages"] = len(parsed.get("pages", []))
        doc.save(update_fields=["title","status","meta"])
        logger.info(
            "[index] Парсинг завершён: pages=%s, title='%s'",
            doc.meta.get("pages"), doc.title,
        )

        # 1) Чанкинг исходного текста
        logger.info("[index] Старт чанкинга текста (target_tokens=350, overlap=50)")
        split = split_into_chunks(parsed, target_tokens=350, overlap=50)
        logger.info("[index] Чанкинг завершён: получено чанков=%s", len(split))

        # Если по какой-то причине разбиение вернуло 0 чанков, попробуем аварийный фолбэк:
        # один большой чанк со всем текстом, чтобы не блокировать пайплайн и можно было видеть результат в админке.
        if not split:
            plain_text = (parsed or {}).get("plain") or ""
            if plain_text.strip():
                logger.warning("[index] split_into_chunks вернул 0; создаём аварийный одиночный чанк из всего текста")
                split = [{
                    "text": plain_text.strip(),
                    "section": (doc.title or ""),
                    "page_from": 1,
                    "page_to": (doc.meta or {}).get("pages") or None,
                    "tokens": None,
                }]
            else:
                logger.error("[index] Пустой результат парсинга: нет текста для сохранения чанков (doc_id=%s)", doc.id)
                raise ValueError("Парсер вернул пустой текст; нечего сохранять в чанки")

        # 2) Сохраняем чанки в БД (обязательно с владельцем) и затем работаем уже с БД-объектами
        with transaction.atomic():
            deleted = Chunk.objects.filter(document=doc).delete()
            if isinstance(deleted, tuple):
                logger.debug("[index] Удалено старых чанков: %s", deleted[0])
            Chunk.objects.bulk_create([
                Chunk(owner=doc.owner, document=doc, idx=i, text=ch["text"],
                      section=ch.get("section",""),
                      page_from=ch.get("page_from"), page_to=ch.get("page_to"),
                      tokens=ch.get("tokens"))
                for i, ch in enumerate(split)
            ], batch_size=500)
        # Контрольная проверка: действительно ли появились записи в БД
        created_count = Chunk.objects.filter(document=doc).count()
        if created_count <= 0:
            logger.error("[index] После сохранения чанков их количество = 0 (doc_id=%s)", doc.id)
            raise RuntimeError("Не удалось сохранить чанки в базу данных")
        logger.info("[index] Сохранены чанки в БД: %s шт.", created_count)

        # Заново читаем сохранённые чанки из БД в гарантированном порядке
        db_chunks = list(Chunk.objects.filter(document=doc).order_by("idx").only(
            "idx", "text", "section", "page_from", "page_to"
        ))
        logger.debug("[index] Перечитано чанков из БД: %s", len(db_chunks))

        # 3) Эмбеддинги и запись в Qdrant
        logger.info("[index] Старт векторизации текста: %s чанков", len(db_chunks))
        # Гарантируем, что коллекция Qdrant создана под текущую модель (на случай, если прогрев не выполнялся)
        try:
            from .vectors import ensure_collection_for_model
            ensure_collection_for_model()
        except Exception:
            logger.warning("[index] Не удалось заранее убедиться в наличии коллекции Qdrant — продолжим, upsert попробует сам")
        vectors = embed_texts([c.text for c in db_chunks])
        vec_dim = len(vectors[0]) if vectors else 0
        logger.info("[index] Векторизация завершена: сгенерировано=%s, размерность=%s", len(vectors), vec_dim)
        # Идемпотентность: удалим старые точки этого документа конкретного владельца
        logger.info("[index] Удаление прежних точек из Qdrant: doc_id=%s, owner_id=%s", doc.id, doc.owner_id)
        delete_doc(doc.id, owner_id=doc.owner_id)
        # Преобразуем к структуре, ожидаемой upsert (минимально инвазивно)
        chunks_payload = [
            {
                "text": c.text,
                "section": c.section or "",
                "page_from": c.page_from,
                "page_to": c.page_to,
            }
            for c in db_chunks
        ]
        logger.info(
            "[index] Отправка векторов в Qdrant: points=%s, doc_id=%s, owner_id=%s",
            len(chunks_payload), doc.id, doc.owner_id,
        )
        upsert_embeddings(
            doc_id=doc.id,
            owner_id=doc.owner_id,
            chunks=chunks_payload,
            vectors=vectors,
        )
        logger.info("[index] Upsert в Qdrant завершён: doc_id=%s, owner_id=%s", doc.id, doc.owner_id)

        doc.status = Document.Status.INDEXED
        doc.save(update_fields=["status"])
        logger.info("[index] Индексирование успешно завершено: doc_id=%s", doc.id)
    except Exception as e:
        logger.exception("[index] Ошибка пайплайна индексирования doc_id=%s: %s", doc_id, e)
        doc.status = Document.Status.FAILED
        doc.error = str(e)
        doc.save(update_fields=["status","error"])
        raise


@shared_task(bind=True)
def warm_embeddings_model(self):
    """Тёплый старт модели эмбеддингов для снижения холодных задержек.
    Загружает модель в память и выполняет пробное кодирование.
    Дополнительно гарантирует создание коллекции в Qdrant под текущую модель.
    Без аргументов — удобно вызывать из celery beat.
    """
    from .vectors import ensure_collection_for_model
    logger.info("[warmup] Старт прогрева модели эмбеддингов")
    mdl = _get_model()
    logger.debug("[warmup] Модель загружена: %s", getattr(mdl, "__class__", type(mdl)).__name__)
    # Минимальный прогрев: одно короткое предложение
    try:
        mdl.encode(["warmup"], normalize_embeddings=True)
        logger.debug("[warmup] Пробное кодирование выполнено")
    except Exception:
        # Даже если encode упал (например, нет ускорений), сама загрузка уже полезна
        logger.warning("[warmup] Пробное кодирование завершилось с ошибкой, продолжаем")
        pass
    # Обеспечим создание коллекции заранее, чтобы она существовала до первой индексации
    try:
        ensure_collection_for_model()
        logger.info("[warmup] Коллекция Qdrant подготовлена под текущую модель")
    except Exception:
        # Не валим задачу прогрева из‑за проблем с Qdrant; они всплывут в основной пайплайн
        logger.warning("[warmup] Не удалось подготовить коллекцию Qdrant во время прогрева")
        pass
    model_name = getattr(mdl, "__class__", type(mdl)).__name__
    logger.info("[warmup] Прогрев завершён: %s", model_name)
    return model_name


@shared_task(bind=True)
def enqueue_pending_documents(self, limit: int = 50):
    """Периодическая задача: находит документы, ожидающие индексирования,
    и ставит для них пайплайн в очередь. Это страховка на случай, если по каким‑то
    причинам задача не была поставлена из API."""
    from .models import Document
    try:
        pending = list(
            Document.objects.filter(status__in=[Document.Status.UPLOADED, Document.Status.PARSED])
            .order_by("created_at")[:limit]
        )
    except Exception as e:
        logger.warning("[sched] Не удалось получить список ожидающих документов: %s", e)
        return 0
    scheduled = 0
    for doc in pending:
        try:
            logger.info("[sched] Постановка индексирования в очередь: doc_id=%s", doc.id)
            pipeline_index_document.delay(doc.id)
            scheduled += 1
        except Exception as e:
            logger.warning("[sched] Ошибка постановки задачи для doc_id=%s: %s", doc.id, e)
    logger.info("[sched] Запланировано задач индексирования: %s", scheduled)
    return scheduled
