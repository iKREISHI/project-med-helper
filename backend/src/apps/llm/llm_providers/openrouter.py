import os
from openai import OpenAI

from config.settings.config import OPENROUTER_API_KEY
from .base import LLMProvider, ChatMessage


class OpenRouterProvider(LLMProvider):
    """
    Универсальная обёртка над OpenAI-SDK, настроенная на https://openrouter.ai.
    • Поддерживает обычный и потоковый режим.
    • Дополнительные заголовки (Referer / X-Title) можно задать через ENV.
    """

    _BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, model: str = "deepseek/deepseek-chat-v3.1:free", **cfg):
        super().__init__(model, **cfg)

        # ключ обязательно лежит в переменной окружения
        api_key = OPENROUTER_API_KEY
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

        self.client = OpenAI(base_url=self._BASE_URL, api_key=api_key)

        # заголовки рейтинга (можно опустить)
        self._extra_headers = {
            "HTTP-Referer": os.getenv("OPENROUTER_REFERER", ""),
            "X-Title": os.getenv("OPENROUTER_TITLE", ""),
        }

    def _request(self, messages: list[ChatMessage], *, stream: bool, **params):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            extra_headers={k: v for k, v in self._extra_headers.items() if v},
            extra_body={},
            **params,
        )

        if stream:
            # response — генератор Chunk-объектов
            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        else:
            yield response.choices[0].message.content
