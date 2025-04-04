from __future__ import annotations

import logging
from typing import Any, assert_never

from django.conf import settings
from django.db import transaction

from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent
from recoco_sync.main.utils import QuestionType, get_question_type

from .choices import GristColumnType
from .clients import GristApiClient
from .constants import project_columns_spec
from .models import GristColumn, GristConfig

logger = logging.getLogger(__name__)


class GristConnector(Connector):
    def on_project_event(self, project_id: int, event: WebhookEvent) -> None:
        for config in GristConfig.objects.filter(
            enabled=True, webhook_config_id=event.webhook_config.pk
        ):
            for _, project_data in self.fetch_projects_data(
                project_ids=[project_id], config=config
            ):
                self.update_or_create_project_record(
                    config=config, project_id=project_id, project_data=project_data
                )

    def get_recoco_api_client(self, **kwargs):
        config: GristConfig = kwargs.get("config")
        return super().get_recoco_api_client(api_url=config.webhook_config.api_url)

    def map_from_project_payload_object(self, payload, **kwargs):
        config: GristConfig = kwargs.get("config")
        if not len(config.table_headers):
            return {}

        data = super().map_from_project_payload_object(payload, **kwargs)
        return {k: data[k] for k in config.table_headers if k in data}

    def map_from_survey_answer_payload_object(self, payload, **kwargs):
        config: GristConfig = kwargs.get("config")
        if not len(config.table_headers):
            return {}

        data = super().map_from_survey_answer_payload_object(payload, **kwargs)
        return {k: data[k] for k in config.table_headers if k in data}

    @transaction.atomic
    def update_or_create_columns(self, config: GristConfig, **kwargs):
        GristColumn.objects.filter(grist_config=config).delete()

        for col_id, col_spec in project_columns_spec.items():
            GristColumn.objects.create(
                grist_config=config,
                col_id=col_id,
                label=col_spec["label"],
                type=col_spec["type"],
            )

        questions = self.get_recoco_api_client(config=config).get_questions()
        for question in questions.get("results"):
            GristColumn.objects.get_or_create(
                grist_config=config,
                col_id=question.get("slug").replace("-", "_"),
                defaults={
                    "label": self.get_column_label_from_payload(question),
                    "type": self.get_column_type_from_payload(question),
                },
            )

    @staticmethod
    def get_column_type_from_payload(question: dict[str, Any]) -> GristColumnType:
        match get_question_type(question):
            case QuestionType.YES_NO:
                return GristColumnType.BOOL
            case QuestionType.MULTIPLE:
                return GristColumnType.CHOICE_LIST
            case QuestionType.REGULAR | QuestionType.YES_NO_MAYBE:
                return GristColumnType.TEXT
            case _:
                assert_never(question)

    @staticmethod
    def get_column_label_from_payload(question: dict[str, Any]) -> str:
        col_label = (
            question.get("text_short")
            or question.get("text")
            or question.get("slug").replace("_", " ").title()
        )
        if len(col_label) > settings.TABLE_COLUMN_HEADER_MAX_LENGTH:
            col_label = f"{col_label[: settings.TABLE_COLUMN_HEADER_MAX_LENGTH - 3]}..."
        return col_label

    def update_or_create_project_record(
        self, config: GristConfig, project_id: int, project_data: dict
    ):
        """
        Update a record related to a givent project, in a Grist table,
        or create it if it doesn't exist.
        """

        client = GristApiClient.from_config(config)

        resp = client.get_records(
            table_id=config.table_id,
            filter={"object_id": [project_id]},
        )

        if len(records := resp["records"]):
            client.update_records(
                table_id=config.table_id,
                records={
                    records[0]["id"]: project_data,
                },
            )
            return

        client.create_records(
            table_id=config.table_id,
            records=[{"object_id": project_id} | project_data],
        )
