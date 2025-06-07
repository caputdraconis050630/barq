#!/bin/bash

# Path
SCRIPT_DIR=$(cd $(dirname $0); pwd)

# CouchDB UP
docker-compose -f $SCRIPT_DIR/docker-compose.yml up -d