#!/bin/bash
set -e
git pull

docker-compose -f docker-compose.yml exec django-web bash -c "pip3 install -r requirements.txt &&
    python3 manage.py collectstatic --noinput &&
    python3 manage.py migrate --noinput"

docker-compose -f docker-compose.yml up -d node-web
docker-compose -f docker-compose.yml restart django-web
docker-compose -f docker-compose.yml restart nginx
hash=$(git rev-parse HEAD)
source .env
curl --http1.1 -X POST \
  https://api.rollbar.com/api/1/deploy \
  -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"environment": "'"$ENVIRONMENT"'", "revision": "'"$hash"'", "local_username": "'"$USER"'"}'
echo "Деплой успешно произведен"

