#!/bin/sh

cd /app

python manage.py collectstatic --no-input

until python manage.py migrate
do
    echo "DB connection is not ready, trying again soon..."
    sleep 2
done

chmod -R 755 /app/static
watchmedo auto-restart --directory=./ --pattern=*.py --recursive --ignore-patterns=./env/*\;./apps/*/tests/* -- uwsgi --http :$PORT --processes $WORKERS --static-map /static=/app/static --module besteats.wsgi:application
