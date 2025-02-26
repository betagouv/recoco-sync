from __future__ import annotations

import logging
from typing import Any, assert_never

from django.db import transaction
from main.connectors import Connector
from main.models import WebhookEvent
from main.utils import QuestionType, get_question_type

from .choices import GristColumnType
from .clients import GristApiClient
from .constants import project_columns_spec
from .models import GristColumn, GristConfig

logger = logging.getLogger(__name__)


class GristConnector(Connector):
    def update_project(self, project_id: int, event: WebhookEvent) -> None:
        for config in GristConfig.objects.filter(
            enabled=True, webhook_config_id=event.webhook_config.pk
        ):
            for _, project_data in self.fetch_projects_data(
                project_ids=[project_id], config=config
            ):
                update_or_create_project_record(
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
            GristColumn.objects.create(
                grist_config=config,
                col_id=question.get("slug").replace("-", "_"),
                label=question.get("text_short"),
                type=self.get_column_type_from_payload(question),
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


def update_or_create_project_record(config: GristConfig, project_id: int, project_data: dict):
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


def grist_table_exists(config: GristConfig) -> bool:
    """Check if a table exists in Grist."""

    return GristApiClient.from_config(config).table_exists(table_id=config.table_id)


def check_table_columns_consistency(config: GristConfig) -> bool:
    """Check the columns of a table in Grist are consistent with the config."""

    config_table_columns = config.table_columns
    config_table_columns_keys = [t["id"] for t in config_table_columns]

    remote_table_columns = GristApiClient.from_config(config).get_table_columns(
        table_id=config.table_id
    )
    remote_table_columns = [
        {"id": t["id"], "fields": {k: t["fields"][k] for k in ("label", "type")}}
        for t in remote_table_columns
        if t["id"] in config_table_columns_keys
    ]

    return sorted(remote_table_columns, key=lambda x: x["id"]) == sorted(
        config_table_columns, key=lambda x: x["id"]
    )
