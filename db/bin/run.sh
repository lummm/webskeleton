#!/bin/sh


docker run -d \
       --rm \
       --net=host \
       -e POSTGRES_USER=${PGUSER} \
       -e POSTGRES_PASSWORD=${PGPASSWORD} \
       --mount source=onward_dev_db_v,target=/var/lib/postgresql/data \
       --name onward_dev_db \
       postgres:13.1
