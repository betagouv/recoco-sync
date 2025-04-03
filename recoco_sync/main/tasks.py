from __future__ import annotations

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

    if event.object_type in (ObjectType.SURVEY_ANSWER, ObjectType.TAGGEDITEM):
        object_id = int(event.object_data.get("project"))
        object_type = ObjectType.PROJECT

    for connector in get_connectors():
        connector.on_webhook_event(object_id=object_id, object_type=object_type, event=event)

    event.status = WebhookEventStatus.PROCESSED
    event.save()
