from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import LesCommunsConfig, LesCommunsProjectSelection, LesCommunsProjet
from .tasks import load_lescommuns_services


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
class LesCommunsProjetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lescommuns_id",
        "recoco_id",
        "created",
    )

    list_filter = ("created",)
    list_select_related = ("config",)

    actions = [
        "load_project_services",
    ]

    @admin.action(description="Charger les services du projet")
    def load_project_services(self, request: HttpRequest, queryset: QuerySet[LesCommunsProjet]):
        for project in queryset:
            load_lescommuns_services.delay(project_id=project.id)


@admin.register(LesCommunsProjectSelection)
class LesCommunsProjectSelectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recoco_id",
        "config",
    )

    list_filter = ("created",)
    list_select_related = ("config",)
