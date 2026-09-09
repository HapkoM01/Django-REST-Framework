from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from users.models import User, Payment
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Загружает тестовые данные платежей (и при необходимости пользователей/курсы/уроки)'

    def handle(self, *args, **options):
        # Пользователи
        user1, _ = User.objects.get_or_create(
            email='user1@example.com',
            defaults={'phone': '+79001112233', 'city': 'Москва'}
        )
        if not user1.has_usable_password():
            user1.set_password('password123')
            user1.save()

        user2, _ = User.objects.get_or_create(
            email='user2@example.com',
            defaults={'phone': '+79004445566', 'city': 'Санкт-Петербург'}
        )
        if not user2.has_usable_password():
            user2.set_password('password123')
            user2.save()

        # Курсы
        course1, _ = Course.objects.get_or_create(
            title='DRF',
            defaults={'description': 'Курс по Django REST Framework'}
        )
        course2, _ = Course.objects.get_or_create(
            title='Python Backend',
            defaults={'description': 'Бэкенд на Python'}
        )

        # Уроки
        lesson1, _ = Lesson.objects.get_or_create(
            course=course1,
            title='Введение в DRF',
            defaults={'description': 'Сериализаторы и ViewSets', 'video_url': 'https://example.com/1'}
        )
        lesson2, _ = Lesson.objects.get_or_create(
            course=course1,
            title='Фильтры и пагинация',
            defaults={'description': 'django-filter', 'video_url': 'https://example.com/2'}
        )
        lesson3, _ = Lesson.objects.get_or_create(
            course=course2,
            title='ORM основы',
            defaults={'description': 'Модели и запросы', 'video_url': 'https://example.com/3'}
        )

        # Платежи (очищаем старые тестовые, чтобы не дублировать при повторном запуске)
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
            f'Создано пользователей: {User.objects.count()}, '
            f'курсов: {Course.objects.count()}, '
            f'уроков: {Lesson.objects.count()}, '
            f'платежей: {Payment.objects.count()}'
        ))
