import os
import mimetypes
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from apps.docs_ingest.models import Document


class Command(BaseCommand):
    """
    Импортирует все PDF-файлы из указанной директории в модель Document.
    """

    help = "Импортирует PDF из директории в модель Document."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            required=True,
            help="Абсолютный путь к директории, где лежат PDF-файлы.",
        )
        parser.add_argument(
            "--owner",
            type=int,
            required=True,
            help="ID пользователя-владельца создаваемых документов.",
        )
        parser.add_argument(
            "--recursive",
            action="store_true",
            help="Обходить поддиректории рекурсивно.",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help=(
                "Пропускать файлы, если объект Document уже существует "
                "с таким же именем файла."
            ),
        )

    def handle(self, *args, **options):
        path: str = options["path"]
        owner_id: int = options["owner"]
        recursive: bool = options["recursive"]
        skip_existing: bool = options["skip_existing"]

        # 1. Проверка каталога
        if not os.path.isdir(path):
            raise CommandError(f"Директория «{path}» не найдена.")

        # 2. Получаем пользователя-владельца
        User = get_user_model()
        try:
            owner = User.objects.get(pk=owner_id)
        except User.DoesNotExist:
            raise CommandError(f"Пользователь с id={owner_id} не найден.")

        imported, failed = 0, 0

        # 3. Итератор по файлам
        def walk(dir_path):
            if recursive:
                for root, _, files in os.walk(dir_path):
                    for name in files:
                        yield os.path.join(root, name)
            else:
                for name in os.listdir(dir_path):
                    yield os.path.join(dir_path, name)

        # 4. Основной цикл импорта
        for file_path in walk(path):
            if not file_path.lower().endswith(".pdf"):
                continue  # пропускаем не-PDF

            file_name = os.path.basename(file_path)

            # 4a. Проверяем дубликаты
            if skip_existing and Document.objects.filter(file=f"docs/{file_name}").exists():
                self.stdout.write(f"Пропуск: «{file_name}» уже загружён.")
                continue

            try:
                with open(file_path, "rb") as fh:
                    django_file = File(fh, name=file_name)
                    doc = Document(
                        owner=owner,
                        title=os.path.splitext(file_name)[0],
                        file=django_file,
                        source="filesystem",
                        content_type=mimetypes.guess_type(file_name)[0] or "application/pdf",
                        language="ru",
                        status=Document.Status.UPLOADED,
                    )
                    doc.save()
                    imported += 1
                    self.stdout.write(self.style.SUCCESS(f"Импортировано: {file_name}"))
            except Exception as exc:  # pylint: disable=broad-except
                failed += 1
                self.stderr.write(
                    self.style.ERROR(f"Ошибка при импорте «{file_name}»: {exc}")
                )

        # 5. Финальный отчёт
        self.stdout.write(
            self.style.SUCCESS(f"Завершено. Успешно: {imported}, ошибок: {failed}")
        )
