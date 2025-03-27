from __future__ import annotations

from typing import Any, Self

from django.conf import settings
from httpx import Client

from recoco_sync.main.clients import TokenBearerAuth, raise_on_4xx_5xx

from .models import LesCommunsConfig


class LesCommunsApiClient:
    _client: Client

    def __init__(self, *args, **kwargs):
        _auth = TokenBearerAuth(
            base_url=settings.LES_COMMUNS_API_URL,
            username=settings.LES_COMMUNS_API_USERNAME,
            password=settings.LES_COMMUNS_API_PASSWORD,
        )
        if settings.LES_COMMUNS_API_KEY:
            _auth.access_token = settings.LES_COMMUNS_API_KEY

        self._client = Client(
            auth=_auth,
            base_url=settings.LES_COMMUNS_API_URL,
            event_hooks={"response": [raise_on_4xx_5xx]},
        )

    @classmethod
    def from_config(cls, config: LesCommunsConfig) -> Self:
        return cls(
            # ...
        )

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
