#!/bin/bash
cd /var/www/triumf
source /var/www/triumf/ venv/bin/activate

python3 manage.py migrate --no-input
python3 manage.py runserver collectstatic --no-input

gunicorn config.wsgi:application --bind 0.0.0.0:8050

