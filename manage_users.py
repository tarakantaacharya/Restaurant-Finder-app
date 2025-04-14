#!/usr/bin/env python3
"""
User management script for the restaurant search application.
This script allows you to create, list, update, and delete users.
"""

import os
import sys
import bcrypt
import argparse
from db import get_db_connection

def create_user(name, email, password):
    """Create a new user in the database."""
    connection = get_db_connection()
    if not connection:
        print("Error: Database connection failed")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if the user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"Error: User with email '{email}' already exists")
            cursor.close()
            connection.close()
            return False
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert the new user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, hashed_password.decode('utf-8'))
        )
        connection.commit()
        
        print(f"User '{name}' with email '{email}' created successfully")
        cursor.close()
        connection.close()
        return True
    
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False

def list_users():
    """List all users in the database."""
    connection = get_db_connection()
    if not connection:
        print("Error: Database connection failed")
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        
        if not users:
            print("No users found")
            cursor.close()
            connection.close()
            return True
        
        print("\nUser List:")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<30} {'Email':<30} {'Created At':<20}")
        print("-" * 80)
        
        for user in users:
            print(f"{user['id']:<5} {user['name']:<30} {user['email']:<30} {user['created_at']}")
        
        print("-" * 80)
        print(f"Total users: {len(users)}")
        
        cursor.close()
        connection.close()
        return True
    
    except Exception as e:
        print(f"Error listing users: {str(e)}")
        return False

def update_user(user_id, name=None, email=None, password=None):
    """Update a user in the database."""
    connection = get_db_connection()
    if not connection:
        print("Error: Database connection failed")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if the user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            print(f"Error: User with ID {user_id} not found")
            cursor.close()
            connection.close()
            return False
        
        # Build the update query
        update_parts = []
        params = []
        
        if name:
            update_parts.append("name = %s")
            params.append(name)
        
        if email:
            update_parts.append("email = %s")
            params.append(email)
        
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_parts.append("password_hash = %s")
            params.append(hashed_password.decode('utf-8'))
        
        if not update_parts:
            print("No updates specified")
            cursor.close()
            connection.close()
            return False
        
        # Execute the update query
        query = f"UPDATE users SET {', '.join(update_parts)} WHERE id = %s"
        params.append(user_id)
        cursor.execute(query, params)
        connection.commit()
        
        print(f"User with ID {user_id} updated successfully")
        cursor.close()
        connection.close()
        return True
    
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        return False

def delete_user(user_id):
    """Delete a user from the database."""
    connection = get_db_connection()
    if not connection:
        print("Error: Database connection failed")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if the user exists
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"Error: User with ID {user_id} not found")
            cursor.close()
            connection.close()
            return False
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete user '{user['name']}' with email '{user['email']}'? (y/n): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled")
            cursor.close()
            connection.close()
            return False
        
        # Delete the user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        
        print(f"User with ID {user_id} deleted successfully")
        cursor.close()
        connection.close()
        return True
    
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return False

def main():
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(description='User management for the restaurant search application')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create user command
    create_parser = subparsers.add_parser('create', help='Create a new user')
    create_parser.add_argument('--name', required=True, help='User name')
    create_parser.add_argument('--email', required=True, help='User email')
    create_parser.add_argument('--password', required=True, help='User password')
    
    # List users command
    list_parser = subparsers.add_parser('list', help='List all users')
    
    # Update user command
    update_parser = subparsers.add_parser('update', help='Update a user')
    update_parser.add_argument('--id', required=True, type=int, help='User ID')
    update_parser.add_argument('--name', help='New user name')
    update_parser.add_argument('--email', help='New user email')
    update_parser.add_argument('--password', help='New user password')
    
    # Delete user command
    delete_parser = subparsers.add_parser('delete', help='Delete a user')
    delete_parser.add_argument('--id', required=True, type=int, help='User ID')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_user(args.name, args.email, args.password)
    elif args.command == 'list':
        list_users()
    elif args.command == 'update':
        update_user(args.id, args.name, args.email, args.password)
    elif args.command == 'delete':
        delete_user(args.id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()