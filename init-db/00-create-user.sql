-- Grant all privileges to the root user
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Tarak@2024';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- Create a specific user for the application if it doesn't exist
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED WITH mysql_native_password BY 'Tarak@2024';
GRANT ALL PRIVILEGES ON zomato_db.* TO 'app_user'@'%';

-- Allow connections from any host
CREATE USER IF NOT EXISTS 'root'@'172.18.0.%' IDENTIFIED WITH mysql_native_password BY 'Tarak@2024';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'172.18.0.%' WITH GRANT OPTION;

-- Apply changes
FLUSH PRIVILEGES;