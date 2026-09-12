from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор платежа."""
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


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password_confirm', 'phone', 'city', 'avatar')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Пароли не совпадают'})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Пользователь с таким email уже существует'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Публичный профиль (чужой): без пароля, без истории платежей.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'date_joined')
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """
    Полный профиль (свой): с историей платежей.
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
        read_only_fields = ('id', 'date_joined', 'email')
