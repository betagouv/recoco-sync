from __future__ import annotations

from unittest.mock import patch

import pytest
from grist_connector.connectors import GristConnector

from .factories import GristConfigFactory


@pytest.mark.django_db
@pytest.fixture
def default_columns(questions_payload_object):
    with patch("recoco_sync.main.clients.RecocoApiClient.get_questions") as mock_get_questions:
        mock_get_questions.return_value = questions_payload_object
        GristConnector().update_or_create_columns(config=GristConfigFactory())
        yield
