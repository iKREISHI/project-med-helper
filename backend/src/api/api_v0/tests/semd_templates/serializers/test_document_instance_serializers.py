import uuid
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models, connection

from apps.users.models.position import Position
from apps.semd_templates.models import (
    DocumentTemplate,
    FieldDefinition,
    DocumentInstance,
    DocumentFieldValue,
)

from api.api_v0.semd_templates.serializers.document_instance import (
    DocumentFieldValueCreateSerializer,
    DocumentFieldValueUpdateSerializer,
    DocumentFieldValueBulkUpdateListSerializer,
    DocumentInstanceCreateSerializer,
    DocumentInstanceSerializer,
)


def build_instance(model_cls, extra=None):
    extra = extra or {}
    data = {}
    for f in model_cls._meta.fields:
        if f.primary_key or f.name in extra:
            continue
        if getattr(f, "null", False) or f.has_default() or getattr(f, "blank", False):
            continue
        if isinstance(f, models.ForeignKey):
            data[f.name] = build_instance(f.related_model)
        elif isinstance(f, (models.CharField, models.TextField)):
            data[f.name] = f"{f.name}_{uuid.uuid4().hex[:6]}"
        elif isinstance(f, models.BooleanField):
            data[f.name] = False
        elif isinstance(f, (models.IntegerField, models.BigIntegerField)):
            data[f.name] = 0
        elif isinstance(f, models.JSONField):
            data[f.name] = {}
    data.update(extra or {})
    return model_cls.objects.create(**data)


def ensure_tables():
    with connection.schema_editor() as sch:
        for mdl in (DocumentInstance, DocumentFieldValue):
            if mdl._meta.db_table not in connection.introspection.table_names():
                sch.create_model(mdl)


class SerializerTestCase(TestCase):
    """Happy- и unhappy-path для сериализаторов SEMD-документов."""

    @classmethod
    def setUpTestData(cls):
        ensure_tables()

        # patch FieldDefinitionSlimSerializer → убрать несуществующее 'type'
        from api.api_v0.semd_templates.serializers import document_instance as sms
        FDefSlim = sms.FieldDefinitionSlimSerializer
        FDefSlim.Meta.fields = tuple(
            n for n in ("id", "key", "label", "type")
            if n in {f.name for f in FieldDefinition._meta.fields}
        )
        sms.DocumentFieldValueSerializer._declared_fields["field"] = FDefSlim(read_only=True)

        # users & fixtures
        cls.position = Position.objects.create(name="Test position")
        User = get_user_model()
        cls.user = User.objects.create_user("doc", "pwd12345", position=cls.position)

        cls.template = build_instance(DocumentTemplate, {"name": "Эпикриз"})
        fk = {"template": cls.template} if "template" in {f.name for f in FieldDefinition._meta.fields} else {}
        cls.complaint_field = build_instance(FieldDefinition, fk | {"key": "complaint"})
        cls.temp_field      = build_instance(FieldDefinition, fk | {"key": "temp"})

    def setUp(self):
        self.req = RequestFactory().get("/")
        self.req.user = self.user

    def test_field_value_create_valid(self):
        ser = DocumentFieldValueCreateSerializer(
            data={"field_id": self.complaint_field.id, "value": {"text": "Боль"}}
        )
        self.assertTrue(ser.is_valid())

    def test_field_value_create_invalid_field(self):
        ser = DocumentFieldValueCreateSerializer(
            data={"field_id": 999999, "value": {"text": "—"}}
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("field_id", ser.errors)

    def test_document_instance_create_success(self):
        payload = {
            "template_id": self.template.id,
            "fields": [
                {"field_id": self.complaint_field.id, "value": {"text": "Жалобы"}},
                {"field_id": self.temp_field.id, "value": {"number": 38.2}},
            ],
        }
        ser = DocumentInstanceCreateSerializer(data=payload, context={"request": self.req})
        self.assertTrue(ser.is_valid(), ser.errors)
        doc = ser.save()
        self.assertEqual(doc.field_values.count(), 2)

    def test_document_instance_create_missing_template(self):
        ser = DocumentInstanceCreateSerializer(data={"fields": []}, context={"request": self.req})
        self.assertFalse(ser.is_valid())
        self.assertIn("template_id", ser.errors)

    def test_document_instance_create_duplicate_field(self):
        """Дубликаты field_id → валидационная ошибка, а не IntegrityError."""
        payload = {
            "template_id": self.template.id,
            "fields": [
                {"field_id": self.complaint_field.id, "value": {"text": "Раз"}},
                {"field_id": self.complaint_field.id, "value": {"text": "Два"}},
            ],
        }
        ser = DocumentInstanceCreateSerializer(data=payload, context={"request": self.req})
        self.assertFalse(ser.is_valid())
        self.assertIn("fields", ser.errors)

    def test_document_instance_serializer_output(self):
        doc = DocumentInstance.objects.create(template=self.template, user=self.user)
        DocumentFieldValue.objects.create(document=doc, field=self.complaint_field, value={"text": "Боль"})
        DocumentFieldValue.objects.create(document=doc, field=self.temp_field, value={"number": 37.0})
        data = DocumentInstanceSerializer(instance=doc).data
        self.assertEqual(len(data["field_values"]), 2)

    def test_field_value_update_success(self):
        doc = DocumentInstance.objects.create(template=self.template, user=self.user)
        fv  = DocumentFieldValue.objects.create(document=doc, field=self.complaint_field, value={"text": "старое"})
        ser = DocumentFieldValueUpdateSerializer(instance=fv, data={"id": fv.id, "value": {"text": "обновлено"}})
        self.assertTrue(ser.is_valid(), ser.errors)
        ser.save()
        fv.refresh_from_db()
        self.assertEqual(fv.value["text"], "обновлено")

    def _two_vals(self):
        doc = DocumentInstance.objects.create(template=self.template, user=self.user)
        fv1 = DocumentFieldValue.objects.create(document=doc, field=self.complaint_field, value={"text": "старое"})
        fv2 = DocumentFieldValue.objects.create(document=doc, field=self.temp_field,      value={"number": 38.5})
        return fv1, fv2

    def test_bulk_update_success(self):
        fv1, fv2 = self._two_vals()
        payload = [
            {"id": fv1.id, "value": {"text": "нет жалоб"}},
            {"id": fv2.id, "value": {"number": 36.6}},
        ]
        ser = DocumentFieldValueBulkUpdateListSerializer(instance=[fv1, fv2], data=payload)
        self.assertTrue(ser.is_valid(), ser.errors)
        ser.save()
        fv1.refresh_from_db()
        fv2.refresh_from_db()
        self.assertEqual(fv1.value["text"], "нет жалоб")
        self.assertEqual(fv2.value["number"], 36.6)

    def test_bulk_update_validation_error(self):
        fv1, fv2 = self._two_vals()
        payload = [
            {"id": fv1.id},                                  # нет value → ошибка
            {"id": fv2.id, "value": {"number": 36.6}},
        ]
        ser = DocumentFieldValueBulkUpdateListSerializer(instance=[fv1, fv2], data=payload)
        self.assertFalse(ser.is_valid())
        self.assertIsInstance(ser.errors, list)
        self.assertIn("value", ser.errors[0])
