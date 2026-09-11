from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для курса через ViewSet.
    - create: только авторизованный НЕ-модератор (модератор не может создавать)
    - list/retrieve: авторизованные
    - update/partial_update: владелец или модератор
    - destroy: только владелец (модератор не может удалять)
    """
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.none()
        if user.groups.filter(name='moderators').exists() or user.is_superuser:
            return Course.objects.all()
        # обычный пользователь видит только свои курсы
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action == 'create':
            # модератор не может создавать
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ('update', 'partial_update'):
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # list, retrieve
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Список и создание уроков.
    Создание — только авторизованный НЕ-модератор.
    """
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name='moderators').exists() or user.is_superuser:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление, удаление урока.
    - retrieve/update: владелец или модератор
    - destroy: только владелец
    """
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name='moderators').exists() or user.is_superuser:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.request.method in ('PUT', 'PATCH'):
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]
