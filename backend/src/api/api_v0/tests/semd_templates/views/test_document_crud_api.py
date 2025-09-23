"""
Интеграционные тесты CRUD-эндпоинтов документов и их полей
(позитивные + негативные сценарии).
"""

from __future__ import annotations
import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models, connection
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.position import Position
from apps.semd_templates.models import (
    DocumentTemplate,
    FieldDefinition,
    DocumentInstance,
    DocumentFieldValue,
)

# -------------------- реальные URL-ы ---------------------
BASE_URL = "/api/v0/semd-documents/"                 # CRUD документов
def FIELDS_URL(doc_id: int) -> str:                  # вложенные поля
    return f"/api/v0/semd-documents/{doc_id}/fields/"


# -------------------- helpers ----------------------------
def create_minimal(mdl: type[models.Model], extra: dict[str, Any] | None = None):
    """
    Создаёт «минимально валидный» объект любой модели:
    все not-null/без default поля заполняются простыми значениями.
    """
    extra = extra or {}
    data: dict[str, Any] = {}

    for f in mdl._meta.fields:
        if f.primary_key or f.name in extra:
            continue
        if getattr(f, "null", False) or f.has_default() or getattr(f, "blank", False):
            continue
        if isinstance(f, models.ForeignKey):
            data[f.name] = create_minimal(f.related_model)
        elif isinstance(f, (models.CharField, models.TextField)):
            data[f.name] = f"{f.name}_{uuid.uuid4().hex[:6]}"
        elif isinstance(f, models.BooleanField):
            data[f.name] = False
        elif isinstance(f, (models.IntegerField, models.BigIntegerField)):
            data[f.name] = 0
        elif isinstance(f, models.JSONField):
            data[f.name] = {}
    data.update(extra)
    return mdl.objects.create(**data)


def ensure_tables():
    """Создаём таблицы DocumentInstance / DocumentFieldValue, если миграций ещё нет."""
    with connection.schema_editor() as s:
        for mdl in (DocumentInstance, DocumentFieldValue):
            if mdl._meta.db_table not in connection.introspection.table_names():
                s.create_model(mdl)


