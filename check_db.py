import pymysql
import os
import sys
import time
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Determine if we're running in Cloud Run
def is_running_in_cloud_run():
    # Check for Cloud Run specific environment variables
    return os.getenv('K_SERVICE') is not None

# Get the appropriate database host
def get_db_host():
    # If explicitly set in environment, use that
    if "DATABASE_HOST" in os.environ:
        return os.environ["DATABASE_HOST"]
    
    # Otherwise determine based on environment
    if is_running_in_cloud_run():
        return os.getenv("DATABASE_HOST_CLOUD", "")
    else:
        return os.getenv("DATABASE_HOST_LOCAL", "localhost")

# Get connection parameters
host = get_db_host()
user = os.getenv("DATABASE_USER", "root")
password = os.getenv("DATABASE_PASSWORD", "")
database = os.getenv("DATABASE_NAME", "zomato_db")
port = int(os.getenv("DATABASE_PORT", "3306"))
socket_path = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")

# Print connection details (without password)
print(f"Attempting to connect to database:")
print(f"Host: {host}")
print(f"User: {user}")
print(f"Database: {database}")
print(f"Port: {port}")
print(f"Running in Cloud Run: {is_running_in_cloud_run()}")
if socket_path:
    print(f"Cloud SQL Connection: {socket_path}")

# Try to resolve the hostname if not using socket
if host and not is_running_in_cloud_run():
    try:
        print(f"Resolving hostname {host}...")
        ip_address = socket.gethostbyname(host)
        print(f"Hostname {host} resolved to {ip_address}")
    except Exception as e:
        print(f"Failed to resolve hostname {host}: {e}")

# Try to connect to the database
max_attempts = 3
for attempt in range(1, max_attempts + 1):
    try:
        print(f"Connection attempt {attempt}/{max_attempts}...")
        
        # Connect to the database
        if socket_path and is_running_in_cloud_run():
            # Connect using Unix socket for Cloud SQL
            connection = pymysql.connect(
                unix_socket=f'/cloudsql/{socket_path}',
                user=user,
                password=password,
                database=database,
                connect_timeout=30
            )
        else:
            # Connect using TCP for local development
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                connect_timeout=10
            )
        
        # Execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Query result: {result}")
        
        # Close the connection
        connection.close()
        print("Database connection successful!")
        sys.exit(0)
    except Exception as e:
        print(f"Database connection attempt {attempt} failed: {e}")
        if attempt < max_attempts:
            print(f"Waiting before retry...")
            time.sleep(2)
        else:
            print("All connection attempts failed")
            sys.exit(1)