from __future__ import annotations

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

    for project_id, project_data in GristConnector().fetch_projects_data(config=config):
        batch_records.append({"object_id": project_id} | project_data)

        if len(batch_records) > batch_size - 1:
            grist_client.create_records(table_id=config.table_id, records=batch_records)
            batch_records = []

    if len(batch_records) > 0:
        grist_client.create_records(table_id=config.table_id, records=batch_records)


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
                    "error": err.response.content,
                }
            )
            break

    if errors:
        logger.error(f"Grist {config.name}, update failures: {errors}.")
