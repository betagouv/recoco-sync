from __future__ import annotations

import logging
from typing import Any, assert_never

from django.conf import settings
from django.db import transaction

from recoco_sync.main.choices import ObjectType
from recoco_sync.main.connectors import Connector
from recoco_sync.main.models import WebhookEvent
from recoco_sync.main.utils import QuestionType, get_question_type

from .choices import GristColumnType
from .clients import GristApiClient
from .constants import project_columns_spec
from .models import GristColumn, GristConfig

logger = logging.getLogger(__name__)


class GristConnector(Connector):
    def on_webhook_event(
        self, object_id: int, object_type: ObjectType, event: WebhookEvent
    ) -> None:
        if not object_type.is_project:
            return

        for config in GristConfig.objects.filter(
            enabled=True, webhook_config_id=event.webhook_config.pk
        ):
            for _, project_data in self.fetch_projects_data(project_ids=[object_id], config=config):
                self.update_or_create_project_record(
                    config=config, project_id=object_id, project_data=project_data
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
            question_col_id = question.get("slug").replace("-", "_")
            question_col_label = self.get_column_label_from_payload(question)

            GristColumn.objects.get_or_create(
                grist_config=config,
                col_id=question_col_id,
                defaults={
                    "label": question_col_label,
                    "type": self.get_column_type_from_payload(question),
                },
            )

            if get_question_type(question) != QuestionType.SIMPLE:
                GristColumn.objects.get_or_create(
                    grist_config=config,
                    col_id=f"{question_col_id}_comment",
                    defaults={
                        "label": f"Commentaire de {question_col_label}",
                        "type": GristColumnType.TEXT,
                    },
                )

    @staticmethod
    def get_column_type_from_payload(question: dict[str, Any]) -> GristColumnType:
        match get_question_type(question):
            case QuestionType.SIMPLE:
                return GristColumnType.TEXT
            case QuestionType.YES_NO:
                return GristColumnType.BOOL
            case QuestionType.YES_NO_MAYBE:
                return GristColumnType.TEXT
            case QuestionType.CHOICES:
                return GristColumnType.TEXT
            case QuestionType.MULTIPLE_CHOICES:
                return GristColumnType.CHOICE_LIST
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
        Update a record related to a given project on Grist side,
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
