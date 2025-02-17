from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.functional import cached_property
from main.models import WebhookConfig

from recoco_sync.utils.models import BaseModel

from .choices import GristColumnType


class GristConfig(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Nom de la configuration")

    doc_id = models.CharField(max_length=32)
    table_id = models.CharField(max_length=32)

    enabled = models.BooleanField(default=True)

    api_url = models.CharField(max_length=128)
    api_key = models.CharField(max_length=64)

    webhook_config = models.ForeignKey(
        WebhookConfig,
        on_delete=models.CASCADE,
        related_name="grist_configs",
    )

    class Meta:
        db_table = "gristconfig"
        ordering = ("-created",)
        verbose_name = "Configuration Grist"
        verbose_name_plural = "Configurations Grist"
        indexes = [
            models.Index(fields=["enabled"]),
        ]

    @cached_property
    def table_columns(self) -> list[dict[str, Any]]:
        return [
            {
                "id": column.col_id,
                "fields": {
                    "label": column.label,
                    "type": GristColumnType(column.type).label,
                },
            }
            for column in self.columns.order_by("created")
        ]

    @cached_property
    def table_headers(self) -> list[str]:
        return list(self.columns.order_by("created").values_list("col_id", flat=True))

    def __str__(self) -> str:
        return self.name or self.doc_id


class GristColumn(BaseModel):
    col_id = models.CharField(max_length=64)

    grist_config = models.ForeignKey(
        GristConfig,
        on_delete=models.CASCADE,
        related_name="columns",
    )

    label = models.CharField(max_length=128)

    type = models.CharField(
        max_length=32,
        choices=GristColumnType.choices,
        default=GristColumnType.TEXT,
    )

    class Meta:
        db_table = "gristcolumn"
        ordering = ("col_id",)  # TODO: change default order ro "created"
        verbose_name = "Grist column"
        verbose_name_plural = "Grist columns"
        unique_together = [
            ("col_id", "grist_config"),
        ]
        indexes = [
            models.Index(fields=["type"]),
        ]

    def __str__(self) -> str:
        return self.label
