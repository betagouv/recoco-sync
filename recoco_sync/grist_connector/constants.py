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
        "label": "Descritpion du projet",
        "type": GristColumnType.TEXT,
    },
    "tags": {
        "label": "Etiquettes",
        "type": GristColumnType.CHOICE_LIST,
    },
    "topics": {
        "label": "Thématiques",
        "type": GristColumnType.CHOICE_LIST,
    },
    "topics_comment": {
        "label": "Commentaire thématiques",
        "type": GristColumnType.TEXT,
    },
    "city": {
        "label": "Commune",
        "type": GristColumnType.TEXT,
    },
    "postal_code": {
        "label": "Code postal",
        "type": GristColumnType.INTEGER,
    },
    "insee": {
        "label": "Code Insee",
        "type": GristColumnType.INTEGER,
    },
    "department": {
        "label": "Département",
        "type": GristColumnType.TEXT,
    },
    "department_code": {
        "label": "Code département",
        "type": GristColumnType.INTEGER,
    },
    "location": {
        "label": "Lieu",
        "type": GristColumnType.TEXT,
    },
}
