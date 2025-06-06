#!/bin/bash

echo "📦 Pulling required Docker runtime images..."

# Python
echo "Pulling python:3.10..."
docker pull python:3.10

# Node.js
echo "Pulling node:16..."
docker pull node:16

# Go
echo "Pulling golang:1.21..."
docker pull golang:1.21

echo "✅ All runtime images pulled successfully."
