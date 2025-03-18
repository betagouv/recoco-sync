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

if [ ! -d "venv" ]; then
    echo "Create virtual environment"
    python -m venv venv
fi
source venv/bin/activate

echo "Install dependencies"
pip install -U dist/*.whl --force-reinstall

echo "Run Django commands"
python manage.py migrate
python manage.py collectstatic --noinput

echo "Done!"
