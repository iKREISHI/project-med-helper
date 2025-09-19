from django.db import models
from django.utils import timezone

from apps.chat.models.chat_session import ChatSession


class ChatMessage(models.Model):
    """
    Сообщение пользователя
    """

    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"

    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "System"),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    token_count = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["session", "created_at"]),
        ]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщение"
