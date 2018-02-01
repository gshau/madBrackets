#!/bin/bash

cd /app

service postgresql start
su postgres -c "psql --command \"CREATE USER docker WITH SUPERUSER PASSWORD 'docker';\""
python3 /data/load_db.py

/etc/init.d/nginx restart
gunicorn ncaatourney:app
