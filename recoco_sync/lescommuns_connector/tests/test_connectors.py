from __future__ import annotations

import pytest

from recoco_sync.lescommuns_connector.connectors import LesCommunsConnector
from recoco_sync.main.choices import ObjectType
from recoco_sync.main.tests.factories import WebhookEventFactory

from .factories import LesCommunsProjectSelectionFactory


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
            "budgetPrevisionnel": None,
            "dateDebutPrevisionnelle": "2023-10-10",
            "porteur": {
                "codeSiret": None,
                "referentFonction": None,
                "referentEmail": "anakin.skywalker@jedi.com",
                "referentNom": None,
                "referentPrenom": None,
            },
            "competences": [],
            "leviers": [],
            "programme": None,
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

    def test_is_project_selection_enabled(self, settings):
        settings.LESCOMMUNS_PROJECT_SELECTION_ENABLED = False
        assert LesCommunsConnector()._is_project_selection_enabled(1) is True

        settings.LESCOMMUNS_PROJECT_SELECTION_ENABLED = True
        assert LesCommunsConnector()._is_project_selection_enabled(1) is False

        selection = LesCommunsProjectSelectionFactory(recoco_id=1, config__enabled=True)
        assert LesCommunsConnector()._is_project_selection_enabled(1) is True

        selection.config.enabled = False
        selection.config.save()
        assert LesCommunsConnector()._is_project_selection_enabled(1) is False

    def test_extract_project_id_from_event(self, settings):
        settings.LESCOMMUNS_RESOURCE_TAG_NAME = "lescommuns-test"

        connector = LesCommunsConnector()

        assert (
            connector._extract_project_id_from_event(
                1, ObjectType.PROJECT, WebhookEventFactory.build()
            )
            == 1
        )
        assert (
            connector._extract_project_id_from_event(
                2,
                ObjectType.RECOMMENDATION,
                WebhookEventFactory.build(
                    payload={"object": {"resource": {"tags": ["lescommuns-test"]}, "project": 1}}
                ),
            )
            == 1
        )
        assert (
            connector._extract_project_id_from_event(
                3,
                ObjectType.RECOMMENDATION,
                WebhookEventFactory.build(
                    payload={"object": {"resource": {"tags": ["other-tag"]}, "project": 1}}
                ),
            )
            is None
        )
        assert (
            connector._extract_project_id_from_event(
                4, ObjectType.SURVEY_ANSWER, WebhookEventFactory.build()
            )
            is None
        )
        assert (
            connector._extract_project_id_from_event(
                4, ObjectType.TAGGEDITEM, WebhookEventFactory.build()
            )
            is None
        )
