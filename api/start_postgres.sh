#!/usr/bin/env bash
set -e

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py db init
python manage.py db migrate
python manage.py db upgrade

python main.py
