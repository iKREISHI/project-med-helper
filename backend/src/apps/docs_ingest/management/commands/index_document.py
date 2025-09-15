from django.core.management.base import BaseCommand, CommandError

# ВАЖНО: импортируем задачу Celery из приложения
from apps.docs_ingest.tasks import pipeline_index_document


class Command(BaseCommand):
    help = (
        "Синхронно запускает пайплайн индексирования для указанного документа.\n"
        "Использование: manage.py index_document <doc_id>\n"
        "Полезно для локальной отладки без запущенного Celery worker."
    )

    def add_arguments(self, parser):
        parser.add_argument("doc_id", type=int, help="ID документа из БД")

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        if doc_id <= 0:
            raise CommandError("Некорректный doc_id")
        self.stdout.write(self.style.NOTICE(f"[cmd] Запуск индексирования doc_id={doc_id} (синхронно)"))
        # Выполняем задачу синхронно, чтобы увидеть полный лог/трейс
        result = pipeline_index_document.apply(args=(doc_id,))
        if result.failed():
            raise CommandError(f"Индексирование завершилось ошибкой: {result.traceback}")
        self.stdout.write(self.style.SUCCESS("[cmd] Индексирование завершено успешно"))
