"""
chat.services
~~~~~~~~~~~~~

Сервис-слой между REST/WebSocket-контроллерами и `ClinicalLLM`.

Задачи модуля
-------------
1. **Создать / найти** `ChatSession` для пользователя.
2. **Записать** входящие сообщения пользователя в БД.
3. **Вызвать** `ClinicalLLM` (одним ответом или токен-стримом).
4. **Сохранить** ответ LLM в таблицу `ChatMessage`.
5. При потоковой выдаче — обернуть генератор токенов в `StreamingHttpResponse`
   с контент-тайпом `text/event-stream` (SSE).

Все операции записи выполняются внутри одной транзакции, поэтому история
диалога всегда консистентна, даже если LLM упадёт с ошибкой.
"""

from typing import Generator, List, Tuple

from django.db import transaction
from django.http import StreamingHttpResponse

from apps.llm.mode.clinical_reference_llm import ClinicalLLM
from apps.chat.models import ChatSession, ChatMessage


SYSTEM_PROMPT = (
    "Ты — справочная LLM-система для врачей-клиницистов.\n\n"
    "ПРАВИЛА РАБОТЫ\n"
    "1. Отвечай только на основании текста из секции CONTEXT. Не добавляй информацию из иных источников.\n"
    "2. Если нужного факта нет в CONTEXT, ответь ровно фразой:\n"
    "   «✘ По предоставленным клиническим рекомендациям данных нет».\n"
    "3. После каждого утверждения указывай квадратные скобки с индексом фрагмента CONTEXT, например [CTX-2].\n"
    "4. Формат ответа:\n"
    "   • **Резюме** — 1–2 предложения (≤120 слов).\n"
    "   • **Подробности** — до 3 абзацев (≤300 слов) с расшифровкой первой аббревиатуры в скобках.\n"
    "   • **Рекомендации** — маркированный список, указывай дозы в мг и мг/кг при необходимости.\n"
    "   • **Уровень доказательности** — укажи «Класс I/IIa/IIb/III; Уровень A/B/C», если есть данные.\n"
    "   • ❗ **Противопоказания/красные флажки** — отдельным пунктом, если присутствуют.\n"
    "   • **Ссылки** — список использованных индексов CONTEXT.\n"
    "5. Язык ответа — русский.\n"
    "6. Ответ предназначен только для квалифицированного медицинского персонала и не является окончательным клиническим решением."
)

def _llm_factory(params: dict | None = None, **search_kwargs) -> ClinicalLLM:
    """
    Фабрика `ClinicalLLM`, проксирующая **provider_params** и параметры поиска.

    Parameters
    ----------
    params : dict | None
        Содержимое поля `params` из REST-запроса; пробрасывается в LLM-провайдер.
    **search_kwargs :
        Аргументы `search_mode`, `k`, `doc_id`, `section` и т.д.

    Returns
    -------
    ClinicalLLM
    """
    return ClinicalLLM(search_mode='hybrid', system_prompt=SYSTEM_PROMPT, k=10)


def _get_or_create_session(user, session_id: int | None) -> ChatSession:
    """
    Возвращает существующий `ChatSession` пользователя либо создаёт новый.

    • Если `session_id` указан, но не принадлежит пользователю, игнорируется —
      создаётся новый сеанс (это важнее, чем 404, чтобы клиент не «сломал»
      работу своей ошибкой).
    """
    if session_id:
        try:
            return ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            pass
    return ChatSession.objects.create(user=user)


@transaction.atomic
def ask_llm_and_save_once(
    *,
    user,
    messages: List[dict],
    session_id: int | None,
    llm_kwargs: dict,
) -> Tuple[ChatSession, ChatMessage]:
    """
    Одноразовый запрос к LLM (без стрима).

    1. Создаёт/находит диалог.
    2. Записывает **все** входящие `messages` (user/assistant/system) в БД.
    3. Берёт последний `role="user"` как question, вызывает LLM.
    4. Сохраняет ответ (`role="assistant"`).
    5. Возвращает `(session, answer_message)` для контроллера.

    Параметры
    ---------
    user : django.contrib.auth.models.User
        Текущий пользователь.
    messages : list[dict]
        История сообщений из HTTP-запроса (должна содержать хотя бы один
        `{"role": "user", "content": "…"}`).
    session_id : int | None
        Если передан — попытка продолжить существующий диалог.
    llm_kwargs : dict
        Аргументы для `ClinicalLLM`, например
        `{"search_mode": "vector", "k": 5, "provider_params": {...}}`.

    Returns
    -------
    (ChatSession, ChatMessage)
        Объект сеанса и сохранённое сообщение-ответ LLM.
    """
    session = _get_or_create_session(user, session_id)

    # сохраним историю запроса
    for msg in messages:
        ChatMessage.objects.create(session=session, role=msg["role"], content=msg["content"])

    # берём последний вопрос пользователя
    question = next(m["content"] for m in reversed(messages) if m["role"] == "user")

    # вызываем LLM
    llm = _llm_factory(params=llm_kwargs.pop("provider_params", None), **llm_kwargs)
    answer = llm.ask(question, k=10, search_mode='hybrid')

    # сохраняем ответ
    answer_msg = ChatMessage.objects.create(
        session=session, role=ChatMessage.ROLE_ASSISTANT, content=str(answer)
    )

    # заполним заголовок диалога первым вопросом
    if not session.title:
        session.title = question[:100]
        session.save(update_fields=["title"])

    return session, answer_msg


def sse_stream_and_save(
    *,
    user,
    messages: List[dict],
    session_id: int | None,
    llm_kwargs: dict,
) -> StreamingHttpResponse:
    """
    Потоковая версия: оборачивает генератор токенов в SSE-ответ.

    Алгоритм почти тот же, что у `ask_llm_and_save_once`, но:

    • вместо возврата строки генерирует SSE-байты `data: <token>\\n\\n`;
    • в конце отправляет событие `event: end`;
    • после окончания стрима пишет в БД полный ответ.

    Возвращает
    ----------
    StreamingHttpResponse
        Готовый HTTP-ответ с `content-type: text/event-stream`.
    """
    session = _get_or_create_session(user, session_id)

    # фиксируем входящие сообщения
    for msg in messages:
        ChatMessage.objects.create(session=session, role=msg["role"], content=msg["content"])

    question = next(m["content"] for m in reversed(messages) if m["role"] == "user")
    llm = _llm_factory(params=llm_kwargs.pop("provider_params", None), **llm_kwargs)

    def _iter() -> Generator[bytes, None, None]:
        buffer: List[str] = []
        for token in llm.ask(question, stream=True):
            t = str(token)
            buffer.append(t)
            yield f"data: {t}\n\n".encode()
        # сигнал о завершении
        yield b"event: end\ndata: [END]\n\n"
        # сохраняем накопленный ответ
        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.ROLE_ASSISTANT,
            content="".join(buffer),
        )

    return StreamingHttpResponse(
        _iter(),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )