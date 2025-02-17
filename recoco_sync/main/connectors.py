from __future__ import annotations

import inspect
import logging
from abc import ABCMeta, abstractmethod
from collections.abc import Generator
from importlib import import_module
from typing import Any

from django.apps import apps
from django.utils.module_loading import module_has_submodule
from main.models import WebhookEvent

from .clients import RecocoApiClient

logger = logging.getLogger(__name__)


class Connector(metaclass=ABCMeta):
    def get_recoco_api_client(self, **kwargs) -> RecocoApiClient:
        return RecocoApiClient(timeout=60, **kwargs)

    def fetch_projects_data(
        self, project_ids: list[int] | None = None, **kwargs
    ) -> Generator[tuple[int, dict]]:
        """Fetch data related to projects through the Recoco API."""

        recoco_client = self.get_recoco_api_client(**kwargs)

        if project_ids:
            projects = [
                recoco_client.get_project(project_id=project_id) for project_id in project_ids
            ]
        else:
            projects = recoco_client.get_projects()

        for project in projects:
            project_data = self.map_from_project_payload_object(payload=project, **kwargs)

            sessions = recoco_client.get_survey_sessions(project_id=project["id"])
            if sessions["count"] > 0:
                answers = recoco_client.get_survey_session_answers(
                    session_id=sessions["results"][0]["id"]
                )
                for answer in answers["results"]:
                    project_data.update(
                        self.map_from_survey_answer_payload_object(payload=answer, **kwargs)
                    )

            yield project["id"], project_data

    def map_from_project_payload_object(self, payload: dict[str, Any], **kwargs) -> dict[str, Any]:
        try:
            return {
                "name": payload["name"],
                "description": payload["description"],
                "city": payload["commune"]["name"],
                "postal_code": int(payload["commune"]["postal"]),
                "insee": int(payload["commune"]["insee"]),
                "department": payload["commune"]["department"]["name"],
                "department_code": int(payload["commune"]["department"]["code"]),
                "location": payload["location"],
                "tags": ",".join(payload["tags"]),
            }
        except (KeyError, ValueError) as exc:
            logger.error(f"Error while mapping project #{payload['id']} payload: {exc}")
            return {}

    def map_from_survey_answer_payload_object(
        self, payload: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        col_id = str(payload["question"]["slug"]).replace("-", "_")

        choices = payload.get("choices")
        comment = payload.get("comment")

        data = {}

        if len(choices) > 0:
            data[col_id] = ",".join([c["text"] for c in choices])
            if comment:
                data[f"{col_id}_comment"] = comment

        # FIXME: handle boolean question case
        # elif "cas du Oui/Non"

        else:
            data[col_id] = comment

        if attachment := payload.get("attachment"):
            data[f"{col_id}_attachment"] = attachment

        return data

    @abstractmethod
    def update_project(self, project_id: int, event: WebhookEvent) -> None:
        pass

    def fetch_questions_data(self, **kwargs) -> Generator[tuple[int, dict]]:
        """Fetch data related to questions through the Recoco API."""

        recoco_client = self.get_recoco_api_client(**kwargs)

        questions = recoco_client.get_questions()

        for question in questions.get("results", []):
            question_data = self.map_from_question_payload_object(payload=question, **kwargs)
            yield question["id"], question_data

    def map_from_question_payload_object(self, payload: dict[str, Any], **kwargs) -> dict[str, Any]:
        return payload


connectors: list[Connector] = []


def get_connectors() -> list[Connector]:
    return connectors


def auto_discover_connectors():
    """Collect all connectors from installed apps."""

    for app_config in apps.get_app_configs():
        if app_config.name.startswith("django.contrib") or not module_has_submodule(
            package=app_config.module, module_name="connectors"
        ):
            continue

        app_module = import_module(name=f"{app_config.name}.connectors")

        for name, obj in inspect.getmembers(app_module):
            if inspect.isclass(obj) and name != "Connector" and issubclass(obj, Connector):
                connectors.append(obj())
