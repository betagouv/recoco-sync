from __future__ import annotations

from django.db import models

from recoco_sync.utils.models import BaseModel


class ProjetLesCommuns(BaseModel):
    les_communs_id = models.CharField(max_length=100)
    recoco_id = models.IntegerField()

    class Meta:
        verbose_name = "Projet Les Communs"
        verbose_name_plural = "Projets Les Communs"
        db_table = "projetlescommuns"
        ordering = ("-created",)
        unique_together = ("les_communs_id", "recoco_id")
