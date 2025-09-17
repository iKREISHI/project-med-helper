import os
from openai import OpenAI
from .base import LLMProvider, ChatMessage


class LMStudioProvider(LLMProvider):
    """
    Работает с локальным сервером LM Studio (режим *OpenAI-совместимого API*).

    Перед запуском включите сервер:
        $ lms server start              # или «Developer → Run as server» в GUI

    Переменные окружения:
        LM_STUDIO_BASE_URL   – URL вида http://localhost:1234/v1   (по умолчанию)
        LM_STUDIO_API_KEY    – любое значение, по умолчанию «lm-studio»
        LM_STUDIO_MODEL      – идентификатор модели, загруженной в LM Studio
    """

    def __init__(self,
                 model: str | None = None,
                 **cfg):
        super().__init__(model or os.getenv("LM_STUDIO_MODEL", "lmstudio-community/qwen3-4b-instruct-2507-mlx"),
                         **cfg)

        self.client = OpenAI(
            base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key=os.getenv("LM_STUDIO_API_KEY", "lm-studio"),
        )

    def _request(self,
                 messages: list[ChatMessage],
                 *,
                 stream: bool,
                 **params):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            **params,
        )

        if stream:
            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        else:
            yield response.choices[0].message.content
