from __future__ import annotations

from unittest.mock import patch

import pytest

from recoco_sync.grist_connector.choices import GristColumnType
from recoco_sync.grist_connector.connectors import (
    GristConnector,
    check_table_columns_consistency,
    grist_table_exists,
)
from recoco_sync.main.utils import QuestionType

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
            "organization": "Commune de Bayonne",
            "created": "2023-10-10T09:50:32.182591+02:00",
            "modified": "2024-05-24T10:54:21.653995+02:00",
        }

    def test_map_from_survey_answer_payload_object(self, survey_answer_payload_object):
        assert GristConnector().map_from_survey_answer_payload_object(
            payload=survey_answer_payload_object,
            config=GristConfigFactory(create_columns=True),
        ) == {
            "thematiques": "Commerce rural,Participation à la vie locale,Patrimoine",
        }

    @pytest.mark.parametrize(
        "question_type,expected_grist_type",
        [
            (QuestionType.REGULAR, GristColumnType.TEXT),
            (QuestionType.YES_NO, GristColumnType.BOOL),
            (QuestionType.YES_NO_MAYBE, GristColumnType.TEXT),
            (QuestionType.MULTIPLE, GristColumnType.CHOICE_LIST),
        ],
    )
    def test_get_column_type_from_payload(self, question_type, expected_grist_type):
        with patch(
            "recoco_sync.grist_connector.connectors.get_question_type",
            return_value=question_type,
        ):
            assert GristConnector.get_column_type_from_payload(question_type) == expected_grist_type


def test_grist_table_exists():
    config = GristConfigFactory.build()
    with patch(
        "recoco_sync.grist_connector.connectors.GristApiClient.table_exists", return_value=True
    ) as mock_table_exists:
        assert grist_table_exists(config) is True
        mock_table_exists.assert_called_once_with(table_id=config.table_id)


@pytest.mark.django_db
def test_check_table_columns_consistency():
    config = GristConfigFactory(create_columns=True, doc_id="123456789", table_id="my_table")
    assert check_table_columns_consistency(config) is True

    GristColumnFactory(grist_config=config)
    assert check_table_columns_consistency(config) is False
