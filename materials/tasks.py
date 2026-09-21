from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_course_update_email(course_id: int, course_title: str, subscriber_emails: list):
    """
    Рассылка писем подписчикам об обновлении материалов курса.
    """
    if not subscriber_emails:
        return f'No subscribers for course {course_id}'

    subject = f'Обновление курса: {course_title}'
    message = (
        f'Курс «{course_title}» был обновлён.\n'
        f'Зайдите в личный кабинет, чтобы ознакомиться с новыми материалами.'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@lms.local')

    # одна рассылка нескольким получателям
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=subscriber_emails,
        fail_silently=False,
    )
    return f'Sent to {len(subscriber_emails)} subscribers for course {course_id}'
