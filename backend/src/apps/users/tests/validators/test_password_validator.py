from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.users.validators.password import (
    validate_password,
    validate_password_length,
    validate_password_digits,
    validate_password_uppercase,
    validate_password_lowercase,
)


class PasswordValidatorTests(SimpleTestCase):
    """Тесты валидаторов пароля."""

    def test_validate_password_length(self):
        # меньше 8 символов — ошибка
        with self.assertRaises(DRFValidationError):
            validate_password_length("Abc1e")
        # ровно 8 символов — ок
        validate_password_length("Abcdef1g")

    def test_validate_password_digits(self):
        with self.assertRaises(DRFValidationError):
            validate_password_digits("Abcdefgh")
        validate_password_digits("Abcdefg1")

    def test_validate_password_uppercase(self):
        with self.assertRaises(DRFValidationError):
            validate_password_uppercase("abcdefg1")
        validate_password_uppercase("Abcdefg1")

    def test_validate_password_lowercase(self):
        with self.assertRaises(DRFValidationError):
            validate_password_lowercase("ABCDEFG1")
        validate_password_lowercase("Abcdefg1")

    def test_validate_password_combined(self):
        # Невалидные случаи для комбинированного валидатора
        for value in [
            "Abcdefg",       # нет цифры
            "abcdefg1",      # нет заглавной
            "ABCDEFG1",      # нет строчной
            "A1cdefg",       # длина < 8
        ]:
            with self.subTest(value=value):
                with self.assertRaises(DRFValidationError):
                    validate_password(value)

        # Валидный пароль
        validate_password("Strong1A")
