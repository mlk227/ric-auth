#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "database started"

python manage.py migrate

if [ "${RESET_DB}" ]; then
    python manage.py flush --noinput
    python manage.py loaddata docker/test/fixtures/fixtures.json
fi    

python manage.py collectstatic --noinput
cp -r docker/test/media/* /mnt/shared_volumes/media/

python manage.py runserver 0.0.0.0:8001
