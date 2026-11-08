#!/bin/sh

python manage.py collectstatic --noinput

python manage.py makemigrations
python manage.py migrate

# APP_PORT variable must be present in env
python manage.py runserver 0.0.0.0:${APP_PORT}
