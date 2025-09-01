release: python manage.py migrate --noinput && python manage.py load_initial_data
web: gunicorn z22.wsgi:application --bind 0.0.0.0:$PORT --log-file -
