#!/usr/bin/env bash

source .env
curl -LsSf https://astral.sh/uv/install.sh | sh
make install

DB_NAME=${DATABASE_URL##*/}
echo "Creating database '$DB_NAME'..."
psql -d "$DATABASE_URL" -c "CREATE DATABASE $DB_NAME;"
psql -d "$DATABASE_URL" -f database.sql