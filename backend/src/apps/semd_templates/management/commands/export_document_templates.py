import os
import json
from django.core.management.base import BaseCommand
from apps.semd_templates.models.semd_docs_templates import DocumentTemplate, TemplateField

class Command(BaseCommand):
    help = "Экспорт DocumentTemplate и всех его полей в JSON файл"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json_file",
            type=str,
            help="Путь к JSON файлу для экспорта. По умолчанию 'json_examples/document_templates_export.json' рядом с manage.py"
        )

    def handle(self, *args, **options):
        # Путь по умолчанию
        json_file = options.get("json_file")
        if not json_file:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split("apps")[0]
            export_dir = os.path.join(project_root, "json_examples")
            os.makedirs(export_dir, exist_ok=True)
            json_file = os.path.join(export_dir, "document_templates_export.json")

        templates = DocumentTemplate.objects.all()
        export_data = []

        for template in templates:
            fields_data = []
            seen_keys = set()
            for tf in TemplateField.objects.filter(template=template).order_by("order"):
                key = tf.field.key
                if key in seen_keys:
                    self.stdout.write(self.style.WARNING(f"Дублирующее поле пропущено: {key}"))
                    continue
                seen_keys.add(key)
                fields_data.append({
                    "key": key,
                    "label": tf.field.label,
                    "field_type": tf.field.field_type,
                    "required": tf.field.required,
                    "server_validators": tf.field.server_validators,
                    "validation_strategy": tf.field.validation_strategy,
                    "order": tf.order
                })

            export_data.append({
                "name": template.name,
                "slug": template.slug,
                "description": template.description,
                "fields": fields_data
            })

        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS(f"Экспорт завершён. Файл: {json_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка записи файла: {e}"))
