#!/bin/sh

echo "Waiting for postgres..."
# (여기에 필요하면 DB health check 루프 추가 가능)
echo "PostgreSQL started"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
