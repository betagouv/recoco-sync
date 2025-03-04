from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User, WebhookConfig, WebhookEvent

admin.site.unregister(Group)


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "api_url",
        "enabled",
    )

    list_filter = (
        "enabled",
        "created",
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "webhook_uuid",
        "topic",
        "object_id",
        "object_type",
        "status",
        "created",
    )

    list_filter = (
        "topic",
        "object_type",
        "status",
    )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    )
    fieldsets = (
        (_("Security"), {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
