import os
import json
from django.core.management.base import BaseCommand
from apps.semd_templates.models.semd_docs_templates import DocumentTemplate, TemplateField
from apps.semd_templates.models.semd_fields import FieldDefinition

class Command(BaseCommand):
    help = "Импорт DocumentTemplate и всех его полей из JSON файла"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json_file",
            type=str,
            help="Путь к JSON файлу для импорта. По умолчанию ищет 'json_examples/document_templates_import.json' рядом с manage.py"
        )

    def handle(self, *args, **options):
        # Определяем путь по умолчанию
        json_file = options.get("json_file")
        if not json_file:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split("apps")[0]
            import_dir = os.path.join(project_root, "json_examples")
            json_file = os.path.join(import_dir, "document_templates_import.json")

        if not os.path.exists(json_file):
            self.stderr.write(self.style.ERROR(f"Файл {json_file} не найден"))
            return

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                templates_data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка чтения файла: {e}"))
            return

        for template_item in templates_data:
            template, created = DocumentTemplate.objects.update_or_create(
                slug=template_item["slug"],
                defaults={
                    "name": template_item.get("name", ""),
                    "description": template_item.get("description", ""),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан шаблон: {template.slug}"))
            else:
                self.stdout.write(self.style.WARNING(f"Обновлён шаблон: {template.slug}"))

            seen_keys = set()
            for field_item in template_item.get("fields", []):
                key = field_item["key"]

                if key in seen_keys:
                    self.stdout.write(self.style.WARNING(f"Дублирующее поле пропущено: {key}"))
                    continue
                seen_keys.add(key)

                # Проверяем наличие поля в базе
                field, _ = FieldDefinition.objects.get_or_create(
                    key=key,
                    defaults={
                        "label": field_item.get("label", ""),
                        "field_type": field_item.get("field_type", "text"),
                        "required": field_item.get("required", False),
                        "server_validators": field_item.get("server_validators", []),
                        "validation_strategy": field_item.get("validation_strategy", "server"),
                    }
                )

                # Создаём связь TemplateField
                TemplateField.objects.update_or_create(
                    template=template,
                    field=field,
                    defaults={"order": field_item.get("order", 0)}
                )

        self.stdout.write(self.style.SUCCESS("Импорт шаблонов завершён."))
