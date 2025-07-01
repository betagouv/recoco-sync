from __future__ import annotations

from unittest.mock import patch

import pytest

from recoco_sync.lescommuns_connector.tasks import load_lescommuns_services

from .factories import LesCommunsConfigFactory, LesCommunsProjetFactory


@pytest.mark.django_db
class TestLoadLescommunsServices:
    def test_unknown_config(self):
        with pytest.raises(ValueError):
            load_lescommuns_services(config_id="a55d2684-f4e8-4c71-bf05-1cf012c3cbce", project_id=1)

    def test_config_not_enabled(self):
        lescommuns_config = LesCommunsConfigFactory(enabled=False)
        with pytest.raises(ValueError):
            load_lescommuns_services(config_id=lescommuns_config.id, project_id=1)

    def test_project_not_found(self):
        lescommuns_config = LesCommunsConfigFactory()
        with pytest.raises(ValueError):
            load_lescommuns_services(config_id=lescommuns_config.id, project_id=1)

    @patch("recoco_sync.lescommuns_connector.tasks.LesCommunsApiClient.get_project_services")
    def test_load_services(self, mock_get_project_services):
        services = [
            {"id": 1, "name": "Service 1"},
            {"id": 2, "name": "Service 2"},
        ]
        mock_get_project_services.return_value = services

        project = LesCommunsProjetFactory()

        load_lescommuns_services(config_id=project.config.id, project_id=project.id)
        project.refresh_from_db()
        assert project.services == services
