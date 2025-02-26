from __future__ import annotations

from unittest.mock import patch

import pytest
from grist_connector.tasks import populate_grist_table, refresh_grist_table

from .factories import GristConfigFactory


class TestPopulateGristTable:
    @pytest.mark.django_db
    def test_config_does_not_exist(self):
        with patch("grist_connector.tasks.logger.error") as logger_mock:
            populate_grist_table(config_id="40d26f87-8b91-4670-a196-bfdcbc39eabb")
        logger_mock.assert_called_once_with(
            "GristConfig with id=40d26f87-8b91-4670-a196-bfdcbc39eabb does not exist"
        )


@pytest.mark.django_db
class TestRefreshGristTable:
    def test_config_does_not_exist(self):
        with patch("grist_connector.tasks.logger.error") as logger_mock:
            refresh_grist_table(config_id="40d26f87-8b91-4670-a196-bfdcbc39eabb")
        logger_mock.assert_called_once_with(
            "GristConfig with id=40d26f87-8b91-4670-a196-bfdcbc39eabb does not exist"
        )

    @patch("grist_connector.tasks.update_or_create_project_record")
    @patch("grist_connector.connectors.GristConnector.fetch_projects_data")
    def test_update_or_create_project_record_call(
        self,
        mock_fetch_projects_data,
        mock_update_or_create_project_record,
    ):
        mock_fetch_projects_data.return_value = [("project_id", {"project_data": "data"})]

        config = GristConfigFactory()
        refresh_grist_table(config_id=config.id)

        mock_fetch_projects_data.assert_called_once_with(config=config)

        mock_update_or_create_project_record.assert_called_once_with(
            config=config,
            project_id="project_id",
            project_data={"project_data": "data"},
        )
