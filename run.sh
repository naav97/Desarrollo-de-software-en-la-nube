flask run --host=0.0.0.0 &
celery -A app.celery_app worker --loglevel INFO