from __future__ import annotations

from django.contrib import admin

from .models import LesCommunsConfig, LesCommunsProjet


@admin.register(LesCommunsConfig)
class LesCommunsConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created",
        "enabled",
    )

    list_filter = ("created",)
    list_select_related = ("webhook_config",)


@admin.register(LesCommunsProjet)
class ProjetLesCommunsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lescommuns_id",
        "recoco_id",
        "created",
    )

    list_filter = ("created",)
    list_select_related = ("config",)
