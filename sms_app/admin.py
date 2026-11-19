from django.contrib import admin

from .models import SentMessage


@admin.register(SentMessage)
class SentMessageAdmin(admin.ModelAdmin):
    list_display = ("recipient", "status", "created_at", "provider_sid")
    list_filter = ("status", "created_at")
    search_fields = ("recipient", "body")
