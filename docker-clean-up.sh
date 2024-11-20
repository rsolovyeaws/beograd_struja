#!/bin/bash

echo "Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null

echo "Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null

echo "Removing all volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null

echo "Removing all networks (except default)..."
docker network rm $(docker network ls -q) 2>/dev/null

echo "Removing all images..."
docker rmi $(docker images -q) --force 2>/dev/null

echo "Pruning all build cache..."
docker builder prune --all --force

echo "Running a full system prune..."
docker system prune --all --volumes --force

echo "Docker environment cleaned up successfully!"
