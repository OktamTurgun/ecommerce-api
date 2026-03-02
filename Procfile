release: python manage.py collectstatic --noinput && python manage.py migrate --noinput
web: gunicorn config.wsgi:application