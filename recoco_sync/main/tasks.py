from __future__ import annotations

from typing import assert_never

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

    match event.object_type:
        case ObjectType.PROJECT | ObjectType.TAGGEDITEM:
            project_id = int(event.object_id)
        case ObjectType.SURVEY_ANSWER:
            project_id = int(event.object_data.get("project"))
        case _:
            assert_never(event.object_type)

    for connector in get_connectors():
        connector.on_project_event(project_id=project_id, event=event)

    event.status = WebhookEventStatus.PROCESSED
    event.save()
