from __future__ import annotations

import logging
from typing import Any, Self

from django.conf import settings
from httpx import Client, Response

from recoco_sync.main.clients import TokenBearerAuth

from .models import LesCommunsConfig

logger = logging.getLogger("__name__")


def raise_on_4xx_5xx(response: Response):
    content = response.read()
    if response.status_code >= 400 and settings.ENVIRONMENT == "dev":
        logger.error(f"Error {response.status_code}: {content}")
    response.raise_for_status()


class LesCommunsApiClient:
    _client: Client

    def __init__(self, api_key: str | None = None, *args, **kwargs):
        _auth = TokenBearerAuth(
            base_url=settings.LESCOMMUNS_API_URL,
            username=settings.LESCOMMUNS_API_USERNAME,
            password=settings.LESCOMMUNS_API_PASSWORD,
        )
        if api_key:
            _auth.access_token = api_key

        self._client = Client(
            auth=_auth,
            base_url=settings.LESCOMMUNS_API_URL,
            event_hooks={"response": [raise_on_4xx_5xx]},
        )

    @classmethod
    def from_config(cls, config: LesCommunsConfig) -> Self:
        return cls(api_key=config.api_key)

    def list_projects(self) -> list[dict[str, Any]]:
        response = self._client.get("/projets/")
        return response.json()

    def get_project(self, project_id: int) -> dict[str, Any]:
        response = self._client.get(f"/projets/{project_id}/")
        return response.json()

    def create_project(self, payload: dict[str, str]) -> dict[str, Any]:
        response = self._client.post("/projets/", json=payload)
        return response.json()

    def update_project(self, project_id: int, payload: dict[str, str]) -> dict[str, Any]:
        response = self._client.patch(f"/projets/{project_id}/", json=payload)
        return response.json()
