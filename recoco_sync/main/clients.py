from __future__ import annotations

from typing import Any

from django.conf import settings
from httpx import Auth, Client, Request, Response


class TokenBearerAuth(Auth):
    requires_response_body = True
    access_token: str = None
    refresh_token: str = None
    base_url: str
    username: str
    password: str

    def __init__(self, base_url: str, username: str, password: str, *args, **kwargs):
        self.base_url = base_url
        self.username = username
        self.password = password
        super().__init__(*args, **kwargs)

    def auth_flow(self, request: Request):
        if self.access_token is None:
            token_response = yield self._build_token_request()
            self._update_tokens(token_response)
            request.headers["Authorization"] = f"Bearer {self.access_token}"
            yield request

        request.headers["Authorization"] = f"Bearer {self.access_token}"
        response = yield request

        if response.status_code == 401:
            refresh_response = yield self._build_refresh_request()
            self._update_tokens(refresh_response)
            request.headers["Authorization"] = f"Bearer {self.access_token}"
            yield request

    def _build_token_request(self):
        return Request(
            "POST",
            f"{self.base_url}/token/",
            data={
                "username": self.username,
                "password": self.password,
            },
        )

    def _build_refresh_request(self):
        return Request(
            "POST",
            f"{self.base_url}/token/refresh/",
            data={
                "refresh": self.refresh_token,
            },
        )

    def _update_tokens(self, response: Response):
        payload = response.json()
        self.access_token = payload["access"]
        if "refresh" in payload:
            self.refresh_token = payload["refresh"]


def raise_on_4xx_5xx(response: Response):
    response.raise_for_status()


class RecocoApiClient:
    _client: Client

    def __init__(self, api_url: str, *args, **kwargs):
        self._client = Client(
            auth=TokenBearerAuth(
                base_url=api_url,
                username=settings.RECOCO_API_USERNAME,
                password=settings.RECOCO_API_PASSWORD,
            ),
            base_url=api_url,
            event_hooks={"response": [raise_on_4xx_5xx]},
            **kwargs,
        )

    def get_projects(self) -> dict[str, Any]:
        response = self._client.get("/projects/")
        return response.json()

    def get_project(self, project_id: int) -> dict[str, Any]:
        response = self._client.get(f"/projects/{project_id}/")
        return response.json()

    def get_survey_sessions(self, project_id: int) -> dict[str, Any]:
        response = self._client.get(f"/survey/sessions/?project_id={project_id}")
        return response.json()

    def get_survey_session_answers(self, session_id: int) -> dict[str, Any]:
        response = self._client.get(f"/survey/sessions/{session_id}/answers/")
        return response.json()

    def get_questions(self) -> dict[str, Any]:
        response = self._client.get("/survey/questions/?limit=500")
        return response.json()

    def get_resource_addons(self, recommendation_id: int) -> dict[str, Any]:
        response = self._client.get(
            f"/api/resource-addons/?recommendation={recommendation_id}&nature=lescommuns"
        )
        return response.json()

    def create_resource_addon(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._client.post("/api/resource-addons/", json=payload)
        return response.json()
