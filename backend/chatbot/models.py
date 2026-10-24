from django.db import models
from django.utils import timezone

from common.models import BaseModel


class ChatbotConversation(BaseModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="+")
    school = models.ForeignKey(
        "accounts.School", null=True, blank=True, on_delete=models.PROTECT
    )
    started_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "chatbot_conversations"


class ChatbotMessage(BaseModel):
    SENDERS = [("user", "User"), ("assistant", "Assistant")]

    conversation = models.ForeignKey(
        ChatbotConversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=10, choices=SENDERS)
    content = models.TextField()

    class Meta:
        db_table = "chatbot_messages"