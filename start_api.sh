#!/bin/bash
set -euo pipefail

echo "<<<<<<<< Static file collection >>>>>>>>>"
uv run python manage.py collectstatic --noinput


echo "<<<<<<<< Database Setup and Migrations Starts >>>>>>>>>"
uv run python manage.py migrate&

echo "<<<<<<< Database Setup and Migrations Complete >>>>>>>>>>"
echo " "

echo "<<<<<<<<<<< SEED DATA >>>>>>>>"
uv run python manage.py seed_data


echo " "
echo "<<<<<<<<<<<<<<<<<<<< START Celery >>>>>>>>>>>>>>>>>>>>>>>>"
uv run celery -A app worker -l info --pool=gevent --concurrency=1000&


echo "<<<<<<<<<<<<<<<<<<<< START API >>>>>>>>>>>>>>>>>>>>>>>>"
# Start the API with gunicorn
uv run gunicorn --bind 0.0.0.0:8000 app.wsgi --reload --access-logfile '-' --workers 2
