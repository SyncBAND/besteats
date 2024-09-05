from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.authentication.models import User
from apps.profiles.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Info'
    extra = 0
    max_num = 1
    min_num = 1


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Custom user model admin.
    """
    inlines = [ProfileInline]
