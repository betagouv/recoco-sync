from __future__ import annotations

from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        from .connectors import auto_discover_connectors

        auto_discover_connectors()
