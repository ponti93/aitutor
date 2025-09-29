#!/usr/bin/env python3
"""
Simple test script to verify the AI Tutor Agent setup
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a simple test app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Simple test model
class TestUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def test_database():
    """Test database connection and basic operations"""
    try:
        with app.app_context():
            # Create tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Test insert
            user = TestUser(username='testuser', email='test@example.com')
            db.session.add(user)
            db.session.commit()
            print("✓ Test user created successfully")
            
            # Test query
            found_user = TestUser.query.filter_by(username='testuser').first()
            if found_user:
                print(f"✓ User found: {found_user.username}")
            else:
                print("✗ User not found")
                
            # Clean up
            db.session.delete(found_user)
            db.session.commit()
            print("✓ Test cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    modules_to_test = [
        'flask',
        'flask_sqlalchemy', 
        'flask_login',
        'werkzeug.security',
        'datetime',
        'json',
        'os'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {module}: {e}")
            return False
    
    return True

def main():
    print("🧪 AI Tutor Agent - Setup Test")
    print("=" * 40)
    
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing database...")
    db_ok = test_database()
    
    print("\n" + "=" * 40)
    if imports_ok and db_ok:
        print("🎉 All tests passed! The basic setup is working.")
        print("\nNext steps:")
        print("1. Run 'python app.py' to start the application")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Register a new account and start using the AI Tutor Agent")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
