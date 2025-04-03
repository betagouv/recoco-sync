from __future__ import annotations

import pytest

from recoco_sync.lescommuns_connector.connectors import LesCommunsConnector


@pytest.mark.django_db
class TestLesCommunsConnector:
    def test_map_from_project_payload_object(self, project_payload_object):
        data = LesCommunsConnector().map_from_project_payload_object(payload=project_payload_object)

        assert data == {
            "nom": "Pôle Santé",
            "description": "Le projet consiste à créer un pôle santé",
            "collectivites": [
                {"code": "44100", "type": "Commune"},
            ],
            "externalId": "777",
            "phase": "Idée",
            "phaseStatut": "En cours",
            "dateDebutPrevisionnelle": "2023-10-10",
            "porteur": {
                "referentEmail": "anakin.skywalker@jedi.com",
                "referentNom": None,
                "referentPrenom": None,
            },
            "competences": [],
            "leviers": [],
        }

    def test_map_from_survey_answer_payload_object(self, survey_answer_payload_object):
        assert (
            LesCommunsConnector().map_from_survey_answer_payload_object(
                payload=survey_answer_payload_object,
            )
            == {}
        )

    def test_phase_mapping(self):
        assert LesCommunsConnector.phase_mapping(None) == "Idée"
        assert LesCommunsConnector.phase_mapping("DRAFT") == "Idée"
        assert LesCommunsConnector.phase_mapping("TO_PROCESS") == "Idée"
        assert LesCommunsConnector.phase_mapping("READY") == "Idée"
        assert LesCommunsConnector.phase_mapping("IN_PROGRESS") == "Idée"
        assert LesCommunsConnector.phase_mapping("DONE") == "Idée"
        assert LesCommunsConnector.phase_mapping("STUCK") == "Idée"
        assert LesCommunsConnector.phase_mapping("REJECTED") == "Idée"

    def test_phase_statut_mapping(self):
        assert LesCommunsConnector.phase_statut_mapping(None) == "En cours"
        assert LesCommunsConnector.phase_statut_mapping("DRAFT") == "En cours"
        assert LesCommunsConnector.phase_statut_mapping("TO_PROCESS") == "En cours"
        assert LesCommunsConnector.phase_statut_mapping("READY") == "En cours"
        assert LesCommunsConnector.phase_statut_mapping("IN_PROGRESS") == "En cours"
        assert LesCommunsConnector.phase_statut_mapping("DONE") == "Terminé"
        assert LesCommunsConnector.phase_statut_mapping("STUCK") == "Bloqué"
        assert LesCommunsConnector.phase_statut_mapping("REJECTED") == "Abandonné"
