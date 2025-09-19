"""
clinical_llm.py
~~~~~~~~~~~~~~~~

Обёртка над поисковым слоем (`vector_search` / `hybrid_search`) и провайдером LLM,
которая

* ищет релевантные фрагменты;
* очищает их перед передачей в модель;
* формирует промпт согласно клиническим правилам;
* **логирует** все этапы через *Django‑совместимый* логгер;
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
from clinical_llm import ClinicalLLM

llm = ClinicalLLM(
    search_mode="hybrid",
    k=3,
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

__all__ = ["ClinicalLLM"]

logger = logging.getLogger("django.clinical_llm")

_BULLET_RE = re.compile(r"^[\u2022•\-–]\s*", flags=re.MULTILINE)
_WS_RE: re.Pattern[str] = re.compile(r"\s+")

try:
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover
    tiktoken = None  # noqa: PLW0127 – fallback at runtime


def _clean_paragraph(text: str) -> str:
    """Удаляет маркёры списков и перевод строки внутри абзаца."""
    text = _BULLET_RE.sub("", text)

    paragraphs: list[str] = []
    for block in text.split("\n\n"):
        block = block.replace("\n", " ")
        block = _WS_RE.sub(" ", block).strip()
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
        tokens += 4  # ChatML overhead per message
        tokens += len(encoding.encode(m.get("content", "")))
    return tokens


class ClinicalLLM:
    _SEARCH_FUNCS: dict[str, Callable[..., List[Dict[str, Any]]]] = {
        "vector": vector_search,
        "hybrid": hybrid_search,
    }

    def __init__(
        self,
        *,
        search_mode: str = "vector",
        k: int = 5,
        owner_id: int | None = None,
        doc_id: int | None = None,
        section: str | None = None,
        provider_params: Dict[str, Any] | None = None,
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

        logger.debug("ClinicalLLM initialised | mode=%s, k=%s", self.search_mode, self.k)

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

        extra_filters: Dict[str, Any] | None = {"section": section} if section else None

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

    @staticmethod
    def _build_prompt(context: List[str], question: str) -> List[Dict[str, str]]:
        numbered_context = "\n".join(
            f"[{i + 1}] {frag}" for i, frag in enumerate(context)
        )

        system_prompt = (
            "Ты — справочная LLM-система для врачей-клиницистов.\n"
            "Правила работы:\n\n"
            "1. Отвечай **только** на основании текста из секции CONTEXT.\n"
            "2. Если факта нет в CONTEXT — честно ответь:\n"
            "   «✘ По предоставленным клиническим рекомендациям данных нет».\n"
            "3. Сохраняй нумерованные ссылки: после каждого утверждения ставь квадратные скобки с индексом "
            "фрагмента, например [1] или [2].\n"
            "4. Стиль ответа: кратко, по существу, 1-2 абзаца, затем «Рекомендации» списком.\n"
            "5. Язык ответа — русский."
        )

        context_block = f"<CONTEXT>\n{numbered_context}\n</CONTEXT>"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "Понял правила."},
            {"role": "user", "content": f"{context_block}\n\n<user>{question}</user>"},
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
        if search_mode is not None:
            orig_mode = self.search_mode
            try:
                self.search_mode = search_mode.lower()
                if self.search_mode not in self._SEARCH_FUNCS:
                    raise ValueError
            except ValueError:
                self.search_mode = orig_mode
                raise ValueError(
                    f"search_mode должен быть 'vector' или 'hybrid', получено: {search_mode}"
                )

        context = self._retrieve_context(
            question,
            k=k,
            owner_id=owner_id,
            doc_id=doc_id,
            section=section,
        )

        messages = self._build_prompt(context, question)
        merged_params = {**self.provider_params, **(provider_params or {})}
        model_name = merged_params.get("model")

        prompt_tokens = _count_chatml_tokens(messages, model_name)
        logger.info("Prompt tokens: %d (model=%s)", prompt_tokens, model_name)

        provider = get_provider()
        if stream:
            logger.debug("Streaming response …")
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

        return answer