from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer
from .filters import PaymentFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD / редактирование профиля пользователя.
    При GET возвращается история платежей.
    """
    queryset = User.objects.all().prefetch_related('payments')
    serializer_class = UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD платежей + фильтрация и сортировка.
    """
    queryset = Payment.objects.select_related('user', 'paid_course', 'paid_lesson').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
