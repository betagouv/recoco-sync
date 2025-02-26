from __future__ import annotations

import pytest
from grist_connector.connectors import GristConnector

from .factories import GristConfigFactory


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
