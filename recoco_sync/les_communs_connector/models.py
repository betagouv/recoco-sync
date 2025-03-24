from __future__ import annotations

from django.db import models

from recoco_sync.main.models import WebhookConfig
from recoco_sync.utils.models import BaseModel


class LesCommunsConfig(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Nom de la configuration")

    webhook_config = models.ForeignKey(
        WebhookConfig,
        on_delete=models.CASCADE,
        related_name="les_communs_configs",
    )

    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuration Les Communs"
        verbose_name_plural = "Configurations Les Communs"
        db_table = "lescommunsconfig"
        ordering = ("-created",)
        indexes = [
            models.Index(fields=["enabled"]),
        ]


class LesCommunsProjet(BaseModel):
    les_communs_id = models.CharField(max_length=100)
    recoco_id = models.IntegerField()

    config = models.ForeignKey(LesCommunsConfig, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Projet Les Communs"
        verbose_name_plural = "Projets Les Communs"
        db_table = "lescommunsprojet"
        ordering = ("-created",)
        unique_together = ("config", "les_communs_id", "recoco_id")
