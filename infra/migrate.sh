#!/bin/bash

docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py loaddb
docker-compose exec backend python manage.py createsuperuser --no-input
docker-compose exec backend python manage.py collectstatic --no-input
