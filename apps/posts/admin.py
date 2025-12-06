from django.contrib import admin

from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'caption', 'created_at')
    search_fields = ('caption',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('likes',)