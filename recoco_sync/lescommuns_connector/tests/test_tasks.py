from __future__ import annotations

from unittest.mock import patch

import pytest

from recoco_sync.lescommuns_connector.tasks import load_lescommuns_services

from .factories import LesCommunsProjetFactory


@pytest.mark.django_db
class TestLoadLescommunsServices:
    def test_project_not_found(self):
        with pytest.raises(ValueError):
            load_lescommuns_services(project_id=1)

    def test_config_not_enabled(self):
        project = LesCommunsProjetFactory(config__enabled=False)
        with pytest.raises(ValueError):
            load_lescommuns_services(project_id=project.id)

    @patch("recoco_sync.lescommuns_connector.tasks.LesCommunsApiClient.get_project_services")
    def test_load_services(self, mock_get_project_services):
        mock_get_project_services.return_value = [
            {
                "id": 1,
                "name": "Service 1",
                "logoUrl": "string",
                "iframeUrl": "string",
            },
            {
                "id": 2,
                "name": "Service 2",
                "logoUrl": "string",
                "iframeUrl": "string",
            },
        ]

        project = LesCommunsProjetFactory()

        assert load_lescommuns_services(project_id=project.id) is True
        project.refresh_from_db()
        assert project.services == [
            {
                "id": 1,
                "name": "Service 1",
                "logo_url": "string",
                "is_listed": True,
                "iframe_url": "string",
                "sous_titre": None,
                "description": None,
                "extend_label": None,
                "extra_fields": [],
                "redirection_url": None,
                "redirection_label": None,
            },
            {
                "id": 2,
                "name": "Service 2",
                "logo_url": "string",
                "is_listed": True,
                "iframe_url": "string",
                "sous_titre": None,
                "description": None,
                "extend_label": None,
                "extra_fields": [],
                "redirection_url": None,
                "redirection_label": None,
            },
        ]

    @patch("recoco_sync.lescommuns_connector.tasks.LesCommunsApiClient.get_project_services")
    def test_no_services_found(self, mock_get_project_services):
        mock_get_project_services.return_value = []

        project = LesCommunsProjetFactory()

        assert load_lescommuns_services(project_id=project.id) is False
        project.refresh_from_db()
        assert project.services == []
