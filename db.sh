#!/bin/bash

# Deprecated #

# Wait for Cassandra to be fully operational
echo "Waiting for Cassandra to be ready..."
until cqlsh -e "describe keyspaces"; do
    sleep 1
done

# Check if keyspace and tables already exist
KEYSPACE="redwing_keyspace"

# Function to check if a keyspace exists
keyspace_exists() {
    cqlsh -e "DESCRIBE KEYSPACE $1" > /dev/null 2>&1
}

# Function to check if a table exists
table_exists() {
    cqlsh -e "DESCRIBE TABLE $1.$2" > /dev/null 2>&1
}

# Create keyspace if it doesn't exist
if ! keyspace_exists $KEYSPACE; then
    echo "Creating keyspace: $KEYSPACE"
    cqlsh -e "CREATE KEYSPACE $KEYSPACE WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '3'};"  # Adjust replication strategy as needed
fi

# Create tables if they don't exist
create_table_if_not_exists() {
    if ! table_exists $KEYSPACE $1; then
        echo "Creating table: $1 in $KEYSPACE"
        # Add your CREATE TABLE statement here
    fi
}

create_table_if_not_exists "vectors"
create_table_if_not_exists "default"

echo "Cassandra initialization completed."
