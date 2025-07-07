from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from recoco_sync.lescommuns_connector.tasks import (
    load_lescommuns_services,
    update_or_create_resource_addons,
)

from .factories import LesCommunsProjetFactory


@pytest.fixture
def services():
    return [
        {
            "id": 1,
            "name": "Service 1",
            "logo_url": "string",
            "iframe_url": "string",
        },
        {
            "id": 2,
            "name": "Service 2",
            "logo_url": "string",
            "iframe_url": "string",
        },
    ]


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
    def test_load_services(self, mock_get_project_services, services):
        mock_get_project_services.return_value = services

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


@pytest.mark.django_db
class TestUpdateOrCreateResourceAddons:
    def test_project_not_found(self):
        with pytest.raises(ValueError):
            update_or_create_resource_addons(project_id=1)

    def test_config_not_enabled(self):
        project = LesCommunsProjetFactory(config__enabled=False)
        with pytest.raises(ValueError):
            update_or_create_resource_addons(project_id=project.id)

    def test_webhook_config_not_enabled(self):
        project = LesCommunsProjetFactory(config__webhook_config__enabled=False)
        with pytest.raises(ValueError):
            update_or_create_resource_addons(project_id=project.id)

    def test_service_not_ready(self):
        project = LesCommunsProjetFactory(recommendation_id=None)
        assert update_or_create_resource_addons(project_id=project.id) is False

    @patch(
        "recoco_sync.main.clients.RecocoApiClient.get_resource_addons",
        Mock(return_value={"count": 0}),
    )
    def test_create_addon_called(self, services):
        project = LesCommunsProjetFactory(recommendation_id=1, services=services)

        with patch("recoco_sync.main.clients.RecocoApiClient.create_resource_addon") as mock_create:
            assert update_or_create_resource_addons(project_id=project.id) is True
            mock_create.assert_called_once_with(
                payload={
                    "recommendation": 1,
                    "nature": "lescommuns",
                    "data": services,
                    "enabled": True,
                }
            )

    @patch(
        "recoco_sync.main.clients.RecocoApiClient.get_resource_addons",
        Mock(return_value={"count": 1, "results": [{"id": 8}]}),
    )
    def test_update_addon_called(self, services):
        project = LesCommunsProjetFactory(recommendation_id=1, services=services)

        with patch("recoco_sync.main.clients.RecocoApiClient.update_resource_addon") as mock_update:
            assert update_or_create_resource_addons(project_id=project.id) is True
            mock_update.assert_called_once_with(
                addon_id=8,
                payload={
                    "recommendation": 1,
                    "nature": "lescommuns",
                    "data": services,
                    "enabled": True,
                },
            )
