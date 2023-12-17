#!/bin/bash

# Check and prompt for LICENSE_KEY if not set
if [ -z "$LICENSE_KEY" ]; then
    read -p "Enter LICENSE_KEY: " LICENSE_KEY
    export LICENSE_KEY
fi

# Check and prompt for CUSTOMER_ID if not set
if [ -z "$CUSTOMER_ID" ]; then
    read -p "Enter CUSTOMER_ID: " CUSTOMER_ID
    export CUSTOMER_ID
fi

# Pull the Docker image
docker pull helloredwing/vector

# Run docker-compose
docker-compose up
