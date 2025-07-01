from __future__ import annotations

from django.db import models

from recoco_sync.main.models import WebhookConfig
from recoco_sync.utils.models import BaseModel


class LesCommunsConfig(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Nom de la configuration")

    webhook_config = models.ForeignKey(
        WebhookConfig,
        on_delete=models.CASCADE,
        related_name="lescommuns_configs",
    )

    api_key = models.CharField(max_length=64)

    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuration LesCommuns"
        verbose_name_plural = "Configurations LesCommuns"
        db_table = "lescommunsconfig"
        ordering = ("-created",)
        indexes = [
            models.Index(fields=["enabled"]),
        ]

    def __str__(self):
        return self.name


class LesCommunsProjet(BaseModel):
    lescommuns_id = models.CharField(max_length=100)
    recoco_id = models.IntegerField()

    config = models.ForeignKey(
        LesCommunsConfig, on_delete=models.CASCADE, related_name="lescommuns_projects"
    )

    services = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Services LesCommuns",
        help_text="Services associés au projet dans LesCommuns",
    )

    recommendation_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID de la recommandation",
        help_text="ID de la recommandation associée dans Recoco",
    )

    class Meta:
        verbose_name = "Projet LesCommuns"
        verbose_name_plural = "Projets LesCommuns"
        db_table = "lescommunsprojet"
        ordering = ("-created",)
        unique_together = ("config", "lescommuns_id", "recoco_id")

    @property
    def is_service_ready(self) -> bool:
        return self.recommendation_id is not None and len(self.services)


class LesCommunsProjectSelection(BaseModel):
    recoco_id = models.IntegerField()

    config = models.ForeignKey(
        LesCommunsConfig,
        on_delete=models.CASCADE,
        related_name="lescommuns_project_selections",
    )

    class Meta:
        verbose_name = "Sélection de projet pour LesCommuns"
        verbose_name_plural = "Sélections de projet pour LesCommuns"
        db_table = "lescommunsprojectselection"
        ordering = ("-created",)
        unique_together = ("config", "recoco_id")
