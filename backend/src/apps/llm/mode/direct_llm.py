"""
direct_llm.py
~~~~~~~~~~~~~
Прямой вызов LLM-провайдера (без retrieval).

* формирует ChatML-сообщения;
* логирует через «django.direct_llm»;
* считает токены (точно при tiktoken, иначе оценочно);
* поддерживает поток (`stream=True`);
* НЕ передаёт provider'у никаких лишних параметров
  (ni `model`, ни `temperature`, ни `max_tokens`).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List

from apps.llm.llm_providers import get_provider

__all__ = ["DirectLLM", "DEFAULT_SYSTEM_PROMPT"]

logger = logging.getLogger("django.direct_llm")

DEFAULT_SYSTEM_PROMPT = (
    "Ты — медицинский ассистент-ИИ для врачей-клиницистов. "
    "Отвечай кратко и по существу, язык — русский."
)

_WS_RE = re.compile(r"\s+")
_JSON_RE = re.compile(r"```json(.*?)```", flags=re.S | re.I)

try:
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover
    tiktoken = None


def _approx_tokens(text: str) -> int:
    return int(len(re.findall(r"\S+", text)) / 0.75)


def _count_tokens(msgs: List[Dict[str, str]], model: str | None) -> int:
    if tiktoken is None or model is None:
        return _approx_tokens(" ".join(m.get("content", "") for m in msgs))
    try:
        enc = tiktoken.encoding_for_model(model)  # type: ignore[arg-type]
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")  # type: ignore[arg-type]

    total = 2  # <im_start>assistant
    for m in msgs:
        total += 4
        total += len(enc.encode(m.get("content", "")))
    return total


def _squeeze(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def _extract_json(text: str) -> str:
    m = _JSON_RE.search(text)
    return m.group(1).strip() if m else text


class DirectLLM:
    """Минималистичный интерфейс прямого обращения к LLM-провайдерам."""

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        extra_params: Dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        self.extra_params = extra_params or {}
        self.provider = get_provider()

        logger.debug("DirectLLM init | model=%s", self.model)

    def ask(
        self,
        question: str,
        *,
        stream: bool = False,
        json_only: bool = False,
        **overrides: Any,
    ):
        msgs = self._build_msgs(question)

        params: Dict[str, Any] = {
            **self.extra_params,
            **overrides,
        }

        # передаём model только если провайдеру он нужен
        if getattr(self.provider, "USE_MODEL_PARAM", True):
            params["model"] = self.model

        prompt_tokens = _count_tokens(msgs, self.model)
        logger.info("Prompt tokens: %d", prompt_tokens)
        logger.debug("Messages: %s", json.dumps(msgs, ensure_ascii=False))

        if stream:
            logger.debug("Streaming …")
            return self.provider.chat(msgs, stream=True, **params)

        answer = self.provider.chat(msgs, **params)

        try:
            resp_tokens = answer.usage.total_tokens  # type: ignore[attr-defined]
        except Exception:
            resp_tokens = _approx_tokens(str(answer))

        logger.info(
            "Response tokens: %s | Total=%s",
            resp_tokens,
            resp_tokens + prompt_tokens if resp_tokens is not None else "?",
        )

        text = str(answer)
        if json_only:
            text = _extract_json(text)
        return _squeeze(text)

    def _build_msgs(self, q: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": "Понял."},
            {"role": "user", "content": q},
        ]
