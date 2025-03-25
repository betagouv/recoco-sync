from __future__ import annotations

from unittest.mock import patch

import pytest

from recoco_sync.grist_connector.admin import GristConfigAdmin
from recoco_sync.grist_connector.models import GristConfig

from .factories import GristColumnFactory, GristConfigFactory


@pytest.fixture
def grist_config_admin():
    return GristConfigAdmin(model=GristConfig, admin_site=None)


def test_grist_table_exists(grist_config_admin):
    config = GristConfigFactory.build()
    with patch(
        "recoco_sync.grist_connector.connectors.GristApiClient.table_exists",
        return_value=True,
    ) as mock_table_exists:
        assert grist_config_admin._grist_table_exists(config) is True
        mock_table_exists.assert_called_once_with(table_id=config.table_id)


@pytest.mark.django_db
def test_check_table_columns_consistency(grist_config_admin):
    config = GristConfigFactory(create_columns=True, doc_id="123456789", table_id="my_table")
    assert grist_config_admin._check_table_columns_consistency(config) is True

    GristColumnFactory(grist_config=config)
    assert grist_config_admin._check_table_columns_consistency(config) is False
