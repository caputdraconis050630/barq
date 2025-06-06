#!/bin/bash

export UVICORN_HOST=0.0.0.0
export UVICORN_PORT=8000

echo "Starting server..."
uvicorn app.main:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --reload
