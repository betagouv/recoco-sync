from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from .clients import GristApiClient
from .connectors import GristConnector
from .models import GristColumn, GristConfig, GristReference
from .tasks import populate_grist_table, refresh_grist_table, sync_grist_references


@admin.register(GristReference)
class GristReferenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "doc_id",
        "table_id",
        "api_url",
    )
    search_fields = (
        "name",
        "doc_id",
        "table_id",
    )


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
        "related_webhook_config",
        "enabled",
    )

    list_filter = ("enabled",)

    actions = [
        "reset_columns",
        "sync_columns",
        "setup_grist_table",
        "sync_references",
    ]

    inlines = (GristConfigColumnInline,)

    list_select_related = ("webhook_config",)

    @admin.display(description="Webhook config")
    def related_webhook_config(self, obj: GristConfig) -> str | None:
        return format_html(
            "<a href='{}'>{}</a>",
            reverse("admin:main_webhookconfig_change", args=[obj.webhook_config.pk]),
            obj.webhook_config.code,
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("webhook_config")
            .prefetch_related("columns")
        )

    def _check_config_is_enabled(self, request: HttpRequest, config: GristConfig) -> bool:
        if not config.enabled:
            self.message_user(request, f"Configuration {config}: inactive.", messages.ERROR)
            return False
        return True

    def _grist_table_exists(self, config: GristConfig) -> bool:
        return GristApiClient.from_config(config).table_exists(table_id=config.table_id)

    @staticmethod
    def _check_table_columns_consistency(config: GristConfig) -> bool:
        config_table_columns = {t["id"]: t["fields"]["type"] for t in config.table_columns}

        remote_table_columns = {
            t["id"]: t["fields"]["type"]
            for t in GristApiClient.from_config(config).get_table_columns(table_id=config.table_id)
            if t["id"] in config_table_columns.keys()
        }

        return config_table_columns == remote_table_columns

    @admin.action(description="Mettre à jour la table Grist")
    def setup_grist_table(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            if not self._check_config_is_enabled(request, config):
                continue

            table_exists = self._grist_table_exists(config)
            if not table_exists:
                res = populate_grist_table.delay(config.id)
                self.message_user(
                    request,
                    f"Configuration {config}: une tâche de création a été lancée "
                    f"(task ID: {res.id}).",
                    messages.SUCCESS,
                )
                continue

            if not self._check_table_columns_consistency(config):
                self.message_user(
                    request,
                    f"Configuration {config}: les colonnes ne sont pas synchronisées."
                    f"Impossible de mettre à jour la table {config.table_id}.",
                    messages.ERROR,
                )
                continue

            res = refresh_grist_table.delay(config.id)
            self.message_user(
                request,
                f"Configuration {config}: une tâche de mise à jour a été lancée "
                f"(task ID: {res.id}).",
                messages.SUCCESS,
            )

    @admin.action(description="Mettre à jour les référentiels")
    def sync_references(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            if not self._check_config_is_enabled(request, config):
                continue

        res = sync_grist_references.delay(config.id)
        self.message_user(
            request,
            f"Configuration {config}: une tâche de mise à jour des référentiels a été lancée "
            f"(task ID: {res.id}).",
            messages.SUCCESS,
        )

    @admin.action(description="Recréer les colonnes en base de données")
    def reset_columns(self, request: HttpRequest, queryset: QuerySet[GristConfig]):
        for config in queryset:
            if not self._check_config_is_enabled(request, config):
                continue

            GristConnector().update_or_create_columns(config=config)
            self.message_user(
                request,
                f"Configuration {config.name}: les colonnes ont été re-créées.",
                messages.SUCCESS,
            )

    @admin.action(description="Synchroniser les colonnes de la table Grist")
    def sync_columns(  # noqa: C901
        self, request: HttpRequest, queryset: QuerySet[GristConfig]
    ):
        for config in queryset:
            if not self._check_config_is_enabled(request, config):
                continue

            if not self._grist_table_exists(config):
                self.message_user(
                    request,
                    f"Action sur la configuration {config.name}: la table grist n'existe pas.",
                    messages.ERROR,
                )
                continue

            grist_client: GristApiClient = GristApiClient.from_config(config)

            indexed_remote_table_columns = {
                col["id"]: col for col in grist_client.get_table_columns(table_id=config.table_id)
            }

            for column in config.table_columns:
                col_id = column["id"]
                remote_column = indexed_remote_table_columns.get(col_id)

                # find out all columns that are in the config but not in Grist
                if not remote_column:
                    self.message_user(
                        request,
                        f"Configuration {config.name}: création de la colonne '{col_id}'.",
                        messages.SUCCESS,
                    )
                    grist_client.create_table_columns(
                        table_id=config.table_id,
                        columns=[
                            {
                                "id": col_id,
                                "fields": {
                                    "label": column["fields"]["label"],
                                    "type": column["fields"]["type"],
                                },
                            }
                        ],
                    )
                    continue

                # find out all columns that are in both sides but with diffs
                if remote_column["fields"]["type"] != column["fields"]["type"]:
                    self.message_user(
                        request,
                        f"Configuration {config.name}: mise à jour de la colonne '{col_id}'.",
                        messages.SUCCESS,
                    )
                    grist_client.update_table_columns(
                        table_id=config.table_id,
                        columns=[
                            {
                                "id": col_id,
                                "fields": {
                                    "type": column["fields"]["type"],
                                    "colId": col_id,
                                },
                            }
                        ],
                    )
                    continue

            # find out all columns that are in Grist but not in the config
            config_columns_ids = [col["id"] for col in config.table_columns]
            for remote_col_id in indexed_remote_table_columns.keys():
                if remote_col_id not in config_columns_ids:
                    self.message_user(
                        request,
                        f"Action sur la configuration {config.name}: la colonne '{remote_col_id}' "
                        "existe uniquement côté Grist.",
                        messages.WARNING,
                    )

            # find out all columns that have been renamed
            for column in config.table_columns:
                col_id = column["id"]
                column_label = column["fields"]["label"]
                remote_column_label = indexed_remote_table_columns[col_id]["fields"]["label"]
                if remote_column_label != column_label:
                    self.message_user(
                        request,
                        f"Configuration {config.name}: la colonne '{col_id}' a été renommée "
                        f"'{column_label}' => '{remote_column_label}'.",
                        messages.WARNING,
                    )
