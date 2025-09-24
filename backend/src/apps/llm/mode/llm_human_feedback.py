"""
llm_human_feedback.py
~~~~~~~~~~~~~~~~~~~~~
Формирует «человеческие» рекомендации к DocumentInstance.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from django.conf import settings
from apps.llm.mode.direct_llm import DirectLLM
from apps.semd_templates.models import DocumentInstance

logger = logging.getLogger("django.llm_human_feedback")


_LLM = DirectLLM(
    model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
    system_prompt=(
        "Ты — опытный клинический аудитор медицинских документов.\n"
        "Сначала перечисли ошибки (раздел «Ошибки»), затем возможные улучшения "
        "(раздел «Можно улучшить»). Если ошибок нет — напиши «Ошибок не найдено»."
    ),
)

def generate_feedback(instance: DocumentInstance) -> str:
    """Возвращает текст рекомендаций по документу."""
    payload: Dict[str, Any] = {
        "template_slug": instance.template.slug,
        "document_id": instance.id,
        "fields": {
            fv.field.key: fv.value
            for fv in instance.field_values.select_related("field")
        },
    }

    prompt = (
        "Проанализируй медицинский документ и дай рекомендации:\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
    logger.debug("LLM feedback prompt for doc %s", instance.id)
    return _LLM.ask(prompt)
