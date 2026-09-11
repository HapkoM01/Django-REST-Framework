from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(BasePermission):
    """Проверка: пользователь состоит в группе moderators."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name='moderators').exists()
        )


class IsOwner(BasePermission):
    """Проверка: пользователь — владелец объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrModerator(BasePermission):
    """
    Владелец может всё со своим объектом.
    Модератор может читать и редактировать любой объект, но не удалять.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        is_moderator = request.user.groups.filter(name='moderators').exists()

        if is_moderator:
            # модератор не может удалять
            if request.method == 'DELETE':
                return False
            return True

        return obj.owner == request.user


class IsOwnerProfile(BasePermission):
    """Редактировать профиль может только сам пользователь."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user
