from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from profiles.forms import CustomUserChangeForm, CustomUserCreationForm
from profiles.models import (
    CustomUser, EmailReset, Group, Organization, PasswordReminder, PasswordReminderQuestions, Role, UserGroupRole)


class UserGroupRoleInline(admin.TabularInline):
    model = UserGroupRole
    fk_name = "user"
    fields = ("user", "group", "role")
    extra = 1
    show_change_link = True


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at", "slug")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_group', 'organization')
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")
    raw_id_fields = ("parent_group",)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'organization', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Custom data'), {'fields': ('katakana_name', 'hiragana_name', 'avatar', 'bio',
                                       'organization', 'login_counter', 'registration_date')})
    )

    list_display = ('username', 'hiragana_name', 'katakana_name', 'email',
                    'is_superuser', 'organization', 'avatar')
    list_filter = ('is_active', "organization")
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")
    inlines = [
        UserGroupRoleInline,
    ]


@admin.register(PasswordReminderQuestions)
class PasswordReminderQuestionsAdmin(admin.ModelAdmin):
    list_display = ('organization', 'question')
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")


@admin.register(PasswordReminder)
class PasswordReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'question')
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('organization', 'name', 'role_type')
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")


@admin.register(UserGroupRole)
class UserGroupRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role')
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")


@admin.register(EmailReset)
class EmailResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'auth_code', 'uuid')
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")
