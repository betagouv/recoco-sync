from __future__ import annotations

import os

for k, v in {
    "ENVIRONMENT": "dev",
    "SECRET_KEY": "youshallnotpass",
    "WEBHOOK_SECRET": "youshallnotpass",
}.items():
    os.environ.setdefault(k, v)

from .default import *

INSTALLED_APPS += [
    "debug_toolbar",
    "django_browser_reload",
]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

INTERNAL_IPS = [
    "127.0.0.1",
]
