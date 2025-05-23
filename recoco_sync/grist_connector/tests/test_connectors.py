from __future__ import annotations

from unittest.mock import patch

import pytest

from recoco_sync.grist_connector.choices import GristColumnType
from recoco_sync.grist_connector.connectors import GristConnector
from recoco_sync.main.utils import QuestionType

from .factories import GristConfigFactory


@pytest.mark.django_db
class TestGristConnector:
    def test_map_from_project_payload_object(self, project_payload_object):
        data = GristConnector().map_from_project_payload_object(
            payload=project_payload_object,
            config=GristConfigFactory(create_columns=True),
        )
        assert data == {
            "name": "Pôle Santé",
            "description": "Le projet consiste à créer un pôle santé",
            "city": "MONNIERES",
            "postal_code": "44690",
            "insee": "44100",
            "department": "Loire-Atlantique",
            "department_code": "44",
            "region": "Pays de la Loire",
            "region_code": "52",
            "location": "rue des hirondelles",
            "latitude": 47.1202035218,
            "longitude": -1.34924956417,
            "tags": "tag1,tag2",
            "organization": "Conseil des Jedi",
            "created": "2023-10-10T09:50:32.182591+02:00",
            "modified": "2024-05-24T10:54:21.653995+02:00",
            "inactive_since": None,
            "active": True,
            "status": "IN_PROGRESS",
            "advisors_note": "Note conseiller",
        }, data

    def test_map_from_survey_answer_payload_object(self, survey_answer_payload_object):
        assert GristConnector().map_from_survey_answer_payload_object(
            payload=survey_answer_payload_object,
            config=GristConfigFactory(create_columns=True),
        ) == {
            "thematiques": "Commerce rural,Participation à la vie locale,Patrimoine",
            "thematiques_comment": "Mon commentaire sur les thématiques",
        }

    @pytest.mark.parametrize(
        "question_type,expected_grist_type",
        [
            (QuestionType.SIMPLE, GristColumnType.TEXT),
            (QuestionType.YES_NO, GristColumnType.BOOL),
            (QuestionType.YES_NO_MAYBE, GristColumnType.TEXT),
            (QuestionType.CHOICES, GristColumnType.TEXT),
            (QuestionType.MULTIPLE_CHOICES, GristColumnType.CHOICE_LIST),
        ],
    )
    def test_get_column_type_from_payload(self, question_type, expected_grist_type):
        with patch(
            "recoco_sync.grist_connector.connectors.get_question_type",
            return_value=question_type,
        ):
            assert GristConnector.get_column_type_from_payload(question_type) == expected_grist_type
