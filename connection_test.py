import mysql.connector
from dotenv import load_dotenv
import os
import sys

def test_connection():
    """Test database connection and display results"""
    load_dotenv()
    
    print("=" * 50)
    print("Insurance Management System")
    print("Database Connection Test")
    print("=" * 50)
    print()
    
    # Get configuration
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASS', ''),
        'database': os.getenv('DB_NAME', 'insurance_db')
    }
    
    print(f"Testing connection to:")
    print(f"  Host: {config['host']}")
    print(f"  User: {config['user']}")
    print(f"  Database: {config['database']}")
    print()
    
    try:
        # Test connection
        print("Attempting to connect...", end=" ")
        conn = mysql.connector.connect(**config)
        print("✓ SUCCESS")
        print()
        
        cursor = conn.cursor(dictionary=True)
        
        # Test Admin table
        print("Checking Admin table...", end=" ")
        cursor.execute("SELECT COUNT(*) as count FROM Admin")
        admin_count = cursor.fetchone()['count']
        print(f"✓ {admin_count} admin(s) found")
        
        # Test Agent table
        print("Checking Agent table...", end=" ")
        cursor.execute("SELECT COUNT(*) as count FROM Agent")
        agent_count = cursor.fetchone()['count']
        print(f"✓ {agent_count} agent(s) found")
        
        # Test Plan table
        print("Checking Plan table...", end=" ")
        cursor.execute("SELECT COUNT(*) as count FROM Plan")
        plan_count = cursor.fetchone()['count']
        print(f"✓ {plan_count} plan(s) found")
        
        # Test Policy table
        print("Checking Policy table...", end=" ")
        cursor.execute("SELECT COUNT(*) as count FROM Policy")
        policy_count = cursor.fetchone()['count']
        print(f"✓ {policy_count} policy(ies) found")
        
        # Test stored functions
        print("Testing COM function...", end=" ")
        cursor.execute("SELECT COM(10000, 20) as result")
        com_result = cursor.fetchone()['result']
        print(f"✓ Result: {com_result}")
        
        print("Testing SEL function...", end=" ")
        cursor.execute("SELECT SEL('100000001') as result")
        sel_result = cursor.fetchone()['result']
        print(f"✓ Result: {sel_result}")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 50)
        print("✓ All tests passed successfully!")
        print("=" * 50)
        print()
        print("Default test credentials:")
        print("  Admin  - User ID: 10001, Password: admin123")
        print("  Agent  - User ID: 1000001, Password: agent123")
        print()
        
        return True
        
    except mysql.connector.Error as e:
        print("✗ FAILED")
        print()
        print("Error details:")
        print(f"  Error Code: {e.errno}")
        print(f"  Error Message: {e.msg}")
        print()
        print("Common solutions:")
        print("  1. Check if MySQL is running: sudo systemctl status mysql")
        print("  2. Verify credentials in .env file")
        print("  3. Ensure database exists: mysql -u root -p < database_setup.sql")
        print()
        return False
        
    except Exception as e:
        print("✗ FAILED")
        print()
        print(f"Unexpected error: {str(e)}")
        print()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)