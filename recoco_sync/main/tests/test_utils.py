from __future__ import annotations

import pytest

from recoco_sync.main.utils import QuestionType, get_question_type


@pytest.mark.parametrize(
    "question_payload,expected_question_type",
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
            QuestionType.CHOICES,
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
            QuestionType.YES_NO,
        ),
        (
            {
                "id": 231,
                "text": "Votre commune fait partie d'un EPCI ?",
                "text_short": "Compétence voirie de l'EPCI",
                "slug": "competence-voirie-de-lepci",
                "is_multiple": False,
                "choices": [
                    {"id": 548, "value": "EPCI compétence voirie", "text": "Oui"},
                    {"id": 549, "value": "Pas voirie EPCI", "text": "Non"},
                    {
                        "id": 550,
                        "value": "Compétence voirie inconnue",
                        "text": "Je ne sais pas",
                    },
                ],
            },
            QuestionType.YES_NO_MAYBE,
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
            QuestionType.MULTIPLE_CHOICES,
        ),
        (
            {
                "id": 13,
                "text": "Description succincte du site",
                "text_short": "Description du site",
                "slug": "description-du-site",
                "is_multiple": False,
                "choices": [],
            },
            QuestionType.SIMPLE,
        ),
    ],
)
def test_get_column_type_from_payload(question_payload, expected_question_type):
    assert get_question_type(question_payload) == expected_question_type
