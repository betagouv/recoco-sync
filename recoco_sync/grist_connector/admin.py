from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from httpx import HTTPStatusError

from .connectors import (
    GristConnector,
    check_table_columns_consistency,
    grist_table_exists,
)
from .models import (
    GristColumn,
    GristConfig,
)
from .tasks import populate_grist_table, refresh_grist_table


@admin.register(GristColumn)
class GristColumnAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "col_id",
        "label",
        "type",
        "grist_config",
    )
    search_fields = (
        "col_id",
        "label",
    )
    list_filter = (
        "type",
        "grist_config__name",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("grist_config")
            .order_by("grist_config__name", "created")
        )


class GristConfigColumnInline(admin.TabularInline):
    model = GristColumn
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("created")


@admin.register(GristConfig)
class GristConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "api_url",
        "enabled",
    )

    list_filter = ("enabled",)

    actions = (
        "setup_grist_table",
        "reset_columns",
    )

    inlines = (GristConfigColumnInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("webhook_config")
            .prefetch_related("columns")
        )

    @admin.action(
        description="Créer ou mettre à jour la table Grist des configurations sélectionnées"
    )
    def setup_grist_table(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            self._setup_grist_table_from_config(request, config)

    def _setup_grist_table_from_config(self, request: HttpRequest, config: GristConfig):
        if not config.enabled:
            self.message_user(
                request,
                f"Configuration {config}: inactive.",
                messages.ERROR,
            )
            return

        try:
            table_exists = grist_table_exists(config)
        except HTTPStatusError as err:
            if err.response.status_code == 404:
                self.message_user(
                    request,
                    f"Configuration {config}: le document {config.doc_id} n'existe pas.",
                    messages.ERROR,
                )
                return
            raise err

        if not table_exists:
            res = populate_grist_table.delay(config.id)
            self.message_user(
                request,
                f"Configuration {config}: une tâche de création a été lancée (task ID: {res.id}).",
                messages.SUCCESS,
            )
            return

        if not check_table_columns_consistency(config):
            self.message_user(
                request,
                f"Configuration {config}: les colonnes ne sont pas cohérentes. "
                f"Impossible de mettre à jour la table {config.table_id}.",
                messages.ERROR,
            )
            return

        res = refresh_grist_table.delay(config.id)
        self.message_user(
            request,
            f"Configuration {config}: une tâche de mise à jour a été lancée (task ID: {res.id}).",
            messages.SUCCESS,
        )

    @admin.action(description="Recréer les colonnes pour les configurations sélectionnées")
    def reset_columns(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            GristConnector().update_or_create_columns(config=config)
            self.message_user(
                request,
                f"Configuration {config.id}: reset columns.",
                messages.SUCCESS,
            )