# -------------------- tests ------------------------------
class DocumentCRUDAPITests(TestCase):
    """Happy- и unhappy-path для /semd-documents/ и вложенных /fields/."""

    @classmethod
    def setUpTestData(cls):
        ensure_tables()

        # ── базовые фикстуры ───────────────────────────────
        cls.position = Position.objects.create(name="Test-Pos")
        User = get_user_model()
        cls.user   = User.objects.create_user("doc",   "pwd123", position=cls.position)
        cls.other  = User.objects.create_user("other", "pwd",    position=cls.position)

        cls.template = create_minimal(DocumentTemplate, {"name": "Эпикриз"})
        fk = {"template": cls.template} if "template" in {f.name for f in FieldDefinition._meta.fields} else {}
        cls.comp_field = create_minimal(FieldDefinition, fk | {"key": "complaint"})
        cls.temp_field = create_minimal(FieldDefinition, fk | {"key": "temp"})

    # каждый тест
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # ───────────────  positive  ───────────────────────────
    def test_create_list_retrieve_delete_document(self):
        payload = {
            "template_id": self.template.id,
            "fields": [
                {"field_id": self.comp_field.id, "value": {"text": "Боль"}},
                {"field_id": self.temp_field.id, "value": {"number": 38.6}},
            ],
        }
        resp = self.client.post(BASE_URL, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        doc_id = resp.data["id"]

        self.assertEqual(self.client.get(BASE_URL).data["count"], 1)            # list
        self.assertEqual(self.client.get(f"{BASE_URL}{doc_id}/").status_code, 200)  # retrieve
        self.assertEqual(self.client.delete(f"{BASE_URL}{doc_id}/").status_code, 204)  # delete
        self.assertFalse(DocumentInstance.objects.filter(id=doc_id).exists())

    def test_fields_list_patch_bulk(self):
        doc = create_minimal(DocumentInstance, {"user": self.user, "template": self.template})
        fv1 = DocumentFieldValue.objects.create(document=doc, field=self.comp_field, value={"text": "старое"})
        fv2 = DocumentFieldValue.objects.create(document=doc, field=self.temp_field, value={"number": 39})

        # list
        self.assertEqual(self.client.get(FIELDS_URL(doc.id)).status_code, 200)

        # patch single
        self.client.patch(f"{FIELDS_URL(doc.id)}{fv1.id}/", {"value": {"text": "нет жалоб"}}, format="json")
        fv1.refresh_from_db()
        self.assertEqual(fv1.value["text"], "нет жалоб")

        # bulk
        self.client.patch(
            f"{FIELDS_URL(doc.id)}bulk_update/",
            [{"id": fv1.id, "value": {"text": "upd"}}, {"id": fv2.id, "value": {"number": 36.6}}],
            format="json",
        )
        fv2.refresh_from_db()
        self.assertEqual(fv2.value["number"], 36.6)

    # ───────────────  negative  ───────────────────────────
    def test_unauthenticated_requests_rejected(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get(BASE_URL).status_code, {401, 403})
        self.assertIn(self.client.post(BASE_URL, {}, format="json").status_code, {401, 403})

    def test_create_invalid_payloads(self):
        self.assertEqual(self.client.post(BASE_URL, {"fields": []}, format="json").status_code, 400)  # no template

        dup_payload = {
            "template_id": self.template.id,
            "fields": [
                {"field_id": self.comp_field.id, "value": {}},
                {"field_id": self.comp_field.id, "value": {}},
            ],
        }
        self.assertEqual(self.client.post(BASE_URL, dup_payload, format="json").status_code, 400)

    def test_access_foreign_document_forbidden(self):
        alien_doc = create_minimal(DocumentInstance, {"user": self.other, "template": self.template})
        self.assertEqual(self.client.get(f"{BASE_URL}{alien_doc.id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"{BASE_URL}{alien_doc.id}/").status_code, 404)

    def test_field_operations_on_foreign_doc_forbidden(self):
        alien_doc = create_minimal(DocumentInstance, {"user": self.other, "template": self.template})
        alien_fv  = DocumentFieldValue.objects.create(document=alien_doc, field=self.comp_field, value={})

        self.assertEqual(self.client.get(FIELDS_URL(alien_doc.id)).status_code, 404)
        self.assertEqual(
            self.client.patch(f"{FIELDS_URL(alien_doc.id)}{alien_fv.id}/", {"value": {}}, format="json").status_code,
            404,
        )

    def test_bulk_update_validation_error(self):
        doc = create_minimal(DocumentInstance, {"user": self.user, "template": self.template})
        fv1 = DocumentFieldValue.objects.create(document=doc, field=self.comp_field, value={"text": "old"})
        fv2 = DocumentFieldValue.objects.create(document=doc, field=self.temp_field, value={"number": 38})

        resp = self.client.patch(
            f"{FIELDS_URL(doc.id)}bulk_update/",
            [{"id": fv1.id}, {"id": fv2.id, "value": {"number": 36.6}}],
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIsInstance(resp.data, list)
        self.assertIn("value", resp.data[0])

    def test_bulk_update_contains_foreign_value(self):
        my_doc = create_minimal(DocumentInstance, {"user": self.user, "template": self.template})
        fv1    = DocumentFieldValue.objects.create(document=my_doc, field=self.comp_field, value={})

        alien_doc = create_minimal(DocumentInstance, {"user": self.other, "template": self.template})
        alien_fv  = DocumentFieldValue.objects.create(document=alien_doc, field=self.comp_field, value={})

        resp = self.client.patch(
            f"{FIELDS_URL(my_doc.id)}bulk_update/",
            [{"id": fv1.id, "value": {"text": "ok"}}, {"id": alien_fv.id, "value": {"text": "fail"}}],
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
