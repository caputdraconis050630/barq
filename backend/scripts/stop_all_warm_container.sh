#!/bin/bash

docker ps -a --filter "name=warm-python-*" --format "{{.Names}}" | xargs -r docker rm -f