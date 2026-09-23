from __future__ import annotations

import json
import traceback

from celery import shared_task
from celery.utils.log import get_task_logger

from .choices import ObjectType, WebhookEventStatus
from .connectors import get_connectors
from .models import WebhookEvent

logger = get_task_logger(__name__)


@shared_task
def process_webhook_event(event_id: int):
    try:
        event = WebhookEvent.objects.select_related("webhook_config").get(id=event_id)
    except WebhookEvent.DoesNotExist:
        logger.error(f"WebhookEvent with id={event_id} does not exist")
        return

    object_id: int | None = int(event.object_id)
    object_type: ObjectType | None = ObjectType(event.object_type)

    # these tests are weird because the data sent by core are not really fit for this use.
    # this should be simplified
    if event.object_type in (ObjectType.SURVEY_ANSWER, ObjectType.TAGGEDITEM):
        object_id = int(
            event.object_data.get(
                "project" if event.object_type == ObjectType.SURVEY_ANSWER else "id", object_id
            )
        )
        object_type = ObjectType.PROJECT

    errors = {}
    for connector in get_connectors():
        try:
            connector.on_webhook_event(object_id=object_id, object_type=object_type, event=event)
        except Exception as e:  # noqa: BLE001 it is logged
            errors[connector.__class__.__name__] = e

    if errors:
        event.status = WebhookEventStatus.FAILED
        event.exception = json.dumps(
            {connector_name: str(error) for connector_name, error in errors.items()}
        )
        event.traceback = ("-----" * 3 + "\n").join(
            (
                f"{connector_name}\n" + "".join(traceback.format_exception(error))
                for connector_name, error in errors.items()
            )
        )
    else:
        event.payload = {}
        event.status = WebhookEventStatus.PROCESSED
    event.save()
