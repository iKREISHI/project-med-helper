from __future__ import annotations

import abc, os
from typing import Iterable, Iterator, List, Dict, Any

# {"role": "user" | "assistant" | "system", "content": "..."}
ChatMessage = Dict[str, str]


class LLMProvider(abc.ABC):
    """
    Базовый контракт — всё приложение видит только .chat().
    Наследники реализуют _request(), опираясь на «родные» SDK.
    """

    def __init__(
        self,
        model: str,
        *,
        system_prompt: str | None = None,
        user_prompt_tpl: str | None = None,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt_tpl = user_prompt_tpl

    def chat(
        self,
        messages: List[ChatMessage] | str,
        *,
        stream: bool = False,
        **params: Any,
    ) -> str | Iterable[str]:
        """
        messages — либо уже готовый список сообщений, либо просто строка от пользователя
        stream=False → вернёт строку
        stream=True  → генератор токенов
        """
        if isinstance(messages, str):
            # Шаблон user_prompt_tpl, если задан
            text = (
                self.user_prompt_tpl.format(q=messages)
                if self.user_prompt_tpl
                else messages
            )
            messages = [{"role": "user", "content": text}]

        # Инъекция системного промпта
        if self.system_prompt:
            messages = [{"role": "system", "content": self.system_prompt}] + messages

        if stream:
            return self._request(messages, stream=True, **params)
        else:
            return "".join(self._request(messages, stream=False, **params))

    @abc.abstractmethod
    def _request(
        self,
        messages: List[ChatMessage],
        *,
        stream: bool,
        **params: Any,
    ) -> Iterator[str]:
        """
        Низкоуровневое обращение к SDK; обязана yield-ить токены, если stream=True
        """
        raise NotImplementedError
