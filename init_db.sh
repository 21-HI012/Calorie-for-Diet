#!/bin/bash

while ! mysqladmin ping -h"localhost" --silent; do
    echo "Waiting for database connection..."
    sleep 1
done

echo "Database connected"

set -e

mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<- EOF
CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;
CREATE USER IF NOT EXISTS '$MYSQL_USER'@'%' IDENTIFIED BY '$MYSQL_PASSWORD';
GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO '$MYSQL_USER'@'%';
FLUSH PRIVILEGES;
EOF
