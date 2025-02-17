from __future__ import annotations

from typing import Any, Self
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from recoco_sync.utils.json import PrettyJSONEncoder
from recoco_sync.utils.models import BaseModel

from .choices import ObjectType, WebhookEventStatus
from .managers import UserManager


def generate_random_code() -> str:
    return str(uuid4().hex[:12].upper())


class WebhookConfig(BaseModel):
    code = models.CharField(
        max_length=32,
        unique=True,
        default=generate_random_code,
    )
    api_url = models.URLField(max_length=255)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Webhook Config"
        verbose_name_plural = "Webhook Configs"
        db_table = "webhookconfig"
        ordering = ("-created",)


class WebhookEvent(BaseModel):
    webhook_uuid = models.UUIDField()

    webhook_config = models.ForeignKey(
        WebhookConfig, on_delete=models.CASCADE, related_name="events"
    )

    topic = models.CharField(
        max_length=32,
        help_text="Topic of the webhook event",
    )

    object_id = models.CharField(
        max_length=32,
        help_text="ID of the object that triggered the webhook event",
    )

    object_type = models.CharField(
        max_length=32,
        choices=ObjectType.choices,
        help_text="Type of the object that triggered the webhook event",
    )

    remote_ip = models.GenericIPAddressField(help_text="IP address of the request client.")
    headers = models.JSONField(default=dict)
    payload = models.JSONField(default=dict, encoder=PrettyJSONEncoder)

    status = models.CharField(
        max_length=32,
        choices=WebhookEventStatus.choices,
        default=WebhookEventStatus.PENDING,
        help_text="Whether or not the webhook event has been successfully processed",
    )

    exception = models.TextField(blank=True)
    traceback = models.TextField(
        blank=True,
        help_text="Traceback if an exception was thrown during processing",
    )

    class Meta:
        verbose_name = "Webhook Event"
        verbose_name_plural = "Webhook Events"
        db_table = "webhookevent"
        ordering = ("-created",)

    @property
    def object_data(self) -> dict[str, Any]:
        return self.payload.get("object", {})

    @classmethod
    def create_from_request(cls, request: WSGIRequest, **kwargs: dict[str, Any]) -> Self:
        return cls.objects.create(
            remote_ip=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            headers=dict(request.headers),
            **kwargs,
        )


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(_("email address"), max_length=254, unique=True)
    first_name = models.CharField(_("first name"), max_length=254)
    last_name = models.CharField(_("last name"), max_length=254)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
