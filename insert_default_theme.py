import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to the database
try:
    connection = mysql.connector.connect(
        host=os.getenv('DATABASE_HOST', 'localhost'),
        user=os.getenv('DATABASE_USER', 'root'),
        password=os.getenv('DATABASE_PASSWORD', ''),
        database=os.getenv('DATABASE_NAME', 'zomato_db'),
        port=int(os.getenv('DATABASE_PORT', '3306'))
    )
    
    cursor = connection.cursor()
    
    # Insert the default color theme
    cursor.execute("""
    INSERT INTO site_settings (setting_key, setting_value) 
    VALUES ('color_theme', 'orange')
    """)
    
    connection.commit()
    print("Default color theme inserted successfully")
    
    # Close the connection
    cursor.close()
    connection.close()
    
except mysql.connector.Error as err:
    print(f"Error: {err}")