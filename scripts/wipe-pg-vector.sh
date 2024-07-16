#!/bin/bash

MOUNT=$(docker inspect pgvector | jq -r '.[0].Mounts[] | select(.Type == "bind") | .Source')

sudo rm -rf $MOUNT
docker stop pgvector && docker rm -f pgvector
