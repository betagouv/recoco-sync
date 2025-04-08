from __future__ import annotations

from typing import Any

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
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

    bulk_records = []
    bulk_errors = []

    for project_id, project_data in GristConnector().fetch_projects_data(config=config):
        bulk_records.append(
            {
                "fields": {"object_id": project_id} | project_data,
            }
        )

        if len(bulk_records) > settings.BULK_SIZE - 1:
            bulk_errors += _batch_create_records(
                grist_client=grist_client,
                table_id=config.table_id,
                records=bulk_records,
            )
            bulk_records = []

    if len(bulk_records) > 0:
        bulk_errors += _batch_create_records(
            grist_client=grist_client,
            table_id=config.table_id,
            records=bulk_records,
        )

    if len(bulk_errors):
        logger.error(f"Grist {config.name}, creation failures: {bulk_errors}.")


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
        # fetch reference table data
        grist_client.doc_id = reference.doc_id
        ref_columns = grist_client.get_table_columns(table_id=reference.table_id)
        ref_records = grist_client.get_records(table_id=reference.table_id, filter={}).get(
            "records"
        )

        # switch to the destination doc
        grist_client.doc_id = config.doc_id

        # create the reference table in the destination doc if not exists
        if not grist_client.table_exists(table_id=reference.table_id):
            grist_client.create_table(
                table_id=reference.table_id,
                columns=ref_columns,
            )
        else:
            # update the reference table columns in the destination doc
            grist_client.update_table_columns(
                table_id=reference.table_id,
                columns=ref_columns,
            )
            dst_records = grist_client.get_records(
                table_id=reference.table_id,
                filter={},
            ).get("records")

            # empty the reference table in the destination doc
            bulk_delete = []

            for record in dst_records:
                bulk_delete.append(record["id"])

                if len(bulk_delete) > settings.BULK_SIZE - 1:
                    grist_client.delete_records(
                        table_id=reference.table_id,
                        record_ids=bulk_delete,
                    )
                    bulk_delete = []

            if len(bulk_delete) > 0:
                grist_client.delete_records(
                    table_id=reference.table_id,
                    record_ids=bulk_delete,
                )

        # fill the reference table in the destination doc
        bulk_records = []

        for record in ref_records:
            bulk_records.append(
                {
                    "fields": record["fields"],
                }
            )
            if len(bulk_records) > settings.BULK_SIZE - 1:
                grist_client.create_records(
                    table_id=reference.table_id,
                    records=bulk_records,
                )
                bulk_records = []

        if len(bulk_records) > 0:
            grist_client.create_records(
                table_id=reference.table_id,
                records=bulk_records,
            )
