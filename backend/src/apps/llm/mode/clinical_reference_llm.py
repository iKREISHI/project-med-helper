"""
clinical_llm.py
~~~~~~~~~~~~~~~~

Обёртка над поисковым слоем (`vector_search` / `hybrid_search`) и провайдером LLM,
которая

* ищет релевантные фрагменты;
* очищает их перед передачей в модель;
* формирует промпт согласно клиническим правилам (системный промпт можно
  переопределить через конструктор);
* **логирует** все этапы через *Django-совместимый* логгер;
* подсчитывает токены промпта/ответа;
* возвращает готовый ответ или поток токенов.

Логирование
-----------
Модуль использует `logging.getLogger("django.clinical_llm")`, поэтому сообщения
автоматически проходят через конфигурацию `LOGGING` в `settings.py` и будут
видны во *всех* подключённых хендлерах (файл, консоль, Sentry и т.д.).
Если в `LOGGING` не прописано отдельного логгера `"django.clinical_llm"`,
сообщения всплывут к корневому `"django"`.

Учёт токенов
------------
Если установлен *tiktoken* и передано имя модели через
`provider_params["model"]`, токены считаются точно; иначе — приблизительно.

Пример использования
~~~~~~~~~~~~~~~~~~~~
```python
from clinical_llm import ClinicalLLM, DEFAULT_SYSTEM_PROMPT

custom_prompt = DEFAULT_SYSTEM_PROMPT + "\n6. Не упоминай, какой ты модель."

llm = ClinicalLLM(
    search_mode="hybrid",
    k=3,
    system_prompt=custom_prompt,
    provider_params={"model": "gpt-4o"},
)
print(llm.ask("Какова доза статинов при высоком риске ИБС?"))
```
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Callable

from apps.docs_ingest.vectors import vector_search, hybrid_search
from apps.llm.llm_providers import get_provider

__all__ = ["ClinicalLLM", "DEFAULT_SYSTEM_PROMPT"]


logger = logging.getLogger("django.clinical_llm")

DEFAULT_SYSTEM_PROMPT = (
    "Ты — справочная LLM-система для врачей-клиницистов.\n\n"
    "ПРАВИЛА РАБОТЫ\n"
    "1. Отвечай только на основании текста из секции CONTEXT. Не добавляй информацию из иных источников.\n"
    "2. Если нужного факта нет в CONTEXT, ответь ровно фразой:\n"
    "   «✘ По предоставленным клиническим рекомендациям данных нет».\n"
    "3. После каждого утверждения указывай квадратные скобки с индексом фрагмента CONTEXT, например [CTX-2].\n"
    "4. Формат ответа:\n"
    "   • Краткое заключение (1–2 предложения, ≤120 слов).\n"
    "   • Раздел «Рекомендации» маркированным списком.\n"
    "   • При необходимости раздел «Ссылки» списком индексов.\n"
    "5. Язык ответа — русский.\n"
    "6. Ответ предназначен только для квалифицированного медицинского персонала и не является окончательным клиническим решением."
)

_BULLET_RE = re.compile(r"^[\u2022•\-–]\s*", flags=re.MULTILINE)
_WS_RE: re.Pattern[str] = re.compile(r"\s+")

try:
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover
    tiktoken = None


def _clean_paragraph(text: str) -> str:
    text = _BULLET_RE.sub("", text)
    paragraphs: list[str] = []
    for block in text.split("\n\n"):
        block = _WS_RE.sub(" ", block.replace("\n", " ")).strip()
        if block:
            paragraphs.append(block)
    return "\n\n".join(paragraphs)


def _approx_token_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _count_chatml_tokens(messages: List[Dict[str, str]], model: str | None) -> int:
    if tiktoken is None or model is None:
        return _approx_token_count(" ".join(m["content"] for m in messages))
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")  # type: ignore[arg-type]

    tokens = 2  # <im_start>assistant
    for m in messages:
        tokens += 4  # overhead per message
        tokens += len(encoding.encode(m.get("content", "")))
    return tokens


class ClinicalLLM:
    """Высокоуровневый интерфейс LLM с настраиваемым системным промптом."""

    _SEARCH_FUNCS: dict[str, Callable[..., List[Dict[str, Any]]]] = {
        "vector": vector_search,
        "hybrid": hybrid_search,
    }

    def __init__(
        self,
        *,
        search_mode: str = "hybrid",
        k: int = 5,
        owner_id: int | None = None,
        doc_id: int | None = None,
        section: str | None = None,
        provider_params: Dict[str, Any] | None = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        search_mode = search_mode.lower()
        if search_mode not in self._SEARCH_FUNCS:
            raise ValueError(
                f"search_mode должен быть 'vector' или 'hybrid', получено: {search_mode}"
            )

        self.search_mode = search_mode
        self.k = k
        self.owner_id = owner_id
        self.doc_id = doc_id
        self.section = section
        self.provider_params = provider_params or {}
        self.system_prompt = system_prompt

        logger.debug(
            "ClinicalLLM initialised | mode=%s | k=%s | prompt_len=%d",
            self.search_mode,
            self.k,
            len(self.system_prompt),
        )

    def _retrieve_context(
        self,
        query: str,
        *,
        k: int | None = None,
        owner_id: int | None = None,
        doc_id: int | None = None,
        section: str | None = None,
    ) -> List[str]:
        search_fn = self._SEARCH_FUNCS[self.search_mode]

        k = k if k is not None else self.k
        owner_id = owner_id if owner_id is not None else self.owner_id
        doc_id = doc_id if doc_id is not None else self.doc_id
        section = section if section is not None else self.section
        extra_filters = {"section": section} if section else None

        logger.debug(
            "Searching | mode=%s | q='%s' | k=%s | owner=%s | doc=%s | filters=%s",
            self.search_mode,
            query,
            k,
            owner_id,
            doc_id,
            extra_filters,
        )

        results = search_fn(
            query,
            top_k=k,
            owner_id=owner_id,
            doc_id=int(doc_id) if doc_id is not None else None,
            extra_filters=extra_filters,
        )

        logger.info("Search returned %d fragments", len(results))
        cleaned = [_clean_paragraph(r["text"]) for r in results]
        logger.debug("Cleaned context: %s", cleaned)
        return cleaned

    def _build_prompt(self, context: List[str], question: str) -> List[Dict[str, str]]:
        """
        Формирует полный chat-prompt с явными секциями CONTEXT, QUESTION, ANSWER.
        Контекст нумеруется как [CTX-n] для точных ссылок.
        """
        numbered_context = "\n".join(
            f"[CTX-{i + 1}] {frag}" for i, frag in enumerate(context)
        )

        user_content = (
            "=====================\n"
            f"CONTEXT:\n{numbered_context}\n"
            "=====================\n"
            f"QUESTION:\n{question}\n"
            "=====================\n"
            "ANSWER:"
        )

        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": "Правила получены и поняты."},
            {"role": "user", "content": user_content},
        ]

    def ask(
        self,
        question: str,
        *,
        stream: bool = False,
        k: int | None = None,
        owner_id: int | None = None,
        doc_id: int | None = None,
        section: str | None = None,
        provider_params: Dict[str, Any] | None = None,
        search_mode: str | None = None,
    ):
        # Допустим временное переопределение режима поиска
        if search_mode is not None and search_mode.lower() != self.search_mode:
            if search_mode.lower() not in self._SEARCH_FUNCS:
                raise ValueError(
                    f"search_mode должен быть 'vector' или 'hybrid', получено: {search_mode}"
                )
            orig_mode, self.search_mode = self.search_mode, search_mode.lower()
        else:
            orig_mode = None

        context = self._retrieve_context(
            question,
            k=k,
            owner_id=owner_id,
            doc_id=doc_id,
            section=section,
        )
        logger.info("context: %s", context)

        messages = self._build_prompt(context, question)
        merged_params = {**self.provider_params, **(provider_params or {})}
        model_name = merged_params.get("model")

        prompt_tokens = _count_chatml_tokens(messages, model_name)
        logger.info("Prompt tokens: %d (model=%s)", prompt_tokens, model_name)

        provider = get_provider()
        if stream:
            logger.debug("Streaming response …")
            if orig_mode:
                self.search_mode = orig_mode
            return provider.chat(messages, stream=True, **merged_params)

        answer = provider.chat(messages, **merged_params)

        try:
            resp_tokens = answer.usage.total_tokens  # type: ignore[attr-defined]
        except Exception:
            resp_tokens = _approx_token_count(str(answer))
        logger.info(
            "Response tokens: %s | Total=%s",
            resp_tokens,
            resp_tokens + prompt_tokens if resp_tokens is not None else "?",
        )

        if orig_mode:
            self.search_mode = orig_mode
        return answer