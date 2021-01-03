#!/bin/bash

docker run -it \
       --rm \
       --net=host \
       -e POSTGRES_USER=${PGUSER} \
       -e POSTGRES_PASSWORD=${PGPASSWORD} \
       --entrypoint psql \
       postgres:13.1 \
       -h 0.0.0.0 -U postgres
