from django.core.management.base import BaseCommand
from decimal import Decimal
from django.contrib.auth.models import Group
from users.models import User, Payment
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Загружает тестовые данные: группу moderators, пользователей, курсы, уроки, платежи'

    def handle(self, *args, **options):
        # Группа модераторов
        Group.objects.get_or_create(name='moderators')

        # Пользователи
        user1, created = User.objects.get_or_create(
            email='user1@example.com',
            defaults={'phone': '+79001112233', 'city': 'Москва'}
        )
        if created or not user1.has_usable_password():
            user1.set_password('password123')
            user1.save()

        user2, created = User.objects.get_or_create(
            email='user2@example.com',
            defaults={'phone': '+79004445566', 'city': 'Санкт-Петербург'}
        )
        if created or not user2.has_usable_password():
            user2.set_password('password123')
            user2.save()

        moderator, created = User.objects.get_or_create(
            email='moderator@example.com',
            defaults={'phone': '+79007778899', 'city': 'Казань'}
        )
        if created or not moderator.has_usable_password():
            moderator.set_password('password123')
            moderator.save()
        moderators_group = Group.objects.get(name='moderators')
        moderator.groups.add(moderators_group)

        # Курсы
        course1, _ = Course.objects.get_or_create(
            title='DRF',
            defaults={'description': 'Курс по Django REST Framework', 'owner': user1}
        )
        if course1.owner is None:
            course1.owner = user1
            course1.save()

        course2, _ = Course.objects.get_or_create(
            title='Python Backend',
            defaults={'description': 'Бэкенд на Python', 'owner': user2}
        )
        if course2.owner is None:
            course2.owner = user2
            course2.save()

        # Уроки
        lesson1, _ = Lesson.objects.get_or_create(
            course=course1,
            title='Введение в DRF',
            defaults={
                'description': 'Сериализаторы и ViewSets',
                'video_url': 'https://example.com/1',
                'owner': user1,
            }
        )
        if lesson1.owner is None:
            lesson1.owner = user1
            lesson1.save()

        lesson2, _ = Lesson.objects.get_or_create(
            course=course1,
            title='Фильтры и пагинация',
            defaults={
                'description': 'django-filter',
                'video_url': 'https://example.com/2',
                'owner': user1,
            }
        )
        if lesson2.owner is None:
            lesson2.owner = user1
            lesson2.save()

        lesson3, _ = Lesson.objects.get_or_create(
            course=course2,
            title='ORM основы',
            defaults={
                'description': 'Модели и запросы',
                'video_url': 'https://example.com/3',
                'owner': user2,
            }
        )
        if lesson3.owner is None:
            lesson3.owner = user2
            lesson3.save()

        # Платежи
        Payment.objects.filter(user__in=[user1, user2]).delete()

        payments_data = [
            {
                'user': user1,
                'paid_course': course1,
                'paid_lesson': None,
                'amount': Decimal('5000.00'),
                'payment_method': Payment.TRANSFER,
            },
            {
                'user': user1,
                'paid_course': None,
                'paid_lesson': lesson2,
                'amount': Decimal('500.00'),
                'payment_method': Payment.CASH,
            },
            {
                'user': user2,
                'paid_course': course2,
                'paid_lesson': None,
                'amount': Decimal('7000.00'),
                'payment_method': Payment.TRANSFER,
            },
            {
                'user': user2,
                'paid_course': None,
                'paid_lesson': lesson1,
                'amount': Decimal('300.00'),
                'payment_method': Payment.CASH,
            },
            {
                'user': user1,
                'paid_course': course2,
                'paid_lesson': None,
                'amount': Decimal('7000.00'),
                'payment_method': Payment.CASH,
            },
        ]

        for data in payments_data:
            Payment.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(
            f'Пользователей: {User.objects.count()}, '
            f'курсов: {Course.objects.count()}, '
            f'уроков: {Lesson.objects.count()}, '
            f'платежей: {Payment.objects.count()}, '
            f'группа moderators: OK, модератор: {moderator.email}'
        ))
