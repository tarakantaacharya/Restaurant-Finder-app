import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            user=os.getenv('DATABASE_USER', 'root'),
            password=os.getenv('DATABASE_PASSWORD', ''),
            database=os.getenv('DATABASE_NAME', 'zomato_db'),
            port=int(os.getenv('DATABASE_PORT', '3306')),
            autocommit=True
        )
        # Return the connection
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def create_site_settings_table():
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return False
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Create site_settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `site_settings` (
          `id` int NOT NULL AUTO_INCREMENT,
          `setting_key` varchar(255) NOT NULL UNIQUE,
          `setting_value` text NOT NULL,
          `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Check if color_theme setting already exists
        cursor.execute("SELECT COUNT(*) as count FROM site_settings WHERE setting_key = 'color_theme'")
        result = cursor.fetchone()
        
        # Insert default color theme if it doesn't exist
        print(f"Current count: {result}")
        if result['count'] == 0:
            cursor.execute("""
            INSERT INTO site_settings (setting_key, setting_value) 
            VALUES ('color_theme', 'orange')
            """)
            print("Default color theme setting created")
        
        # Add is_admin column to users table if it doesn't exist
        try:
            cursor.execute("SHOW COLUMNS FROM users LIKE 'is_admin'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE")
                print("Added is_admin column to users table")
                
                # Set the default admin user as admin
                cursor.execute("UPDATE users SET is_admin = TRUE WHERE email = 'admin@example.com'")
                print("Set admin@example.com as admin")
        except Exception as e:
            print(f"Error checking/adding is_admin column: {e}")
        
        connection.commit()
        print("Site settings table created successfully")
        return True
    
    except mysql.connector.Error as err:
        print(f"Error creating site_settings table: {err}")
        return False
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_site_settings_table()