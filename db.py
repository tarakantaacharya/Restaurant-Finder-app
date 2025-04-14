import pymysql
import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Determine if we're running in Cloud Run
def is_running_in_cloud_run():
    # Check for Cloud Run specific environment variables
    return os.getenv('K_SERVICE') is not None

# Get the appropriate database host
def get_db_host():
    cloud_run_host = os.getenv("DATABASE_HOST_CLOUD", "")
    local_host = os.getenv("DATABASE_HOST_LOCAL", "localhost")
    
    # If explicitly set in environment, use that
    if "DATABASE_HOST" in os.environ:
        return os.environ["DATABASE_HOST"]
    
    # Otherwise determine based on environment
    if is_running_in_cloud_run():
        print("Running in Cloud Run, using host:", cloud_run_host)
        return cloud_run_host
    else:
        print("Running locally, using host:", local_host)
        return local_host

# Fetch database config from environment variables
db_config = {
    "host": get_db_host(),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "database": os.getenv("DATABASE_NAME"),
    "port": int(os.getenv("DATABASE_PORT", "3306"))
}

# Print connection info (without password)
print(f"Database connection info: host={db_config['host']}, user={db_config['user']}, db={db_config['database']}, port={db_config['port']}")

# Check if any of the database configurations are missing
for key, value in db_config.items():
    if value is None and key != "host":  # Allow host to be empty for Cloud SQL socket connection
        print(f"Error: Missing environment variable for {key}")
        exit(1)

def get_db_connection():
    try:
        # Check if we're using Cloud SQL socket connection
        socket_path = os.getenv("CLOUD_SQL_CONNECTION_NAME")
        
        if socket_path and is_running_in_cloud_run():
            # Connect using Unix socket for Cloud SQL
            connection = pymysql.connect(
                unix_socket=f'/cloudsql/{socket_path}',
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"],
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=30
            )
        else:
            # Connect using TCP for local development or if socket not configured
            connection = pymysql.connect(
                host=db_config["host"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"],
                port=db_config["port"],
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )
        return connection
    except pymysql.MySQLError as e:
        if hasattr(e, 'args') and len(e.args) > 1:
            print("Database connection failed:", e.args[0], e.args[1])
            print(f"Check if MySQL is running on {db_config['host']}:{db_config['port']}")
        else:
            print("Database connection failed:", e)
            print(f"Check if MySQL is running on {db_config['host']}:{db_config['port']}")
        return None

# Only test connection at import if not in Cloud Run
# In Cloud Run, we'll handle connection at runtime
if not is_running_in_cloud_run():
    conn = get_db_connection()
    if conn:
        print("Database connection test successful")
        conn.close()
    else:
        print("Database connection test failed")