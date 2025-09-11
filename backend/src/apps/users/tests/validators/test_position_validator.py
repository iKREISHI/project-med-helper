from django.test import SimpleTestCase
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.users.validators.position import (
    validate_position_name,
    validate_position_short_name,
)
from apps.users.models.position import Position


class PositionNameValidatorTests(SimpleTestCase):
    def test_name_required_raises_on_none(self):
        with self.assertRaises(DjangoValidationError):
            validate_position_name(None)

    def test_name_required_raises_on_empty(self):
        for value in ["", "   "]:
            with self.subTest(value=value):
                with self.assertRaises(DjangoValidationError):
                    validate_position_name(value)

    def test_name_min_length_after_strip(self):
        for value in ["ab", " a "]:
            with self.subTest(value=value):
                with self.assertRaises(DjangoValidationError):
                    validate_position_name(value)

        for value in ["abc", "  abc  ", "должность"]:
            with self.subTest(value=value):
                validate_position_name(value)


class PositionShortNameValidatorTests(SimpleTestCase):
    def test_short_name_optional_accepts_none_and_empty(self):
        validate_position_short_name(None)
        validate_position_short_name("")
        with self.assertRaises(DjangoValidationError):
            validate_position_short_name("   ")

    def test_short_name_min_length_after_strip(self):
        with self.assertRaises(DjangoValidationError):
            validate_position_short_name(" a ")
        validate_position_short_name("ab")
        validate_position_short_name(" ab ")
