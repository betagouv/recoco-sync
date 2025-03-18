#!/bin/bash

set -e

cd /home/recocosync/app

echo "Checking environment variables"
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    echo "DJANGO_SETTINGS_MODULE is not set"
    exit 1
fi
if [ -z "$DOTENV_FILE" ]; then
    echo "DOTENV_FILE is not set"
    exit 1
fi

echo "Setup python environment"
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -U dist/*.whl

echo "Run Django commands"
python manage.py migrate
python manage.py collectstatic --noinput

echo "Done!"
