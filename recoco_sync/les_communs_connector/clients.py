from __future__ import annotations

from typing import Any

from django.conf import settings
from httpx import Client

from recoco_sync.main.clients import TokenBearerAuth, raise_on_4xx_5xx


class LesCommunsApiClient:
    _client: Client

    def __init__(self, api_url: str, *args, **kwargs):
        self._client = Client(
            auth=TokenBearerAuth(
                base_url=api_url,
                username=settings.LES_COMMUNS_API_USERNAME,
                password=settings.LES_COMMUNS_API_PASSWORD,
            ),
            headers=self.headers,
            base_url=api_url,
            event_hooks={"response": [raise_on_4xx_5xx]},
            **kwargs,
        )

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def create_project(self, payload: dict[str, str]) -> dict[str, Any]:
        response = self._client.post("/projets/", json=payload)
        return response.json()

    def update_project(self, project_id: int, payload: dict[str, str]) -> dict[str, Any]:
        response = self._client.patch(f"/projets/{project_id}/", json=payload)
        return response.json()
