from django.db import models


class SentMessage(models.Model):
    """One record per SMS send attempt (powers the message-history feature)."""

    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    recipient = models.CharField(max_length=20)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    provider_sid = models.CharField(max_length=64, blank=True)
    error_detail = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} ({self.status}) at {self.created_at:%Y-%m-%d %H:%M}"
