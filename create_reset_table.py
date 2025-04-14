from db import get_db_connection

def create_password_reset_table():
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'password_reset_tokens'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating password_reset_tokens table...")
            
            # Create the table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry DATETIME NOT NULL,
                used TINYINT(1) DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # Add index
            cursor.execute("CREATE INDEX idx_token ON password_reset_tokens(token)")
            
            connection.commit()
            print("Table created successfully")
        else:
            print("password_reset_tokens table already exists")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        return False

if __name__ == "__main__":
    create_password_reset_table()