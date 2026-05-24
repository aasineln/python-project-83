#!/usr/bin/env bash

source .env
curl -LsSf https://astral.sh/uv/install.sh | sh
make install

DB_NAME=${DATABASE_URL##*/}
echo "Creating database '$DB_NAME'..."
psql -U postgres -c "CREATE DATABASE $DB_NAME;"
psql -U postgres -d $DB_NAME -f database.sql