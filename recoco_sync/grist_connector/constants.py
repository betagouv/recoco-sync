from __future__ import annotations

from .choices import GristColumnType

project_columns_spec = {
    "object_id": {
        "label": "ID",
        "type": GristColumnType.INTEGER,
    },
    "name": {
        "label": "Nom du projet",
        "type": GristColumnType.TEXT,
    },
    "description": {
        "label": "Description du projet",
        "type": GristColumnType.TEXT,
    },
    "tags": {
        "label": "Etiquettes",
        "type": GristColumnType.CHOICE_LIST,
    },
    "city": {
        "label": "Commune",
        "type": GristColumnType.TEXT,
    },
    "postal_code": {
        "label": "Code postal",
        "type": GristColumnType.TEXT,
    },
    "insee": {
        "label": "Code Insee",
        "type": GristColumnType.TEXT,
    },
    "department": {
        "label": "Département",
        "type": GristColumnType.TEXT,
    },
    "department_code": {
        "label": "Code département",
        "type": GristColumnType.TEXT,
    },
    "region": {
        "label": "Région",
        "type": GristColumnType.TEXT,
    },
    "region_code": {
        "label": "Code région",
        "type": GristColumnType.TEXT,
    },
    "location": {
        "label": "Lieu",
        "type": GristColumnType.TEXT,
    },
    "latitude": {
        "label": "Latitude",
        "type": GristColumnType.NUMERIC,
    },
    "longitude": {
        "label": "Longitude",
        "type": GristColumnType.NUMERIC,
    },
    "organization": {
        "label": "Organisation",
        "type": GristColumnType.TEXT,
    },
    "created": {
        "label": "Créé le",
        "type": GristColumnType.DATETIME,
    },
    "modified": {
        "label": "Modifié le",
        "type": GristColumnType.DATETIME,
    },
    "inactive_since": {
        "label": "Inactif depuis le",
        "type": GristColumnType.DATETIME,
    },
    "active": {
        "label": "Actif",
        "type": GristColumnType.BOOL,
    },
    "status": {
        "label": "Statut",
        "type": GristColumnType.TEXT,
    },
    "advisors_note": {
        "label": "Note des conseillers",
        "type": GristColumnType.TEXT,
    },
}
