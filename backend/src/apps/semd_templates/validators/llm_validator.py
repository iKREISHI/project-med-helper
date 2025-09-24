"""
Заглушка для LLM-валидации.

Вместо реального вызова ИИ мы формируем
читаемый JSON с теми полями документа,
которые должны проверяться ИИ
(`validation_strategy` = 'llm' | 'both')
и возвращаем его наверх, чтобы API-эндпоинт
мог отдать этот JSON клиенту.
"""
from __future__ import annotations

import json
from typing import Dict, Any

from apps.semd_templates.models import DocumentInstance
from apps.semd_templates.models.semd_fields import ValidationStrategy


def build_llm_payload(instance: DocumentInstance) -> Dict[str, Any]:
    """
    Собирает словарь:

    {
        "template_slug": "epicrisis",
        "document_id": 42,
        "fields": {
            "anamnesis": "...",
            "diagnosis": "...",
            ...
        }
    }
    """
    payload: Dict[str, Any] = {
        "template_slug": instance.template.slug,
        "document_id": instance.id,
        "fields": {},
    }

    qs = instance.field_values.select_related("field")
    for fv in qs:
        if fv.field.validation_strategy in (
            ValidationStrategy.LLM,
            ValidationStrategy.BOTH,
        ):
            payload["fields"][fv.field.key] = fv.value

    return payload


def validate_with_llm_stub(payload: Dict[str, Any]) -> tuple[list[str], str]:
    """
    «Валидация» LLM: фактически ничего не делает
    и всегда считает данные корректными.

    Возвращает:
        - пустой список ошибок
        - красиво отформатированный JSON,
          который можно показать в API-ответе
    """
    pretty_json: str = json.dumps(payload, ensure_ascii=False, indent=2)
    return [], pretty_json
