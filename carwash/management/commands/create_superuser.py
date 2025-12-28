from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction


class Command(BaseCommand):
    help = 'Создает суперпользователя, если он не существует'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Имя пользователя суперпользователя',
        )
        parser.add_argument(
            '--email',
            default='admin@carwash.local',
            help='Email суперпользователя',
        )
        parser.add_argument(
            '--password',
            default='admin123',
            help='Пароль суперпользователя',
        )

    def handle(self, *args, **options):
        User = get_user_model()

        username = options['username']
        email = options['email']
        password = options['password']

        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Суперпользователь "{username}" уже существует')
                    )
                    return

                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name='Администратор',
                    last_name='Системы'
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Суперпользователь "{username}" успешно создан!\n'
                        f'   Логин: {username}\n'
                        f'   Email: {email}\n'
                        f'   Пароль: {password}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при создании суперпользователя: {e}')
            )
