from __future__ import annotations

import pytest

from .factories import LesCommunsProjetFactory


@pytest.mark.parametrize(
    "recommendation_id,services,expected",
    [
        (None, [], False),
        (1, [], False),
        (None, [{"id": 1}, {"id": 2}], False),
        (1, [{"id": 1}, {"id": 2}], True),
        (1, {}, False),
        (1, {"id": 1}, True),
    ],
)
def test_les_communs_projet_is_service_ready(recommendation_id, services, expected):
    project = LesCommunsProjetFactory.build(recommendation_id=recommendation_id, services=services)
    assert project.is_service_ready is expected
