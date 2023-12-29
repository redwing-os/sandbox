#!/bin/bash

# Load the .env file and extract the REPLACEMENT_IP
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found. Exiting."
    exit 1
fi

# Use the environment variable for the replacement IP
replacement_ip=$REPLACEMENT_IP

# Check if the IP is set
if [ -z "$replacement_ip" ]; then
    echo "No replacement IP set. Exiting."
    exit 1
fi

# Regex pattern to match both 'localhost:50051' and '127.0.0.1:5001'
pattern="(localhost:50051|127.0.0.1:5001)"

# Find and replace in all Python files within the current directory and subdirectories
find ./ -type f -name "*.py" -exec sed -i "s/${pattern}/${replacement_ip}/g" {} +

echo "Replacement complete."
