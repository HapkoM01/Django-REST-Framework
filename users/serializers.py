from rest_framework import serializers
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор платежа (для списка и фильтрации)."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='paid_course.title', read_only=True, default=None)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True, default=None)

    class Meta:
        model = Payment
        fields = (
            'id',
            'user',
            'user_email',
            'payment_date',
            'paid_course',
            'course_title',
            'paid_lesson',
            'lesson_title',
            'amount',
            'payment_method',
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя + история платежей (доп. задание).
    """
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone',
            'city',
            'avatar',
            'is_active',
            'date_joined',
            'payments',
        )
        read_only_fields = ('id', 'date_joined')
