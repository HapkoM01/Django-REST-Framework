from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')
