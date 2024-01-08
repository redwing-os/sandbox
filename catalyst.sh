#!/bin/bash

# Define the Docker image name
DOCKER_IMAGE="helloredwing/catalyst"
HOST="localhost"
PORT="8080"

# Pull the Docker image
echo "Pulling Docker image: $DOCKER_IMAGE..."
docker pull $DOCKER_IMAGE

# Run the Docker container
echo -e "\033[1;44m Running Docker container for $DOCKER_IMAGE on $HOST:$PORT and $HOST:5000 \033[0m"
docker run -d -p 8080:80 -p 5000:5000 $DOCKER_IMAGE
