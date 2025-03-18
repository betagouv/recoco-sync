from __future__ import annotations

import uuid

import factory
import factory.fuzzy
from django.conf import settings
from grist_connector.choices import GristColumnType
from grist_connector.connectors import GristConnector
from grist_connector.models import GristColumn, GristConfig

from recoco_sync.main.choices import ObjectType
from recoco_sync.main.models import WebhookEvent
from recoco_sync.main.tests.factories import BaseFactory, WebhookConfigFactory


class WebhookEventFactory(BaseFactory):
    class Meta:
        model = WebhookEvent

    webhook_uuid = factory.LazyFunction(uuid.uuid4)
    topic = "projects.Project/update"
    object_id = 1
    object_type = ObjectType.PROJECT

    remote_ip = factory.Faker("ipv4")
    headers = {}
    payload = {}


class GristConfigFactory(BaseFactory):
    class Meta:
        model = GristConfig

    api_url = settings.GRIST_API_URL_EXAMPLE
    name = factory.Faker("word")
    doc_id = factory.fuzzy.FuzzyText(length=10)
    table_id = factory.fuzzy.FuzzyText(length=10)
    webhook_config = factory.SubFactory(WebhookConfigFactory)

    @factory.post_generation
    def create_columns(obj, create, extracted, **kwargs):  # noqa: N805
        if not create:
            return
        if extracted:
            GristConnector().update_or_create_columns(config=obj)


class GristColumnFactory(BaseFactory):
    class Meta:
        model = GristColumn

    col_id = factory.Faker("word")
    label = factory.Faker("word")
    type = GristColumnType.TEXT
