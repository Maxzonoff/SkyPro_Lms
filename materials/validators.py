import re
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Проверяет, что ссылка ведёт только на YouTube.
    value — строка с URL.
    """
    pattern = r"^https?://(www\.|m\.)?(youtube\.com|youtu\.be)/.*$"
    if not value:
        return value

    if not re.match(pattern, value.lower()):
        raise serializers.ValidationError("Разрешены только ссылки на YouTube")

    return value
