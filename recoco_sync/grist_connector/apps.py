from __future__ import annotations

from django.apps import AppConfig


class GristConnectorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "grist_connector"
