from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца (last_login).
    Обновление батчем, не по одному.
    """
    threshold = timezone.now() - timedelta(days=30)
    qs = User.objects.filter(
        is_active=True,
        last_login__lt=threshold,
    )
    # также пользователи, которые ни разу не логинились и зарегистрированы > месяца назад
    never_logged = User.objects.filter(
        is_active=True,
        last_login__isnull=True,
        date_joined__lt=threshold,
    )
    count = qs.update(is_active=False) + never_logged.update(is_active=False)
    return f'Deactivated {count} users'
