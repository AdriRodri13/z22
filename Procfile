release: python manage.py migrate --noinput && python manage.py load_initial_data
web: gunicorn z22.wsgi:application --log-file -
