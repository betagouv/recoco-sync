from __future__ import annotations

import inspect
import logging
from abc import ABCMeta, abstractmethod
from collections.abc import Generator
from importlib import import_module
from typing import Any

from django.apps import apps
from django.utils.module_loading import module_has_submodule

from recoco_sync.main.models import WebhookEvent
from recoco_sync.main.utils import QuestionType, get_question_type

from .clients import RecocoApiClient
from .schemas import Project

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
        data = Project(**payload)
        return data.model_dump(by_alias=True)

    def map_from_survey_answer_payload_object(
        self, payload: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        data = {}

        question = payload.get("question")
        if not question:
            return data

        question_slug = question.get("slug")
        if not question_slug:
            return data

        col_id = str(question_slug).replace("-", "_")
        choices = payload.get("choices", [])
        comment = payload.get("comment", "")

        match get_question_type(question):
            case QuestionType.SIMPLE:
                data[col_id] = comment

            case QuestionType.YES_NO:
                data[col_id] = (
                    str(choices[0]["text"]).lower() == "oui" if len(choices) > 0 else False
                )
                data[f"{col_id}_comment"] = comment

            case QuestionType.YES_NO_MAYBE:
                data[col_id] = str(choices[0]["text"]).lower() if len(choices) > 0 else ""
                data[f"{col_id}_comment"] = comment

            case QuestionType.CHOICES | QuestionType.MULTIPLE_CHOICES:
                data[col_id] = ",".join([c["text"] for c in choices])
                data[f"{col_id}_comment"] = comment

        if attachment := payload.get("attachment"):
            data[f"{col_id}_attachment"] = attachment

        return data

    @abstractmethod
    def on_project_event(self, project_id: int, event: WebhookEvent) -> None:
        pass


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
