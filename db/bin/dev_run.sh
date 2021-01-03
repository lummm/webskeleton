#!/bin/bash

docker run -d \
       --rm \
       -e POSTGRES_USER=${PGUSER} \
       -e POSTGRES_PASSWORD=${PGPASSWORD} \
       -p 5432:5432 \
       --mount source=${DEV_VOLUME_NAME},target=/var/lib/postgresql/data \
       --name onward_dev_db \
       postgres:13.1
