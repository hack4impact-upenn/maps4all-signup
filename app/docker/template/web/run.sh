#!/bin/bash
echo "starting web server"

if ! [ -e /persists/db_initialized ]
then
  echo "initializing db"
  touch /persists/db_initialized
  cd /app
  python3 manage.py recreate_db
  python3 manage.py setup_prod
fi

cd /app
honcho start -f Proc
