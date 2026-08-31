web: python manage.py migrate && python manage.py collectstatic --no-input && gunicorn MHA.wsgi:application --bind 0.0.0.0:$PORT
