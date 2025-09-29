#!/usr/bin/env python3
"""
PostgreSQL Setup Script for AI Tutor Agent
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def create_database():
    """Create the aitutor database in PostgreSQL"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="incorrect"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'aitutor'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE aitutor")
            print("✅ Database 'aitutor' created successfully")
        else:
            print("✅ Database 'aitutor' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def test_connection():
    """Test connection to the aitutor database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="aitutor",
            user="postgres",
            password="incorrect"
        )
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False

def main():
    print("🔧 Setting up PostgreSQL for AI Tutor Agent")
    print("=" * 50)
    
    print("\n1. Creating database...")
    if not create_database():
        print("❌ Failed to create database")
        return
    
    print("\n2. Testing connection...")
    if not test_connection():
        print("❌ Failed to connect to database")
        return
    
    print("\n" + "=" * 50)
    print("🎉 PostgreSQL setup completed successfully!")
    print("\nNext steps:")
    print("1. Stop the current application (Ctrl+C)")
    print("2. Restart the application: python app_simple.py")
    print("3. The application will automatically create all tables")
    print("4. Register a new account and test the functionality")

if __name__ == '__main__':
    main()
