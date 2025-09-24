from __future__ import annotations

from typing import Any, Dict, List, Tuple

from apps.semd_templates.validators import run_server_validators
from apps.semd_templates.models import DocumentInstance
from apps.llm.mode.llm_human_feedback import generate_feedback
from apps.semd_templates.models.semd_fields import ValidationStrategy


def validate_document_instance(
    instance: DocumentInstance,
) -> Tuple[bool, Dict[str, Dict[str, Any]], str]:
    """
    Полная проверка документа.

    :return: (is_valid, details, feedback_text)
    """
    overall_valid: bool = True
    details: Dict[str, Dict[str, Any]] = {}

    # --- проверяем каждый FieldValue серверными валидаторами ---
    qs = instance.field_values.select_related("field")
    for fv in qs:
        strategy = fv.field.validation_strategy
        server_errors: List[str] = []
        llm_errors: List[str] = []

        if strategy in (ValidationStrategy.SERVER, ValidationStrategy.BOTH):
            server_errors = run_server_validators(
                fv.value,
                fv.field.server_validators,
            )

        # Мы больше НЕ требуем структурного JSON от LLM, так что llm_errors
        # остаётся пустым или заполняется будущей логикой, если понадобится.
        field_valid = not server_errors and not llm_errors
        if not field_valid:
            overall_valid = False

        details[fv.field.key] = {
            "server_errors": server_errors,
            "llm_errors": llm_errors,
            "status": "valid" if field_valid else "invalid",
        }

    # --- получаем человеко-читаемые рекомендации ---
    feedback_text: str = generate_feedback(instance)

    return overall_valid, details, feedback_text
