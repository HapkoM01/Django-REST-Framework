from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from .models import Payment
from .serializers import (
    UserSerializer,
    UserPublicSerializer,
    UserRegisterSerializer,
    PaymentSerializer,
)
from .filters import PaymentFilter
from .permissions import IsOwnerProfile

User = get_user_model()


class UserRegisterAPIView(generics.CreateAPIView):
    """Регистрация — доступна без авторизации."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD пользователей.
    - list/retrieve: любой авторизованный
      (свой профиль — полный, чужой — публичный)
    - update/partial_update/destroy: только свой профиль
    - create: через /api/auth/register/
    """
    queryset = User.objects.all().prefetch_related('payments')
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsOwnerProfile()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == request.user:
            serializer = UserSerializer(instance)
        else:
            serializer = UserPublicSerializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # список — только публичная информация
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserPublicSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserPublicSerializer(queryset, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """CRUD платежей + фильтрация и сортировка."""
    queryset = Payment.objects.select_related('user', 'paid_course', 'paid_lesson').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
