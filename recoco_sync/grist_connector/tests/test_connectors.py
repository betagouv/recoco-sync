from __future__ import annotations

import pytest
from grist_connector.connectors import GristConnector

from .factories import GristConfigFactory


@pytest.mark.django_db
class TestGristConnector:
    def test_map_from_project_payload_object(self, project_payload_object, default_columns):
        assert GristConnector().map_from_project_payload_object(
            payload=project_payload_object,
            config=GristConfigFactory(create_columns=True),
        ) == {
            "name": "Pôle Santé",
            "context": "Le projet consiste à créer un pôle santé",
            "city": "MONNIERES",
            "postal_code": 44690,
            "insee": 44100,
            "department": "Loire-Atlantique",
            "department_code": 44,
            "location": "rue des hirondelles",
            "tags": "tag1,tag2",
        }

    def test_map_from_survey_answer_payload_object(
        self, survey_answer_payload_object, default_columns
    ):
        assert GristConnector().map_from_survey_answer_payload_object(
            payload=survey_answer_payload_object,
            config=GristConfigFactory(create_columns=True),
        ) == {
            "topics": "Commerce rural,Citoyenneté / Participation de la population à la vie locale,"
            "Transition écologique et biodiversité,"
            "Transition énergétique",
            "topics_comment": "Mon commentaire sur les thématiques",
        }
