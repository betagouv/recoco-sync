from __future__ import annotations

import httpx
import pytest
from django.conf import settings


@pytest.fixture
def project_payload_object():
    return {
        "id": 777,
        "name": "Pôle Santé",
        "description": "Le projet consiste à créer un pôle santé",
        "status": "IN_PROGRESS",
        "inactive_since": None,
        "created_on": "2023-10-10T09:50:32.182591+02:00",
        "updated_on": "2024-05-24T10:54:21.653995+02:00",
        "org_name": "Conseil des Jedi",
        "switchtenders": [
            {
                "username": "anakin.skywalker@jedi.com",
                "first_name": "Anakin",
                "last_name": "Skywalker",
                "email": "anakin.skywalker@jedi.com",
                "profile": {
                    "organization": {"name": "pref44"},
                    "organization_position": "CHA",
                },
                "is_active": True,
            },
            {
                "username": "obiwan.kenobi@jedi.com",
                "first_name": "Obiwan",
                "last_name": "Kenobi",
                "email": "obiwan.kenobi@jedi.com",
                "profile": {
                    "organization": {"name": "PREFECTURE 44"},
                    "organization_position": "Chargé de projets",
                },
                "is_active": True,
            },
            {
                "username": "quigon.jinn@jedi.com",
                "first_name": "Qui-Gon",
                "last_name": "Jinn",
                "email": "quigon.jinn@jedi.com",
                "profile": {
                    "organization": {"name": "Préfecture 44"},
                    "organization_position": "Chef de bureau",
                },
                "is_active": True,
            },
        ],
        "commune": {
            "name": "MONNIERES",
            "insee": "44100",
            "postal": "44690",
            "department": {"name": "Loire-Atlantique", "code": "44"},
            "latitude": 47.1202035218,
            "longitude": -1.34924956417,
        },
        "location": "rue des hirondelles",
        "latitude": 47.1202035218,
        "longitude": -1.34924956417,
        "recommendation_count": 0,
        "public_message_count": 0,
        "private_message_count": 0,
        "topics": [
            {"name": "Financement"},
            {"name": "Etudes"},
        ],
        "tags": ["tag1", "tag2"],
    }


@pytest.fixture
def survey_answer_payload_object():
    return {
        "id": 12583,
        "created_on": "2023-11-03T09:48:55.478361+01:00",
        "updated_on": "2024-06-05T16:55:15.302646+02:00",
        "question": {
            "id": 85,
            "text": "Thématique(s)",
            "text_short": "Thématique(s)",
            "slug": "thematiques",
            "is_multiple": True,
            "choices": [
                {
                    "id": 258,
                    "value": "13",
                    "text": "Commerce rural",
                },
                {
                    "id": 247,
                    "value": "2",
                    "text": "Participation à la vie locale",
                },
                {"id": 249, "value": "4", "text": "Logement / Habitat"},
                {"id": 254, "value": "9", "text": "Patrimoine"},
                {"id": 303, "value": "15", "text": "Tourisme"},
                {"id": 306, "value": "17", "text": "Autre"},
            ],
        },
        "session": 806,
        "project": 831,
        "choices": [
            {"id": 258, "value": "13", "text": "Commerce rural"},
            {
                "id": 247,
                "value": "2",
                "text": "Participation à la vie locale",
            },
            {
                "id": 254,
                "value": "9",
                "text": "Patrimoine",
            },
        ],
        "comment": "Mon commentaire sur les thématiques",
        "attachment": None,
        "updated_by": {
            "username": "sifo.dyas@jedi.com",
            "first_name": "Sifo",
            "last_name": "Dyas",
            "email": "sifo.dyas@jedi.com",
            "profile": {"organization": None, "organization_position": None},
            "is_active": True,
        },
    }


@pytest.fixture
def questions_payload_object():
    return {
        "count": 18,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 85,
                "text": "Thématique(s)",
                "text_short": "Thématique(s)",
                "slug": "thematiques",
                "is_multiple": True,
                "choices": [
                    {"id": 258, "value": "13", "text": "Commerce rural"},
                    {
                        "id": 247,
                        "value": "2",
                        "text": "Participation à la vie locale",
                    },
                    {"id": 249, "value": "4", "text": "Logement / Habitat"},
                    {"id": 254, "value": "9", "text": "Patrimoine"},
                    {"id": 303, "value": "15", "text": "Tourisme"},
                    {"id": 306, "value": "17", "text": "Autre"},
                ],
            },
            {
                "id": 91,
                "text": "Budget prévisionnel",
                "text_short": "Budget prévisionnel",
                "slug": "budget-previsionnel",
                "is_multiple": False,
                "choices": [],
            },
            {
                "id": 120,
                "text": "Niveau de maturité du projet",
                "text_short": "Maturité du projet",
                "slug": "maturite-du-projet",
                "is_multiple": True,
                "choices": [
                    {"id": 299, "value": "Amorçage", "text": "Amorçage"},
                    {"id": 300, "value": "Diagnostic", "text": "Diagnostic"},
                    {"id": 302, "value": "Terminé", "text": "Terminé"},
                    {"id": 301, "value": "En cours", "text": "En cours"},
                ],
            },
        ],
    }


@pytest.fixture(autouse=True)
def mock_recoco_client_httpx_responses(respx_mock, questions_payload_object):
    respx_mock.post(f"{settings.RECOCO_API_URL_EXAMPLE}/token/").mock(
        return_value=httpx.Response(200, json={"access": "token"})
    )
    respx_mock.get(f"{settings.RECOCO_API_URL_EXAMPLE}/survey/questions/?limit=500").mock(
        return_value=httpx.Response(200, json=questions_payload_object)
    )
