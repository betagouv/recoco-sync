from __future__ import annotations

import os

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

for k, v in {
    "ENVIRONMENT": "prod",
    "DEBUG": "false",
}.items():
    os.environ.setdefault(k, v)

from .default import *

#
# Sentry
#
if SENTRY_URL := env.str("SENTRY_URL", default=None):
    sentry_sdk.init(
        dsn=SENTRY_URL,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        environment=ENVIRONMENT,
        traces_sample_rate=0.05,
        send_default_pii=True,
    )
