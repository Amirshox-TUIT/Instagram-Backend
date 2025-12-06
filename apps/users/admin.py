from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'followers_count', 'followings_count', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('following',)

    fieldsets = (
        ("User Info", {
            "fields": ("username", "email", "password")
        }),
        ("Profile", {
            "fields": ("profile_picture", "bio")
        }),
        ("Relations", {
            "fields": ("following",)
        }),
        ("Dates", {
            "fields": ("created_at", "updated_at")
        }),
    )