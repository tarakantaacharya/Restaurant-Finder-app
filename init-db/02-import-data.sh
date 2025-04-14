#!/bin/bash

# This script can be used to import data from a CSV file into the MySQL database
# It's included in the Docker container and can be run manually if needed

echo "Waiting for MySQL to start..."
sleep 10

# Check if the CSV file exists
if [ -f "/docker-entrypoint-initdb.d/zomato_data.csv" ]; then
    echo "Importing data from CSV file..."
    
    # Create a temporary SQL file for the LOAD DATA INFILE command
    cat > /tmp/import.sql << EOF
    LOAD DATA INFILE '/docker-entrypoint-initdb.d/zomato_data.csv' 
    INTO TABLE zomato_new 
    FIELDS TERMINATED BY ',' 
    ENCLOSED BY '"' 
    LINES TERMINATED BY '\n' 
    IGNORE 1 ROWS;
EOF

    # Execute the SQL file
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" < /tmp/import.sql
    
    echo "Data import completed."
else
    echo "No CSV file found. Skipping data import."
    echo "You can add your own CSV file named 'zomato_data.csv' to the init-db directory."
fi

echo "Database initialization completed."