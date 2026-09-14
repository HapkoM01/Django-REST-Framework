from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet,
    PaymentViewSet,
    UserRegisterAPIView,
    StripeCheckoutAPIView,
    StripeSessionStatusAPIView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('auth/register/', UserRegisterAPIView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('payments/stripe/checkout/', StripeCheckoutAPIView.as_view(), name='stripe-checkout'),
    path(
        'payments/stripe/status/<str:session_id>/',
        StripeSessionStatusAPIView.as_view(),
        name='stripe-session-status',
    ),
    path('', include(router.urls)),
]
