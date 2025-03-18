from __future__ import annotations

import os

for k, v in {
    "ENVIRONMENT": "prod",
    "DEBUG": "false",
}.items():
    os.environ.setdefault(k, v)

from .default import *
