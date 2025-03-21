from __future__ import annotations

from django.contrib import admin

from .models import ProjetLesCommuns


@admin.register(ProjetLesCommuns)
class ProjetLesCommunsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "les_communs_id",
        "recoco_id",
        "created",
    )

    list_filter = ("created",)
