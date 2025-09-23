from __future__ import annotations

from typing import Dict, Any, List, Tuple

from apps.semd_templates.validators import run_server_validators
from apps.semd_templates.models import DocumentInstance
from apps.semd_templates.validators.llm_validator import (
    build_llm_payload,
    validate_with_llm_stub,
)
from apps.semd_templates.models.semd_fields import ValidationStrategy


def validate_document_instance(
    instance: DocumentInstance,
) -> Tuple[bool, Dict[str, Dict[str, Any]], str]:
    """
    Полная проверка документа.

    :return: (is_valid, details, llm_payload_json)
        is_valid            — bool
        details             — {field_key: {...}}
        llm_payload_json    — str (pretty JSON) либо "" если нет полей для LLM
    """
    overall_valid: bool = True
    details: Dict[str, Dict[str, Any]] = {}

    # ——— Сначала подготовим payload для LLM ———
    llm_payload: Dict[str, Any] = build_llm_payload(instance)
    llm_errors_global, llm_payload_json = validate_with_llm_stub(llm_payload)

    # ——— Затем проходим по каждому полю ———
    qs = instance.field_values.select_related("field")
    for fv in qs:
        strategy = fv.field.validation_strategy
        server_errors: List[str] = []
        llm_errors: List[str] = []

        # серверная часть
        if strategy in (ValidationStrategy.SERVER, ValidationStrategy.BOTH):
            server_errors = run_server_validators(
                fv.value, fv.field.server_validators
            )

        # llm-часть (заглушка уже отработала выше)
        if strategy in (ValidationStrategy.LLM, ValidationStrategy.BOTH):
            llm_errors = []  # всегда пусто в заглушке

        field_valid = not server_errors and not llm_errors
        if not field_valid:
            overall_valid = False

        details[fv.field.key] = {
            "server_errors": server_errors,
            "llm_errors": llm_errors,
            "status": "valid" if field_valid else "invalid",
        }

    # если в документе нет полей для LLM, вернём пустую строку,
    # чтобы ответ был компактнее
    if not llm_payload["fields"]:
        llm_payload_json = ""

    return overall_valid, details, llm_payload_json
