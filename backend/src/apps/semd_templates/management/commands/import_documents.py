import json
from pathlib import Path
from types import SimpleNamespace

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.semd_templates.models import (
    DocumentTemplate,
    FieldDefinition,
)
from api.api_v0.semd_templates.serializers.document_instance import (
    DocumentInstanceCreateSerializer,
)


class Command(BaseCommand):
    """
    Импортирует документы из JSON-файла, используя
    DocumentInstanceCreateSerializer для валидации.
    """

    help = (
        "Загружает документы в базу из JSON. "
        "Пример использования:\n"
        "  python manage.py import_documents --file data.json --user admin"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            "-f",
            required=True,
            help="Путь к JSON-файлу с данными.",
        )
        parser.add_argument(
            "--user",
            "-u",
            required=True,
            help="ID или username пользователя, от чьего имени создаются документы.",
        )

    # ──────────────────────────────────────────────────────────────────
    #                        helpers
    # ──────────────────────────────────────────────────────────────────
    def _get_user(self, user_arg):
        User = get_user_model()
        try:
            # сначала пытаемся как PK
            return User.objects.get(pk=int(user_arg))
        except (ValueError, User.DoesNotExist):
            pass
        try:
            return User.objects.get(username=user_arg)
        except User.DoesNotExist as exc:
            raise CommandError(f"Пользователь «{user_arg}» не найден.") from exc

    def _load_json(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            raise CommandError(f"Файл «{file_path}» не найден.")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Невалидный JSON: {exc}") from exc

    # ──────────────────────────────────────────────────────────────────
    #                        main handle
    # ──────────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        json_data = self._load_json(options["file"])
        user = self._get_user(options["user"])

        templates = json_data.get("templates", [])
        if not templates:
            self.stdout.write(self.style.WARNING("В файле нет шаблонов для импорта."))
            return

        successes, failures = 0, 0

        # искусственный request, чтобы сериализатор не упал
        fake_request = SimpleNamespace(user=user)

        for idx, tmpl in enumerate(templates, start=1):
            payload = {
                "template_id": tmpl["template_id"],
                "fields": [
                    {"field_id": f["field_id"], "value": f["value"]}
                    for f in tmpl.get("fields", [])
                ],
            }
            serializer = DocumentInstanceCreateSerializer(
                data=payload,
                context={"request": fake_request},
            )

            try:
                serializer.is_valid(raise_exception=True)
                with transaction.atomic():
                    serializer.save()  # создаёт DocumentInstance + значения
                successes += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{idx}/{len(templates)}] Документ «{tmpl['slug']}» импортирован."
                    )
                )
            except Exception as exc:
                failures += 1
                msg = (
                    exc.detail  # DRF ValidationError
                    if hasattr(exc, "detail")
                    else str(exc)
                )
                self.stderr.write(
                    self.style.ERROR(
                        f"[{idx}/{len(templates)}] Ошибка в «{tmpl['slug']}»: {msg}"
                    )
                )

        # ─────────── summary ───────────
        self.stdout.write(self.style.MIGRATE_HEADING("\nИтого"))
        self.stdout.write(self.style.SUCCESS(f"  Успешно: {successes}"))
        self.stdout.write(self.style.ERROR(f"  Ошибок : {failures}"))
