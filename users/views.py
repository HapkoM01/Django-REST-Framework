from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from materials.models import Course
from .models import Payment
from .serializers import (
    UserSerializer,
    UserPublicSerializer,
    UserRegisterSerializer,
    PaymentSerializer,
    StripeCheckoutSerializer,
)
from .filters import PaymentFilter
from .permissions import IsOwnerProfile
from .services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session,
    retrieve_stripe_session,
    StripeError,
)

User = get_user_model()


class UserRegisterAPIView(generics.CreateAPIView):
    """Регистрация пользователя (без JWT)."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """CRUD пользователей. Свой профиль — полный, чужой — публичный."""
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


class StripeCheckoutAPIView(APIView):
    """
    Создание оплаты курса через Stripe.
    Создаёт Product → Price → Checkout Session, сохраняет Payment.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=StripeCheckoutSerializer,
        responses={
            201: PaymentSerializer,
            400: OpenApiResponse(description='Ошибка валидации или Stripe'),
            404: OpenApiResponse(description='Курс не найден'),
        },
        examples=[
            OpenApiExample(
                'Запрос',
                value={
                    'course_id': 1,
                    'success_url': 'http://127.0.0.1:8000/success/',
                    'cancel_url': 'http://127.0.0.1:8000/cancel/',
                },
                request_only=True,
            ),
        ],
        description='Создаёт продукт, цену и сессию Stripe. Возвращает платёж со ссылкой на оплату.',
    )
    def post(self, request, *args, **kwargs):
        serializer = StripeCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        success_url = serializer.validated_data['success_url']
        cancel_url = serializer.validated_data['cancel_url']

        course = get_object_or_404(Course, pk=course_id)
        amount = course.price or 0
        if amount <= 0:
            return Response(
                {'error': 'У курса не указана цена (price > 0)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = create_stripe_product(
                name=course.title,
                description=course.description or course.title,
            )
            price = create_stripe_price(product['id'], float(amount))
            session = create_stripe_checkout_session(
                price_id=price['id'],
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=request.user.email,
            )
        except StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            user=request.user,
            paid_course=course,
            amount=amount,
            payment_method=Payment.STRIPE,
            status=Payment.STATUS_PENDING,
            stripe_product_id=product['id'],
            stripe_price_id=price['id'],
            stripe_session_id=session['id'],
            payment_link=session['url'],
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class StripeSessionStatusAPIView(APIView):
    """Проверка статуса Stripe-сессии и синхронизация с Payment."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='session_id',
                location=OpenApiParameter.PATH,
                description='ID сессии Stripe (cs_...)',
                required=True,
                type=str,
            ),
        ],
        responses={200: PaymentSerializer, 400: OpenApiResponse(description='Ошибка Stripe'), 404: OpenApiResponse(description='Платёж не найден')},
    )
    def get(self, request, session_id, *args, **kwargs):
        payment = get_object_or_404(
            Payment,
            stripe_session_id=session_id,
            user=request.user,
        )
        try:
            session = retrieve_stripe_session(session_id)
        except StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # синхронизация статуса
        if session['payment_status'] == 'paid':
            payment.status = Payment.STATUS_PAID
        elif session['status'] == 'expired':
            payment.status = Payment.STATUS_CANCELED
        payment.save(update_fields=['status'])

        data = PaymentSerializer(payment).data
        data['stripe_session'] = session
        return Response(data)
