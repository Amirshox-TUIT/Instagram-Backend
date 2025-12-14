from django.contrib import admin
from telebot.types import Chat

from apps.chats.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_filter = ("content", 'sender', 'recipient')
    list_display = ("id", "content", "sender", "recipient")
    search_fields = ("id", "content")
