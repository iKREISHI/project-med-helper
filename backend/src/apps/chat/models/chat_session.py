from django.conf import settings
from django.db import models
from django.utils import timezone


class ChatSession(models.Model):
    """
    Один «диалог» (чат-сеанс). Создаётся при первом сообщении пользователя.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    title = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Диалог (чат-сеанс)"
        verbose_name_plural = "Диалоги (чат-сеансы)"

    def __str__(self) -> str:  # pragma: no cover
        return f"ChatSession({self.uuid})"