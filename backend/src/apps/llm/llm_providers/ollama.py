import os

import ollama
from .base import LLMProvider, ChatMessage


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3", host: str | None = None, **cfg):
        super().__init__(model, **cfg)
        self.host = os.getenv("LOCAL_LLM_API")  # например "http://localhost:11434"

    def _request(self, messages, *, stream: bool, **params):
        if stream:
            for chunk in ollama.chat(
                model=self.model,
                messages=messages,
                stream=True,
                host=self.host,
                **params,
            ):
                yield chunk["message"]["content"]
        else:
            resp = ollama.chat(
                model=self.model,
                messages=messages,
                stream=False,
                host=self.host,
                **params,
            )
            yield resp["message"]["content"]
