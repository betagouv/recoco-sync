from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from recoco_sync.main.choices import ObjectType, WebhookEventStatus
from recoco_sync.main.tasks import process_webhook_event

from .factories import WebhookEventFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "object_id, object_type, object_payload, expected_object_id, expected_object_type",
    [
        (999, ObjectType.PROJECT, {"project": 999}, 999, ObjectType.PROJECT),
        (888, ObjectType.SURVEY_ANSWER, {"project": 999}, 999, ObjectType.PROJECT),
        (777, ObjectType.TAGGEDITEM, {"id": 999}, 999, ObjectType.PROJECT),
        (
            666,
            ObjectType.USER,
            {"id": 666, "projects": [999, 694, 1029, 1123]},
            666,
            ObjectType.USER,
        ),
        # (ObjectType.RECOMMENDATION, 666, {}),
    ],
)
def test_task_triggered_and_event_saved(
    object_id, object_type, object_payload, expected_object_id, expected_object_type
):
    event = WebhookEventFactory(
        object_id=object_id,
        object_type=object_type,
        payload={"object": object_payload},
    )

    fake_connector = MagicMock()

    with patch("recoco_sync.main.tasks.get_connectors", Mock(return_value=[fake_connector])):
        process_webhook_event(event_id=event.id)

    fake_connector.on_webhook_event.assert_called_once_with(
        object_id=expected_object_id, object_type=expected_object_type, event=event
    )

    event.refresh_from_db()
    assert event.status == WebhookEventStatus.PROCESSED
    assert event.payload == ""


@pytest.mark.django_db
@pytest.mark.parametrize(
    "object_id, object_type, object_payload, expected_object_id, expected_object_type",
    [
        (999, ObjectType.PROJECT, {"project": 999}, 999, ObjectType.PROJECT),
    ],
)
def test_task_failed_and_errors_stored(
    object_id, object_type, object_payload, expected_object_id, expected_object_type
):
    event = WebhookEventFactory(
        object_id=object_id,
        object_type=object_type,
        payload={"object": object_payload},
    )

    error = Exception("something happened")
    fake_connector = MagicMock()
    fake_connector.on_webhook_event.side_effect = error

    with patch("recoco_sync.main.tasks.get_connectors", Mock(return_value=[fake_connector])):
        process_webhook_event(event_id=event.id)

    fake_connector.on_webhook_event.assert_called_once_with(
        object_id=expected_object_id, object_type=expected_object_type, event=event
    )

    event.refresh_from_db()
    assert event.status == WebhookEventStatus.FAILED
    assert event.payload != ""
    assert str(error) in event.traceback
    assert event.exception == '{"MagicMock": "something happened"}'


@pytest.mark.django_db
def test_event_does_not_exist():
    with patch("recoco_sync.main.tasks.logger.error") as logger_mock:
        process_webhook_event(event_id=1)
    logger_mock.assert_called_once_with("WebhookEvent with id=1 does not exist")
