from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from apps.users.models.position import Position


class Command(BaseCommand):
    """
    Команда для добавления должностей.

    Режимы работы
    1. Добавить одну должность:
       python manage.py create_positions --name "Врач-терапевт" \
                                         --short-name "Терапевт"

    2. Добавить стандартный набор врачебных должностей:
       python manage.py create_positions --medical-set
    """
    help = _('Create medical staff positions.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Полное наименование должности.'),
        )
        parser.add_argument(
            '--short-name',
            dest='short_name',
            help=_('Сокращённое наименование должности.'),
        )
        parser.add_argument(
            '--minzdrav',
            dest='minzdrav_position',
            help=_('Соответствующая должность Минздрава.'),
        )
        parser.add_argument(
            '--medical-set',
            action='store_true',
            help=_('Создать типовой набор врачебных должностей.'),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        medical_set: bool = options['medical_set']
        name: str | None = options.get('name')
        short_name: str | None = options.get('short_name')
        minzdrav_position: str | None = options.get('minzdrav_position')

        if medical_set and name:
            raise CommandError(_(
                'Параметры --medical-set и --name несовместимы.'
            ))
        if not medical_set and not name:
            raise CommandError(_(
                'Укажите либо --medical-set, либо --name.'
            ))

        if medical_set:
            positions = [
                {
                    'name': 'Главный врач',
                    'short_name': 'Главврач',
                    'minzdrav_position': 'Главный врач'
                },
                {
                    'name': 'Заместитель главного врача',
                    'short_name': 'Зам. главврача',
                    'minzdrav_position': 'Заместитель главного врача'
                },
                {
                    'name': 'Врач-терапевт участковый',
                    'short_name': 'Терапевт',
                    'minzdrav_position': 'Врач-терапевт'
                },
                {
                    'name': 'Врач-кардиолог',
                    'short_name': 'Кардиолог',
                    'minzdrav_position': 'Врач-кардиолог'
                },
                {
                    'name': 'Врач-хирург',
                    'short_name': 'Хирург',
                    'minzdrav_position': 'Врач-хирург'
                },
                {
                    'name': 'Врач-невролог',
                    'short_name': 'Невролог',
                    'minzdrav_position': 'Врач-невролог'
                },
                {
                    'name': 'Врач-анестезиолог-реаниматолог',
                    'short_name': 'Реаниматолог',
                    'minzdrav_position': 'Врач-анестезиолог-реаниматолог'
                },
                {
                    'name': 'Врач-педиатр',
                    'short_name': 'Педиатр',
                    'minzdrav_position': 'Врач-педиатр'
                },
                {
                    'name': 'Старшая медицинская сестра',
                    'short_name': 'Ст. м/с',
                    'minzdrav_position': 'Старшая медицинская сестра'
                },
                {
                    'name': 'Медицинская сестра участковая',
                    'short_name': 'М/с участковая',
                    'minzdrav_position': 'Медицинская сестра участковая'
                },
            ]
        else:
            positions = [{
                'name': name,
                'short_name': short_name,
                'minzdrav_position': minzdrav_position or name,
            }]

        created_total = 0
        for entry in positions:
            try:
                obj, created_flag = Position.objects.get_or_create(
                    name=entry['name'],
                    defaults={
                        'short_name': entry.get('short_name'),
                        'minzdrav_position': entry.get('minzdrav_position'),
                    }
                )
            except IntegrityError as exc:
                raise CommandError(_(
                    f'Ошибка БД при создании «{entry["name"]}»: {exc}'
                ))

            if created_flag:
                created_total += 1
                self.stdout.write(self.style.SUCCESS(
                    _(f'Создана должность «{obj.name}».')
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    _(f'Должность «{obj.name}» уже существует, пропущено.')
                ))

        self.stdout.write(self.style.MIGRATE_HEADING(
            _(f'Итого создано {created_total} должн.')
        ))
