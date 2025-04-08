from __future__ import annotations

from typing import Any

from celery import shared_task
from celery.utils.log import get_task_logger
from httpx import HTTPError

from .clients import GristApiClient
from .connectors import GristConnector
from .models import GristConfig

logger = get_task_logger(__name__)


@shared_task
def populate_grist_table(config_id: str):
    try:
        config = GristConfig.objects.prefetch_related("columns").get(id=config_id)
    except GristConfig.DoesNotExist:
        logger.error(f"GristConfig with id={config_id} does not exist")
        return

    grist_client = GristApiClient.from_config(config)

    grist_client.create_table(
        table_id=config.table_id,
        columns=config.table_columns,
    )

    batch_records = []
    batch_size = 100
    batch_errors = []

    for project_id, project_data in GristConnector().fetch_projects_data(config=config):
        batch_records.append({"object_id": project_id} | project_data)

        if len(batch_records) > batch_size - 1:
            batch_errors += _batch_create_records(
                grist_client=grist_client,
                table_id=config.table_id,
                records=batch_records,
            )
            batch_records = []

    if len(batch_records) > 0:
        batch_errors += _batch_create_records(
            grist_client=grist_client,
            table_id=config.table_id,
            records=batch_records,
        )

    if len(batch_errors):
        logger.error(f"Grist {config.name}, creation failures: {batch_errors}.")


def _batch_create_records(
    grist_client: GristApiClient, table_id: str, records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    errors = []

    try:
        grist_client.create_records(table_id=table_id, records=records)
    except HTTPError:
        pass
    else:
        return errors

    for record in records:
        try:
            grist_client.create_records(table_id=table_id, records=[record])
        except HTTPError as err:
            errors.append(
                {
                    "project_id": record.get("object_id"),
                    "error": str(err),
                }
            )

    return errors


@shared_task
def refresh_grist_table(config_id: str):
    try:
        config = GristConfig.objects.get(id=config_id)
    except GristConfig.DoesNotExist:
        logger.error(f"GristConfig with id={config_id} does not exist")
        return

    errors = []
    grist_connector = GristConnector()

    for project_id, project_data in grist_connector.fetch_projects_data(config=config):
        try:
            grist_connector.update_or_create_project_record(
                config=config, project_id=project_id, project_data=project_data
            )
        except HTTPError as err:
            errors.append(
                {
                    "project_id": project_id,
                    "error": str(err),
                }
            )

    if errors:
        logger.error(f"Grist {config.name}, update failures: {errors}.")


@shared_task
def sync_grist_references(config_id: str):
    try:
        config = GristConfig.objects.get(id=config_id)
    except GristConfig.DoesNotExist:
        logger.error(f"GristConfig with id={config_id} does not exist")
        return

    grist_client = GristApiClient.from_config(config)

    for reference in config.references.all():
        grist_client.doc_id = reference.doc_id
        ref_columns = grist_client.get_table_columns(table_id=reference.table_id)
        ref_records = grist_client.get_records(table_id=reference.table_id, filter={})

        grist_client.doc_id = config.doc_id
        if not grist_client.table_exists(table_id=reference.table_id):
            grist_client.create_table(
                table_id=reference.table_id,
                columns=ref_columns,
            )
        grist_client.update_records(
            table_id=reference.table_id,
            records=ref_records.get("records"),
        )
