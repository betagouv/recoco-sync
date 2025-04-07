from __future__ import annotations

import httpx
import pytest
from django.conf import settings


@pytest.fixture
def grist_table_columns():
    return {
        "columns": [
            {
                "id": "object_id",
                "fields": {
                    "colRef": 411,
                    "parentId": 16,
                    "parentPos": 411,
                    "type": "Int",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "ID",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "name",
                "fields": {
                    "colRef": 412,
                    "parentId": 16,
                    "parentPos": 412,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Nom du projet",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "description",
                "fields": {
                    "colRef": 413,
                    "parentId": 16,
                    "parentPos": 413,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Description du projet",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "tags",
                "fields": {
                    "colRef": 414,
                    "parentId": 16,
                    "parentPos": 414,
                    "type": "ChoiceList",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Etiquettes",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "topics",
                "fields": {
                    "colRef": 415,
                    "parentId": 16,
                    "parentPos": 415,
                    "type": "ChoiceList",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Th\u00e9matiques",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "topics_comment",
                "fields": {
                    "colRef": 416,
                    "parentId": 16,
                    "parentPos": 416,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Commentaire th\u00e9matiques",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "city",
                "fields": {
                    "colRef": 417,
                    "parentId": 16,
                    "parentPos": 417,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Commune",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "postal_code",
                "fields": {
                    "colRef": 418,
                    "parentId": 16,
                    "parentPos": 418,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Code postal",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "insee",
                "fields": {
                    "colRef": 419,
                    "parentId": 16,
                    "parentPos": 419,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Code Insee",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "department",
                "fields": {
                    "colRef": 420,
                    "parentId": 16,
                    "parentPos": 420,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "D\u00e9partement",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "department_code",
                "fields": {
                    "colRef": 421,
                    "parentId": 16,
                    "parentPos": 421,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Code d\u00e9partement",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "location",
                "fields": {
                    "colRef": 422,
                    "parentId": 16,
                    "parentPos": 422,
                    "type": "Text",
                    "widgetOptions": "",
                    "isFormula": False,
                    "formula": "",
                    "label": "Lieu",
                    "description": "",
                    "untieColIdFromLabel": False,
                    "summarySourceCol": 0,
                    "displayCol": 0,
                    "visibleCol": 0,
                    "rules": None,
                    "recalcWhen": 0,
                    "recalcDeps": None,
                },
            },
            {
                "id": "thematiques",
                "fields": {
                    "label": "Thématique(s)",
                    "type": "ChoiceList",
                },
            },
            {
                "id": "budget_previsionnel",
                "fields": {
                    "label": "Budget prévisionnel",
                    "type": "Text",
                },
            },
            {
                "id": "maturite_du_projet",
                "fields": {
                    "label": "Maturité du projet",
                    "type": "ChoiceList",
                },
            },
            {
                "id": "created",
                "fields": {
                    "label": "Créé le",
                    "type": "DateTime:Europe/Amsterdam",
                },
            },
            {
                "id": "modified",
                "fields": {
                    "label": "Modifié le",
                    "type": "DateTime:Europe/Amsterdam",
                },
            },
            {
                "id": "organization",
                "fields": {
                    "label": "Organisation",
                    "type": "Text",
                },
            },
            {
                "id": "latitude",
                "fields": {
                    "label": "Latitude",
                    "type": "Numeric",
                },
            },
            {
                "id": "longitude",
                "fields": {
                    "label": "Longitude",
                    "type": "Numeric",
                },
            },
            {
                "id": "inactive_since",
                "fields": {
                    "label": "Inactif depuis le",
                    "type": "DateTime:Europe/Amsterdam",
                },
            },
            {
                "id": "active",
                "fields": {
                    "label": "Actif",
                    "type": "Bool",
                },
            },
            {
                "id": "status",
                "fields": {
                    "label": "Statut",
                    "type": "Text",
                },
            },
        ]
    }


@pytest.fixture(autouse=True)
def mock_grist_client_httpx_responses(respx_mock, grist_table_columns):
    respx_mock.get(
        f"{settings.GRIST_API_URL_EXAMPLE}/docs/123456789/tables/my_table/columns/"
    ).mock(return_value=httpx.Response(200, json=grist_table_columns))
