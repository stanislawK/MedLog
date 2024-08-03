#!/bin/bash

python manage.py migrate --noinput
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to migrate: $status"
    exit $status
fi
if [ $DEBUG == True ]; then
    python manage.py runserver 0.0.0.0:8000
else
    python manage.py collectstatic --noinput &&
    gunicorn -w 2 core.wsgi:application --bind 0.0.0.0:8000
fi
