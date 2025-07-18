# Generated by Django 5.1.6 on 2025-07-01 07:40
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lescommuns_connector", "0002_lescommunsconfig_api_key_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="lescommunsprojet",
            name="services",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Services associés au projet dans LesCommuns",
                verbose_name="Services LesCommuns",
            ),
        ),
    ]
