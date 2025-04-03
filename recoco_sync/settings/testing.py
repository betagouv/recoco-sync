from __future__ import annotations

import os

for k, v in {
    "ENVIRONMENT": "testing",
    "SECRET_KEY": "youshallnotpass",
    "DATABASE_URL": "postgres://postgres:postgres@localhost:5435/recocosync-testing",
    "BROKER_URL": "redis://localhost:6380/0",
    "RECOCO_API_USERNAME": "",
    "RECOCO_API_PASSWORD": "",
    "WEBHOOK_SECRET": "youshallnotpass",
    "LESCOMMUNS_API_URL": "https://les-communs-transition-ecologique-api-staging.osc-fr1.scalingo.io/api",
    "LESCOMMUNS_API_USERNAME": "",
    "LESCOMMUNS_API_PASSWORD": "",
}.items():
    os.environ.setdefault(k, v)


from .default import *

RECOCO_API_URL_EXAMPLE = "https://recoco.example.com/api"
GRIST_API_URL_EXAMPLE = "https://grist.example.com/api"
