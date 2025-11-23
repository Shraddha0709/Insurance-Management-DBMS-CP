#!/usr/bin/env python3
"""
Password Hash Generator and Database Updater
This script generates bcrypt hashes and updates the database
"""

import bcrypt
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def generate_hash(password):
    """Generate bcrypt hash for a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def update_database():
    """Update database with correct password hashes"""
    
    print("=" * 60)
    print("Password Hash Generator & Database Updater")
    print("=" * 60)
    print()
    
    # Generate hashes
    admin_password = "admin123"
    agent_password = "agent123"
    
    admin_hash = generate_hash(admin_password)
    agent_hash = generate_hash(agent_password)
    
    print("Generated Password Hashes:")
    print(f"Admin (admin123): {admin_hash}")
    print(f"Agent (agent123): {agent_hash}")
    print()
    
    # Connect to database
    try:
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASS', ''),
            'database': os.getenv('DB_NAME', 'insurance_db')
        }
        
        print("Connecting to database...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Update Admin password
        print("Updating Admin password...")
        cursor.execute(
            "UPDATE Admin SET Password = %s WHERE Admin_id = '10001'",
            (admin_hash,)
        )
        
        # Update Agent password
        print("Updating Agent password...")
        cursor.execute(
            "UPDATE Agent SET Password = %s WHERE Agency_code = '1000001'",
            (agent_hash,)
        )
        
        conn.commit()
        
        # Verify updates
        cursor.execute("SELECT Admin_id, Name, Password FROM Admin WHERE Admin_id = '10001'")
        admin = cursor.fetchone()
        
        cursor.execute("SELECT Agency_code, Name, Password FROM Agent WHERE Agency_code = '1000001'")
        agent = cursor.fetchone()
        
        print()
        print("✓ Passwords updated successfully!")
        print()
        print("Verification:")
        print(f"  Admin  - ID: {admin[0]}, Name: {admin[1]}")
        print(f"           Hash: {admin[2][:50]}...")
        print(f"  Agent  - ID: {agent[0]}, Name: {agent[1]}")
        print(f"           Hash: {agent[2][:50]}...")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("You can now login with:")
        print("  Admin  - User ID: 10001, Password: admin123")
        print("  Agent  - User ID: 1000001, Password: agent123")
        print("=" * 60)
        print()
        
    except mysql.connector.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

def test_login():
    """Test login functionality"""
    print()
    print("=" * 60)
    print("Testing Login Functionality")
    print("=" * 60)
    print()
    
    try:
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASS', ''),
            'database': os.getenv('DB_NAME', 'insurance_db')
        }
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        # Test Admin login
        print("Testing Admin login (10001/admin123)...")
        cursor.execute("SELECT Password FROM Admin WHERE Admin_id = %s", ('10001',))
        admin = cursor.fetchone()
        
        if admin:
            if bcrypt.checkpw('admin123'.encode('utf-8'), admin['Password'].encode('utf-8')):
                print("✓ Admin login test PASSED")
            else:
                print("✗ Admin login test FAILED - password mismatch")
        else:
            print("✗ Admin not found")
        
        # Test Agent login
        print("Testing Agent login (1000001/agent123)...")
        cursor.execute("SELECT Password FROM Agent WHERE Agency_code = %s", ('1000001',))
        agent = cursor.fetchone()
        
        if agent:
            if bcrypt.checkpw('agent123'.encode('utf-8'), agent['Password'].encode('utf-8')):
                print("✓ Agent login test PASSED")
            else:
                print("✗ Agent login test FAILED - password mismatch")
        else:
            print("✗ Agent not found")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    print()
    choice = input("Choose action:\n  1. Update passwords in database\n  2. Test login\n  3. Both\nEnter choice (1/2/3): ")
    print()
    
    if choice in ['1', '3']:
        update_database()
    
    if choice in ['2', '3']:
        test_login()