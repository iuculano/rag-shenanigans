#!/bin/bash

DATABASE_LOCATION=/var/database
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

sudo mkdir $DATABASE_LOCATION

docker run --name pgvector \
    -e POSTGRES_USER=$DATABASE_USER \
    -e POSTGRES_PASSWORD=$DATABASE_PASSWORD \
    -v $DATABASE_LOCATION:/var/lib/postgresql/data \
    -p 5432:5432 \
    -d pgvector/pgvector:pg16

PG_CONN_STR="postgresql://$DATABASE_USER:$DATABASE_PASSWORD@localhost:5432/postgres"
echo $PG_CONN_STR
