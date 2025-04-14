import pymysql
import os
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get connection parameters
host = os.getenv("DATABASE_HOST_LOCAL", "localhost")
user = os.getenv("DATABASE_USER", "root")
password = os.getenv("DATABASE_PASSWORD", "")
database = os.getenv("DATABASE_NAME", "zomato_db")
port = int(os.getenv("DATABASE_PORT", "3306"))

print(f"Checking MySQL connection to {host}:{port}...")
print(f"User: {user}")
print(f"Database: {database}")

# Try to check if the port is open
try:
    print(f"Checking if port {port} is open on {host}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    if result == 0:
        print(f"Port {port} is open on {host}")
    else:
        print(f"Port {port} is closed on {host}")
    sock.close()
except Exception as e:
    print(f"Error checking port: {e}")

# Try to connect to MySQL
try:
    print("Attempting to connect to MySQL...")
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        connect_timeout=5
    )
    
    print("Connection successful!")
    
    # Check if the database exists
    with connection.cursor() as cursor:
        cursor.execute("SHOW DATABASES LIKE %s", (database,))
        result = cursor.fetchone()
        if result:
            print(f"Database '{database}' exists")
        else:
            print(f"Database '{database}' does not exist")
    
    connection.close()
except Exception as e:
    print(f"MySQL connection failed: {e}")
    print("\nPossible solutions:")
    print("1. Make sure MySQL server is running")
    print("2. Check if MySQL is running on the correct port (default is 3306)")
    print("3. Verify your username and password are correct")
    print("4. Ensure the database exists")
    print("5. Check if your firewall is blocking the connection")