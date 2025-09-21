from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    """
    Создаёт суперпользователя для кастомной модели User.

   Режимы работы
    1. Полностью неинтерактивный:
       python manage.py create_superuser --username admin --password secret

    2. Генерация случайного пароля:
       python manage.py create_superuser --username admin --gen-pass

    3. Пароль = логин (только для разработки):
       python manage.py create_superuser --username admin --dev-pass

    4. Полноценная интерактивность (пароль вводится вручную):
       python manage.py create_superuser --username admin
    """
    help = _('Create a superuser for the custom User model.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            required=True,
            help=_('Имя пользователя (обязательно).'),
        )
        parser.add_argument(
            '--password',
            help=_('Пароль. Пропустите, чтобы ввести вручную.'),
        )
        parser.add_argument(
            '--gen-pass',
            action='store_true',
            help=_('Сгенерировать безопасный случайный пароль.'),
        )
        parser.add_argument(
            '--dev-pass',
            action='store_true',
            help=_('Использовать логин как пароль (НЕ ДЛЯ ПРОДАКШНА!).'),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        username: str = options['username']
        password: str | None = options.get('password')
        gen_pass: bool = options['gen_pass']
        dev_pass: bool = options['dev_pass']

        exclusive_flags = sum([bool(password), gen_pass, dev_pass])
        if exclusive_flags > 1:
            raise CommandError(_(
                'Параметры --password, --gen-pass и --dev-pass '
                'взаимоисключают друг друга.'
            ))

        if dev_pass:
            password = username
            self.stdout.write(
                self.style.NOTICE(
                    _('ВНИМАНИЕ: используется режим dev — пароль = логин.')
                )
            )

        if gen_pass:
            password = User.objects.make_random_password()
            self.stdout.write(
                self.style.MIGRATE_HEADING(_('Сгенерированный пароль: ') + password)
            )

        if not password:
            while True:
                password = getpass('Введите пароль: ')
                password2 = getpass('Повторите пароль: ')

                if password != password2:
                    self.stderr.write(_('Пароли не совпадают. Попробуйте снова.\n'))
                    continue
                try:
                    validate_password(password)
                except Exception as exc:
                    self.stderr.write(_(f'Пароль не прошёл валидацию: {exc}\n'))
                    continue
                break

        try:
            if User.objects.filter(username=username).first():
                return
            User.objects.create_superuser(username=username, password=password)
        except IntegrityError:
            raise CommandError(_('Пользователь с таким именем уже существует.'))
        except Exception as exc:
            raise CommandError(_(f'Ошибка создания суперпользователя: {exc}'))

        self.stdout.write(self.style.SUCCESS(
            _(f'Суперпользователь «{username}» успешно создан.')
        ))
