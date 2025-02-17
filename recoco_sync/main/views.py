from __future__ import annotations

from copy import deepcopy as copy
from functools import partial

from django.db import transaction
from django.http import HttpRequest
from ninja import Router

from .choices import WebhookEventStatus
from .models import WebhookConfig, WebhookEvent
from .schemas import WebhookEventSchema
from .security import SecurityAuth
from .triggers import on_webhook_event_commit

router = Router()


@router.post("/webhook/{code}", auth=SecurityAuth())
def webhook(request: HttpRequest, code: str, payload: WebhookEventSchema):
    try:
        config = WebhookConfig.objects.get(code=code)
    except WebhookConfig.DoesNotExist:
        return {
            "id": None,
            "status": WebhookEventStatus.INVALID,
            "message": "Invalid webhook code",
        }
    if not config.enabled:
        return {
            "id": None,
            "status": WebhookEventStatus.INVALID,
            "message": "Webhook is disabled",
        }

    # FIXME: fix this stuff, make something simpler
    data = payload.dict()
    data["payload"] = copy(data)
    obj = data.pop("object")
    data["object_id"] = obj["id"]
    data["webhook_config_id"] = config.id

    with transaction.atomic():
        event = WebhookEvent.create_from_request(request, **data)
        transaction.on_commit(partial(on_webhook_event_commit, event=event))

    return {
        "id": event.id,
        "status": event.status,
        "message": "Webhook event created",
    }
