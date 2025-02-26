from __future__ import annotations

from unittest.mock import patch

import pytest
from grist_connector.connectors import check_table_columns_consistency, grist_table_exists

from .factories import GristColumnFactory, GristConfigFactory


def test_grist_table_exists():
    config = GristConfigFactory.build()
    with patch(
        "grist_connector.connectors.GristApiClient.table_exists", return_value=True
    ) as mock_table_exists:
        assert grist_table_exists(config) is True
        mock_table_exists.assert_called_once_with(table_id=config.table_id)


@pytest.mark.django_db
def test_check_table_columns_consistency():
    config = GristConfigFactory(create_columns=True, doc_id="123456789", table_id="my_table")
    assert check_table_columns_consistency(config) is True

    GristColumnFactory(grist_config=config)
    config.refresh_from_db()
    assert check_table_columns_consistency(config) is False
