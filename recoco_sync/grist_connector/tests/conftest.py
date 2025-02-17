from __future__ import annotations

import pytest
from grist_connector.connectors import GristConnector

from .factories import GristConfigFactory


@pytest.mark.django_db
@pytest.fixture
def default_columns():
    GristConnector().update_or_create_columns(config=GristConfigFactory())
    yield
