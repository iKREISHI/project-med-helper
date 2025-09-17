from __future__ import annotations

import re
from typing import Any, Dict, List, Callable

from apps.docs_ingest.vectors import vector_search, hybrid_search
from apps.llm.llm_providers import get_provider

__all__ = ["ClinicalLLM"]


_BULLET_RE = re.compile(r"^[\u2022•\-–]\s*", flags=re.MULTILINE)
_WS_RE: re.Pattern[str] = re.compile(r"\s+")


def _clean_paragraph(text: str) -> str:
    """
    Убирает маркёры списков и лишние переводы строк внутри абзацев.

    Args:
        text: сырой фрагмент из поиска.

    Returns:
        Очищенный фрагмент.
    """
    text = _BULLET_RE.sub("", text)

    paragraphs: list[str] = []
    for block in text.split("\n\n"):
        block = block.replace("\n", " ")
        block = _WS_RE.sub(" ", block).strip()
        if block:
            paragraphs.append(block)

    return "\n\n".join(paragraphs)


class ClinicalLLM:
    """
    Удобная обёртка над провайдером LLM + поиском фрагментов по документам.

    Параметры инициализации
    -----------------------
    search_mode : str
        «vector» (по умолчанию) или «hybrid» — какую функцию поиска использовать.
    k : int
        Сколько фрагментов вставлять в CONTEXT.
    owner_id : int | None
        Фильтр по владельцу документа.
    doc_id : int | None
        Фильтр по ID документа.
    section : str | None
        Фильтр по секции/главе документа.
    provider_params : dict | None
        Параметры, которые всегда будут проксированы в provider.chat(**params).
    """

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

    def _retrieve_context(
        self,
        query: str,
        *,
        k: int | None = None,
        owner_id: int | None = None,
        doc_id: int | None = None,
        section: str | None = None,
    ) -> List[str]:
        """
        Выполняет поиск (vector/hybrid) и очищает результаты.
        """
        search_fn = self._SEARCH_FUNCS[self.search_mode]

        # Приоритет: аргументы метода > атрибуты экземпляра
        k = k if k is not None else self.k
        owner_id = owner_id if owner_id is not None else self.owner_id
        doc_id = doc_id if doc_id is not None else self.doc_id
        section = section if section is not None else self.section

        extra_filters: Dict[str, Any] | None = None
        if section:
            extra_filters = {"section": section}

        results = search_fn(
            query,
            top_k=k,
            owner_id=owner_id,
            doc_id=int(doc_id) if doc_id is not None else None,
            extra_filters=extra_filters,
        )

        cleaned = [_clean_paragraph(r["text"]) for r in results]
        return cleaned

    @staticmethod
    def _build_prompt(context: List[str], question: str) -> List[Dict[str, str]]:
        """
        Формирует messages для provider.chat.
        """
        numbered_context = "\n".join(
            f"[{idx + 1}] {fragment}" for idx, fragment in enumerate(context)
        )

        system_prompt = (
            "Ты — справочная LLM-система для врачей-клиницистов.\n"
            "Правила работы:\n\n"
            "1. Отвечай **только** на основании текста из секции CONTEXT.\n"
            "2. Если факта нет в CONTEXT — честно ответь:\n"
            "   «✘ По предоставленным клиническим рекомендациям данных нет».\n"
            "   (ничего не придумывай!)\n"
            "3. Сохраняй нумерованные ссылки: после каждого утверждения ставь квадратные скобки "
            "с индексом фрагмента, например [1] или [2].\n"
            "   Нумерация соответствует порядку появления фрагментов в CONTEXT.\n"
            "4. Стиль ответа: кратко, по существу, 1-2 абзаца, затем «Рекомендации» списком, если уместно.\n"
            "5. Язык ответа — русский, медицинская терминология допускается."
        )

        context_block = f"<CONTEXT>\n{numbered_context}\n</CONTEXT>"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "Понял правила."},
            {"role": "user", "content": f"{context_block}\n\n<user>{question}</user>"},
        ]
        return messages

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
        """
        Получить ответ LLM с возможностью переопределить настройки на вызов.

        Args:
            question: вопрос врача.
            stream: если True — вернуть генератор токенов.
            k/owner_id/doc_id/section: переопределяют соответствующие настройки экземпляра.
            provider_params: дополнительные параметры, проксируются в provider.chat.
            search_mode: временно переопределяет search_mode экземпляра.

        Returns:
            str | Generator[str, None, None]
        """
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

        # Итоговые параметры провайдера: экземплярные + вызова
        merged_params = {**self.provider_params, **(provider_params or {})}

        provider = get_provider()

        if stream:
            return provider.chat(messages, stream=True, **merged_params)

        return provider.chat(messages, **merged_params)


# if __name__ == "__main__":
#     llm = ClinicalLLM(search_mode="hybrid", k=3)
#     response = llm.ask("Какова доза статинов при высоком риске ИБС?")
#     print(response)
