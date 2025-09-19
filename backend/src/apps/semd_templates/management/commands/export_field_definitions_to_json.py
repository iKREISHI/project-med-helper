import os
import json
from django.core.management.base import BaseCommand
from apps.semd_templates.models.semd_fields import FieldDefinition

class Command(BaseCommand):
    help = "Экспорт FieldDefinition в JSON файл"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json_file",
            type=str,
            help="Путь к JSON файлу для экспорта. По умолчанию 'export_json/field_definitions_export.json' рядом с manage.py"
        )

    def handle(self, *args, **options):
        json_file = options.get("json_file")
        if not json_file:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split("apps")[0]
            export_dir = os.path.join(project_root, "json_examples")
            os.makedirs(export_dir, exist_ok=True)
            json_file = os.path.join(export_dir, "field_definitions_export.json")

        field_list = FieldDefinition.objects.all()
        seen_keys = set()
        export_data = []

        for field in field_list:
            if field.key in seen_keys:
                self.stdout.write(self.style.WARNING(f"Дублирующее поле пропущено: {field.key}"))
                continue
            seen_keys.add(field.key)
            export_data.append({
                "key": field.key,
                "label": field.label,
                "field_type": field.field_type,
                "required": field.required,
                "server_validators": field.server_validators,
                "validation_strategy": field.validation_strategy
            })

        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS(f"Экспорт завершён. Файл: {json_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка записи файла: {e}"))
