#!/bin/bash

echo "Stopping all running Docker containers..."
docker stop $(docker ps -q)

echo "Removing all Docker containers..."
docker rm -f $(docker ps -aq)

echo "Deleting all Docker images..."
docker rmi -f $(docker images -q)

echo "All containers stopped, removed, and all Docker images deleted."

source start_fork.sh
source start_phil.sh

bash