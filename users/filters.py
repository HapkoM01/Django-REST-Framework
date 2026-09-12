import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    """
    Фильтрация платежей:
    - по курсу (paid_course)
    - по уроку (paid_lesson)
    - по способу оплаты (payment_method)
    Сортировка по дате — через OrderingFilter во view.
    """
    paid_course = django_filters.NumberFilter(field_name='paid_course_id')
    paid_lesson = django_filters.NumberFilter(field_name='paid_lesson_id')
    payment_method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHOD_CHOICES)

    class Meta:
        model = Payment
        fields = ['paid_course', 'paid_lesson', 'payment_method']
