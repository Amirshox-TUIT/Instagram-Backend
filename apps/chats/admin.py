from django.contrib import admin
from telebot.types import Chat

from apps.chats.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_filter = ("content", 'sender_id', 'recipient')
    list_display = ("id", "content", "sender_id", "recipient")
    search_fields = ("id", "content")
