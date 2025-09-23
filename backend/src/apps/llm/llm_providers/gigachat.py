from __future__ import annotations
import os, logging
from typing import List
from gigachat import GigaChat
from config.settings.config import GIGACHAT_API_KEY
from .base import LLMProvider, ChatMessage



class GigaChatProvider(LLMProvider):
    _TIMEOUT: float = 30.0

    def __init__(self, model: str = "GigaChat", **cfg):
        super().__init__(model, **cfg)
        self.credentials = GIGACHAT_API_KEY
        self.verify_ssl_certs = cfg.get("verify_ssl_certs", False)

    @staticmethod
    def _to_prompt(msgs: List[ChatMessage]) -> str:
        role = {"system": "system", "user": "user", "assistant": "assistant"}
        return "\n".join(f"{role[m['role']]}: {m['content']}" for m in msgs)

    def _request(self, messages: List[ChatMessage], *, stream: bool, **params):
        prompt = self._to_prompt(messages)
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
