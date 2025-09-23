from django.core.exceptions import ValidationError
from decimal import Decimal
import re


def not_empty(value):
    if value in (None, "", [], {}, ()):
        raise ValidationError("Значение не должно быть пустым.")


def max_length(value, length):
    if len(str(value)) > int(length):
        raise ValidationError(f"Длина значения превышает {length} символов.")


def min_length(value, length):
    if len(str(value)) < int(length):
        raise ValidationError(f"Длина значения меньше {length} символов.")


def max_value(value, bound):
    if Decimal(str(value)) > Decimal(str(bound)):
        raise ValidationError(f"Значение должно быть ≤ {bound}.")


def min_value(value, bound):
    if Decimal(str(value)) < Decimal(str(bound)):
        raise ValidationError(f"Значение должно быть ≥ {bound}.")


def regex(value, pattern):
    if not re.match(pattern, str(value)):
        raise ValidationError(
            f"Значение не соответствует регулярному выражению {pattern!r}."
        )


SERVER_VALIDATOR_MAP = {
    "not_empty": lambda v, p=None: not_empty(v),
    "max_length": max_length,
    "min_length": min_length,
    "max_value": max_value,
    "min_value": min_value,
    "regex": regex,
}


def run_server_validators(value, validators_spec):
    """
    validators_spec: list[str], например ['not_empty', 'max_length:100']
    Возвращает list[str] — сообщения об ошибках.
    """
    errors = []

    for rule in validators_spec:
        if ":" in rule:
            name, param = rule.split(":", 1)
        else:
            name, param = rule, None

        func = SERVER_VALIDATOR_MAP.get(name)
        if func is None:  # неизвестное правило — пропускаем
            continue

        try:
            if param is None:
                func(value, None)
            else:
                func(value, param)
        except ValidationError as exc:
            errors.append(str(exc))

    return errors
