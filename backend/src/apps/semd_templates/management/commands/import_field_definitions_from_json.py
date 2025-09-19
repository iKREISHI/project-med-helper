import json
import os
from django.core.management.base import BaseCommand
from apps.semd_templates.models.semd_fields import FieldDefinition

class Command(BaseCommand):
    help = "Импорт FieldDefinition из JSON файла"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json_file",
            type=str,
            help="Путь к JSON файлу с определениями полей. По умолчанию ищет 'field_definitions.json' в папке 'data_json' рядом с manage.py",
        )

    def handle(self, *args, **options):
        json_file = options.get("json_file")
        if not json_file:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split("apps")[0]
            default_dir = os.path.join(project_root, "json_examples")
            default_name = "field_definitions.json"
            json_file = os.path.join(default_dir, default_name)
            if not os.path.exists(json_file):
                self.stderr.write(self.style.ERROR(
                    f"Файл '{default_name}' не найден в папке '{default_dir}'"
                ))
                return

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка чтения файла: {e}"))
            return

        for item in data:
            field, created = FieldDefinition.objects.update_or_create(
                key=item["key"],
                defaults={
                    "label": item.get("label", ""),
                    "field_type": item.get("field_type", "text"),
                    "required": item.get("required", False),
                    "server_validators": item.get("server_validators", []),
                    "validation_strategy": item.get("validation_strategy", "server"),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создано поле: {field.key}"))
            else:
                self.stdout.write(self.style.WARNING(f"Обновлено поле: {field.key}"))

        self.stdout.write(self.style.SUCCESS("Импорт завершён."))
