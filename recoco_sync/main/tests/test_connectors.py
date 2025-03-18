from __future__ import annotations

from recoco_sync.main.connectors import Connector


class ConnectorStub(Connector):
    def update_project(self, project_id, event):
        pass


class TestConnector:
    def test_map_from_project_payload_object(self, project_payload_object):
        assert ConnectorStub().map_from_project_payload_object(payload=project_payload_object) == {
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

    def test_map_survey_answer_payload_object(self, survey_answer_payload_object):
        assert ConnectorStub().map_from_survey_answer_payload_object(
            payload=survey_answer_payload_object
        ) == {
            "thematiques": "Commerce rural,Participation à la vie locale,Patrimoine",
            "thematiques_comment": "Mon commentaire sur les thématiques",
        }
