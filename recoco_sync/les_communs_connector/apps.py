from __future__ import annotations

from django.apps import AppConfig


class LesCommunsConnectorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco_sync.les_communs_connector"
