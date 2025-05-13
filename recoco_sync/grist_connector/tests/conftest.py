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
                    "type": "Int",
                    "label": "ID",
                },
            },
            {
                "id": "name",
                "fields": {
                    "type": "Text",
                    "label": "Nom du projet",
                },
            },
            {
                "id": "description",
                "fields": {
                    "type": "Text",
                    "label": "Description du projet",
                },
            },
            {
                "id": "tags",
                "fields": {
                    "type": "ChoiceList",
                    "label": "Etiquettes",
                },
            },
            {
                "id": "advisors_note",
                "fields": {
                    "type": "Text",
                    "label": "Note conseiller",
                },
            },
            {
                "id": "city",
                "fields": {
                    "type": "Text",
                    "label": "Commune",
                },
            },
            {
                "id": "postal_code",
                "fields": {
                    "type": "Text",
                    "label": "Code postal",
                },
            },
            {
                "id": "insee",
                "fields": {
                    "type": "Text",
                    "label": "Code Insee",
                },
            },
            {
                "id": "department",
                "fields": {
                    "type": "Text",
                    "label": "Département",
                },
            },
            {
                "id": "department_code",
                "fields": {
                    "type": "Text",
                    "label": "Code département",
                },
            },
            {
                "id": "region",
                "fields": {
                    "type": "Text",
                    "label": "Région",
                },
            },
            {
                "id": "region_code",
                "fields": {
                    "type": "Text",
                    "label": "Code région",
                },
            },
            {
                "id": "location",
                "fields": {
                    "type": "Text",
                    "label": "Lieu",
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
                "id": "organization",
                "fields": {
                    "label": "Organisation",
                    "type": "Text",
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
            {
                "id": "thematiques",
                "fields": {
                    "label": "Thématique(s)",
                    "type": "ChoiceList",
                },
            },
            {
                "id": "thematiques_comment",
                "fields": {
                    "label": "Commentaire de Thématique(s)",
                    "type": "Text",
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
                "id": "maturite_du_projet_comment",
                "fields": {
                    "label": "Commentaire de Maturité du projet",
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
