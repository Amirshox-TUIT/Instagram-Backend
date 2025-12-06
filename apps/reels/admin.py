from django.contrib import admin

from apps.reels.models import Reel, ReelsComment


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_filter = ('content', 'author_id')
    search_fields = ('content',)
    list_display = ('content', 'author_id', 'id')

@admin.register(ReelsComment)
class ReelsCommentAdmin(admin.ModelAdmin):
    list_filter = ('text', 'reel_id', 'user_id')
    search_fields = ('text',)
    list_display = ('text', 'reel_id', 'user_id')

