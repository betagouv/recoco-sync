#!/bin/bash

python -m celery -A recoco_sync.worker worker -l INFO --concurrency=2
