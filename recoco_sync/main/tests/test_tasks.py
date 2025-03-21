from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from recoco_sync.main.choices import ObjectType, WebhookEventStatus
from recoco_sync.main.tasks import process_webhook_event

from .factories import WebhookEventFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "object_type, object_id, object_payload",
    [
        (ObjectType.PROJECT, 999, {"project": 999}),
        (ObjectType.PROJECT, 999, {"project": 999}),
        (ObjectType.SURVEY_ANSWER, 888, {"project": 999}),
    ],
)
def test_task_triggered_and_event_saved(object_type, object_id, object_payload):
    event = WebhookEventFactory(
        object_type=object_type,
        object_id=object_id,
        payload={"object": object_payload},
    )

    fake_connector = MagicMock()

    with patch("recoco_sync.main.tasks.get_connectors", Mock(return_value=[fake_connector])):
        process_webhook_event(event_id=event.id)

    fake_connector.on_project_event.assert_called_once_with(project_id=999, event=event)

    event.refresh_from_db()
    assert event.status == WebhookEventStatus.PROCESSED


@pytest.mark.django_db
def test_event_does_not_exist():
    with patch("recoco_sync.main.tasks.logger.error") as logger_mock:
        process_webhook_event(event_id=1)
    logger_mock.assert_called_once_with("WebhookEvent with id=1 does not exist")
