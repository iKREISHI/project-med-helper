from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.users.validators.username import (
    validate_username,
    validate_username_exists,
    validate_username_unique,
    validate_username_length,
    validate_username_symbols,
)


User = get_user_model()


from apps.users.models.position import Position


class UsernameValidatorTests(TestCase):
    """Тесты валидаторов имени пользователя."""

    def setUp(self):
        # Создаём должность, требуемую для создания пользователя
        self.position = Position.objects.create(name="Тестовая должность")

    def test_validate_username_length(self):
        with self.assertRaises(DRFValidationError):
            validate_username_length("abc")
        validate_username_length("abcdef")

    def test_validate_username_symbols(self):
        # кириллица и пробелы недопустимы
        for value in ["иван", "user name", "john-doe", "name!", "наme"]:
            with self.subTest(value=value):
                with self.assertRaises(DRFValidationError):
                    validate_username_symbols(value)
        # допустимы латиница, цифры и подчёркивание
        for value in ["user_1", "JohnDoe", "john123", "USER_name_99"]:
            with self.subTest(value=value):
                validate_username_symbols(value)

    def test_validate_username_unique(self):
        User.objects.create_user(username="existing_user", password="Strong1A", position=self.position)
        with self.assertRaises(DRFValidationError):
            validate_username_unique("existing_user")
        # другое имя — проходит
        validate_username_unique("new_user")

    def test_validate_username_exists(self):
        # когда пользователя нет — ошибка
        with self.assertRaises(DRFValidationError):
            validate_username_exists("ghost")
        # создаём и проверяем, что теперь валидатор проходит
        User.objects.create_user(username="ghost", password="Strong1A", position=self.position)
        validate_username_exists("ghost")

    def test_validate_username_combined(self):
        # комбинированный валидатор должен последовательно проверять длину, символы и уникальность
        # 1) длина < 6
        with self.assertRaises(DRFValidationError):
            validate_username("u_1")
        # 2) запрещённые символы
        with self.assertRaises(DRFValidationError):
            validate_username("bad-name")
        # 3) имя уже занято
        User.objects.create_user(username="taken_1", password="Strong1A", position=self.position)
        with self.assertRaises(DRFValidationError):
            validate_username("taken_1")
        # 4) корректное новое имя проходит
        validate_username("new_user_1")
