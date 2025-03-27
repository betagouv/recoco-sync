# Generated by Django 5.1.6 on 2025-03-27 13:44
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("les_communs_connector", "0002_lescommunsconfig_lescommunsprojet_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="lescommunsconfig",
            options={
                "ordering": ("-created",),
                "verbose_name": "Configuration LesCommuns",
                "verbose_name_plural": "Configurations LesCommuns",
            },
        ),
        migrations.AlterModelOptions(
            name="lescommunsprojet",
            options={
                "ordering": ("-created",),
                "verbose_name": "Projet LesCommuns",
                "verbose_name_plural": "Projets LesCommuns",
            },
        ),
    ]
