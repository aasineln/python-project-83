#!/usr/bin/env bash

source .env
curl -LsSf https://astral.sh/uv/install.sh | sh
make install

DB_NAME=${DATABASE_URL##*/}
echo "Creating database '$DB_NAME'..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -d page_analyzer_dev -f database.sql