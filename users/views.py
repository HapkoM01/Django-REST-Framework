from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD / редактирование профиля пользователя (дополнительное задание).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
