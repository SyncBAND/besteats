#!/bin/sh

cd /app

watchmedo auto-restart --directory=./ --pattern=*.py --recursive --ignore-patterns=./env/*\;./apps/*/tests/* -- celery -A besteats worker -B -c 2 -l info
