import os
from gigachat import GigaChat

from config.settings.config import GIGACHAT_API_KEY
from .base import LLMProvider, ChatMessage





class GigaChatProvider(LLMProvider):
    """
    Работает и с обычными, и с потоковыми ответами.
    ─ stream управляется аргументом метода .chat()
    ─ список messages преобразуется в строку-диалог (SDK пока принимает именно строку)
    """

    def __init__(self, model: str = "GigaChat", **cfg):
        super().__init__(model, **cfg)
        self.credentials = GIGACHAT_API_KEY

    # ---------- утилита для конвертации сообщений ----------
    @staticmethod
    def _to_prompt(messages: list[ChatMessage]) -> str:
        """
        Преобразуем [{'role':'user','content':'Привет'} ...] → строку
        в стиле:
            user: Привет
            assistant: ...
        """
        role_map = {"system": "system", "user": "user", "assistant": "assistant"}
        return "\n".join(f"{role_map[m['role']]}: {m['content']}" for m in messages)

    # ---------- основной вызов ----------
    def _request(self, messages: list[ChatMessage], *, stream: bool, **params):
        prompt = self._to_prompt(messages)
        print(self.credentials)
        # модель передаётся в конструктор клиента, stream — в метод chat()
        with GigaChat(
            credentials=self.credentials,
            scope="GIGACHAT_API_PERS",
            model=self.model,
            verify_ssl_certs=False,      # ставьте True при установленном корне Минцифры
        ) as giga:

            if stream:
                for chunk in giga.chat(prompt, stream=True, **params):
                    delta = chunk.choices[0].delta.get("content", "")
                    if delta:
                        yield delta
            else:
                resp = giga.chat(prompt, **params)
                yield resp.choices[0].message.content