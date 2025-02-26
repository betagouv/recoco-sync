from __future__ import annotations

from unittest.mock import patch

import pytest
from grist_connector.choices import GristColumnType
from grist_connector.connectors import (
    GristConnector,
    check_table_columns_consistency,
    grist_table_exists,
)

from .factories import GristColumnFactory, GristConfigFactory


@pytest.mark.django_db
class TestGristConnector:
    def test_map_from_project_payload_object(self, project_payload_object):
        assert GristConnector().map_from_project_payload_object(
            payload=project_payload_object,
            config=GristConfigFactory(create_columns=True),
        ) == {
            "name": "Pôle Santé",
            "description": "Le projet consiste à créer un pôle santé",
            "city": "MONNIERES",
            "postal_code": 44690,
            "insee": 44100,
            "department": "Loire-Atlantique",
            "department_code": 44,
            "location": "rue des hirondelles",
            "tags": "tag1,tag2",
        }

    def test_map_from_survey_answer_payload_object(self, survey_answer_payload_object):
        assert GristConnector().map_from_survey_answer_payload_object(
            payload=survey_answer_payload_object,
            config=GristConfigFactory(create_columns=True),
        ) == {
            "thematiques": "Commerce rural,Participation à la vie locale,Patrimoine",
        }

    @pytest.mark.parametrize(
        "question_payload,expected_type",
        [
            (
                {
                    "id": 6,
                    "text": "Quel est l’état général du bâti ?",
                    "text_short": "état_général_bati",
                    "slug": "etat_general_bati",
                    "is_multiple": False,
                    "choices": [
                        {
                            "id": 23,
                            "value": "bon_état",
                            "text": "Bon état général, pas de travaux structurels nécessaires",
                        },
                        {
                            "id": 24,
                            "value": "état_moyen",
                            "text": "Etat moyen, travaux importants à prévoir",
                        },
                    ],
                },
                GristColumnType.TEXT,
            ),
            (
                {
                    "id": 7,
                    "text": "Est-ce qu’un diagnostic bâtiments et infrastructures a été réalisé ?",
                    "text_short": "Diagnostic bâtimentaire",
                    "slug": "diagnostic-batimentaire",
                    "is_multiple": False,
                    "choices": [
                        {"id": 27, "value": "diag_oui", "text": "Oui"},
                        {"id": 28, "value": "diag_non", "text": "Non"},
                    ],
                },
                GristColumnType.BOOL,
            ),
            (
                {
                    "id": 85,
                    "text": "Thématique(s)",
                    "text_short": "Thématique(s)",
                    "slug": "thematiques-2",
                    "is_multiple": True,
                    "choices": [
                        {"id": 258, "value": "13", "text": "Commerce rural"},
                        {
                            "id": 247,
                            "value": "2",
                            "text": "Citoyenneté / Participation de la population à la vie locale",
                        },
                        {"id": 249, "value": "4", "text": "Logement / Habitat"},
                    ],
                },
                GristColumnType.CHOICE_LIST,
            ),
        ],
    )
    def test_get_column_type_from_payload(self, question_payload, expected_type):
        assert GristConnector.get_column_type_from_payload(question_payload) == expected_type


def test_grist_table_exists():
    config = GristConfigFactory.build()
    with patch(
        "grist_connector.connectors.GristApiClient.table_exists", return_value=True
    ) as mock_table_exists:
        assert grist_table_exists(config) is True
        mock_table_exists.assert_called_once_with(table_id=config.table_id)


@pytest.mark.django_db
def test_check_table_columns_consistency():
    config = GristConfigFactory(create_columns=True, doc_id="123456789", table_id="my_table")
    assert check_table_columns_consistency(config) is True

    GristColumnFactory(grist_config=config)
    assert check_table_columns_consistency(config) is False
