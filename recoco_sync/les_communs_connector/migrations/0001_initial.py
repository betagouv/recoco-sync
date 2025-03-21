# Generated by Django 5.1.6 on 2025-03-21 14:59
from __future__ import annotations

import uuid

import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProjetLesCommuns",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("les_communs_id", models.CharField(max_length=100)),
                ("recoco_id", models.IntegerField()),
            ],
            options={
                "verbose_name": "Projet Les Communs",
                "verbose_name_plural": "Projets Les Communs",
                "db_table": "projetlescommuns",
                "ordering": ("-created",),
                "unique_together": {("les_communs_id", "recoco_id")},
            },
        ),
    ]
