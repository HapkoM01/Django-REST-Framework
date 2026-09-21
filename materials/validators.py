from django.core.exceptions import ValidationError
from urllib.parse import urlparse


def validate_youtube_url(value):
    """
    Разрешены только ссылки на youtube.com / youtu.be.
    """
    if not value:
        return

    try:
        parsed = urlparse(value)
    except Exception:
        raise ValidationError('Некорректная ссылка на видео.')

    host = (parsed.netloc or '').lower()
    # убираем www.
    if host.startswith('www.'):
        host = host[4:]

    allowed = ('youtube.com', 'youtu.be')
    if host not in allowed:
        raise ValidationError(
            'Ссылка на видео должна вести только на youtube.com (или youtu.be). '
            'Сторонние ресурсы запрещены.'
        )
