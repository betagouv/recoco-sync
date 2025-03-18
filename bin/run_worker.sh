#!/bin/bash


if [ -d "venv" ]; then
    source venv/bin/activate
fi

python -m celery -A recoco_sync.worker worker -l INFO --concurrency=2
