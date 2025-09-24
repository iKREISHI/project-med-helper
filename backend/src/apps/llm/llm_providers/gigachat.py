"""
gigachat.py
~~~~~~~~~~~
Адаптер GigaChat под интерфейс LLMProvider.
"""
from __future__ import annotations

import logging
from typing import List

from gigachat import GigaChat
from django.conf import settings
from .base import LLMProvider, ChatMessage

logger = logging.getLogger("django.gigachat_provider")


class GigaChatProvider(LLMProvider):
    """
    GigaChat SDK не принимает параметр `model` в chat(),
    поэтому помечаем это флагом USE_MODEL_PARAM = False.
    """
    _TIMEOUT = 30.0
    USE_MODEL_PARAM = False   # ← ключевая строка

    def __init__(self, model: str = "GigaChat", **cfg):
        super().__init__(model, **cfg)
        self.credentials = settings.GIGACHAT_API_KEY
        self.verify_ssl_certs = cfg.get("verify_ssl_certs", False)

    # internal helpers
    @staticmethod
    def _to_prompt(msgs: List[ChatMessage]) -> str:
        role = {"system": "system", "user": "user", "assistant": "assistant"}
        return "\n".join(f"{role[m['role']]}: {m['content']}" for m in msgs)

    def _request(self, prompt: str, *, stream: bool, **params):
        with GigaChat(
            credentials=self.credentials,
            scope="GIGACHAT_API_PERS",
            model=self.model,
            timeout=self._TIMEOUT,
            verify_ssl_certs=self.verify_ssl_certs,
        ) as giga:
            if stream:
                for chunk in giga.chat(prompt, stream=True, **params):
                    delta = chunk.choices[0].delta.get("content", "")
                    if delta:
                        yield delta
            else:
                resp = giga.chat(prompt, **params)
                yield resp.choices[0].message.content

    # public method required by DirectLLM
    def chat(self, messages: List[ChatMessage], *, stream: bool = False, **params):
        prompt = self._to_prompt(messages)
        # убеждаемся, что лишний ключ 'model' точно удалён
        params.pop("model", None)
        if stream:
            return self._request(prompt, stream=True, **params)
        return "".join(self._request(prompt, stream=False, **params))
