# Generated by Django 5.1.6 on 2025-02-26 13:20
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("grist_connector", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="gristcolumn",
            options={
                "ordering": ("created", "col_id"),
                "verbose_name": "Grist column",
                "verbose_name_plural": "Grist columns",
            },
        ),
    ]
