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
        data = {}

        for src, dst in {
            "name": "name",
            "description": "description",
            "location": "location",
            "org_name": "organization",
            "created_on": "created",
            "updated_on": "modified",
        }.items():
            data[dst] = payload.get(src, "")

        if commune := payload.get("commune"):
            try:
                data.update(
                    {
                        "city": commune["name"],
                        "postal_code": int(commune["postal"]),
                        "insee": int(commune["insee"]),
                        "department": commune["department"]["name"],
                        "department_code": int(commune["department"]["code"]),
                    }
                )
            except (KeyError, ValueError) as exc:
                logger.error(f"Error while mapping commune of project #{payload['id']}: {exc}")

        data["tags"] = ",".join(payload.get("tags", []))

        return data

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
            case QuestionType.MULTIPLE:
                data[col_id] = ",".join([c["text"] for c in choices])
                data[f"{col_id}_comment"] = comment

            case QuestionType.YES_NO:
                data[col_id] = (
                    str(choices[0]["text"]).lower() == "oui" if len(choices) > 0 else False
                )
                data[f"{col_id}_comment"] = comment

            case QuestionType.REGULAR | QuestionType.YES_NO_MAYBE:
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
