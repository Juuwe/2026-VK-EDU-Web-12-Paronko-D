from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email')

    class ProfileInline(admin.StackedInline):
        model = Profile
        extra = 0

    inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'created_at', 'correct_answers_count',)
    search_fields = ('user__username', 'nickname', 'user__email',)
    list_filter = ('created_at',)

    list_select_related = ('user',)
