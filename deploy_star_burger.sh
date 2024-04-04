#!/bin/bash
set -e
cd $1
source venv/bin/activate
git pull
pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
systemctl restart star-back.service
systemctl reload nginx.service
hash=$(git rev-parse HEAD)
source .env
curl --http1.1 -X POST \
  https://api.rollbar.com/api/1/deploy \
  -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"environment": "'"$ENVIRONMENT"'", "revision": "'"$hash"'", "local_username": "'"$USER"'"}'
echo "Деплой успешно произведен"

