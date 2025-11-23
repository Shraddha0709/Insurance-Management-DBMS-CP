#!/usr/bin/env python3
"""
Database Population Script
Generates realistic sample data for the Insurance Management System
"""

import mysql.connector
import bcrypt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import random

load_dotenv()

# Realistic Indian names
FIRST_NAMES = [
    'Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anita', 'Rahul', 'Pooja',
    'Arjun', 'Kavya', 'Suresh', 'Meera', 'Karthik', 'Divya', 'Arun', 'Riya',
    'Sanjay', 'Neha', 'Rohan', 'Anjali', 'Manoj', 'Shreya', 'Nitin', 'Tanvi',
    'Deepak', 'Simran', 'Vishal', 'Isha', 'Gaurav', 'Preeti'
]

LAST_NAMES = [
    'Kumar', 'Sharma', 'Patel', 'Singh', 'Reddy', 'Gupta', 'Verma', 'Joshi',
    'Nair', 'Rao', 'Iyer', 'Shah', 'Mehta', 'Agarwal', 'Malhotra', 'Desai',
    'Pillai', 'Menon', 'Kapoor', 'Choudhury'
]

CITIES = [
    ('Mumbai', 'Maharashtra', '400001'), ('Delhi', 'Delhi', '110001'),
    ('Bangalore', 'Karnataka', '560001'), ('Hyderabad', 'Telangana', '500001'),
    ('Chennai', 'Tamil Nadu', '600001'), ('Kolkata', 'West Bengal', '700001'),
    ('Pune', 'Maharashtra', '411001'), ('Ahmedabad', 'Gujarat', '380001'),
    ('Jaipur', 'Rajasthan', '302001'), ('Lucknow', 'Uttar Pradesh', '226001'),
    ('Kochi', 'Kerala', '682001'), ('Chandigarh', 'Chandigarh', '160001'),
    ('Indore', 'Madhya Pradesh', '452001'), ('Nagpur', 'Maharashtra', '440001'),
    ('Vadodara', 'Gujarat', '390001')
]

OCCUPATIONS = [
    'Software Engineer', 'Business Owner', 'Doctor', 'Teacher', 'Banker',
    'CA', 'Lawyer', 'Architect', 'Consultant', 'Manager', 'Engineer',
    'Government Employee', 'Sales Executive', 'HR Professional', 'Accountant'
]

EDUCATION = [
    'Graduate', 'Post Graduate', 'Professional', 'Doctorate', 'Diploma',
    'B.Tech', 'MBA', 'CA', 'M.Tech', 'B.Com', 'M.Com'
]

RELATIONS = ['Spouse', 'Son', 'Daughter', 'Parent', 'Sibling', 'Mother', 'Father']

def get_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', ''),
        database=os.getenv('DB_NAME', 'insurance_db')
    )

def generate_mobile():
    """Generate random Indian mobile number"""
    return f"{random.choice([98, 97, 96, 95, 94, 93, 92, 91, 90, 89])}{random.randint(10000000, 99999999)}"

def generate_email(name):
    """Generate email from name"""
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'rediffmail.com']
    return f"{name.lower().replace(' ', '.')}@{random.choice(domains)}"

def random_date(start_year, end_year):
    """Generate random date between years"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def populate_admins(cursor, count=5):
    """Create multiple admin accounts"""
    print(f"Creating {count} admin accounts...")
    
    branches = ['BR001', 'BR002', 'BR003', 'BR004', 'BR005']
    designations = ['Manager', 'Senior Manager', 'Team Lead', 'Branch Manager', 'Regional Manager']
    
    for i in range(count):
        admin_id = str(10001 + i).zfill(5)
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        password_hash = bcrypt.hashpw(f'admin{i+1}'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute("""
                INSERT INTO Admin (Admin_id, Branch_id, Name, Mobile, Email, DOB, Designation, Password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                admin_id,
                branches[i],
                name,
                generate_mobile(),
                generate_email(name),
                random_date(1975, 1990).strftime('%Y-%m-%d'),
                designations[i],
                password_hash
            ))
            print(f"  ✓ Admin {admin_id} - {name} (password: admin{i+1})")
        except mysql.connector.IntegrityError:
            print(f"  ⊙ Admin {admin_id} already exists, skipping...")

def populate_agents(cursor, count=15):
    """Create multiple agent accounts"""
    print(f"\nCreating {count} agent accounts...")
    
    # Get admin IDs
    cursor.execute("SELECT Admin_id, Branch_id FROM Admin")
    admins = cursor.fetchall()
    
    for i in range(count):
        agency_code = str(1000001 + i).zfill(7)
        admin = random.choice(admins)
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        password_hash = bcrypt.hashpw(f'agent{i+1}'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute("""
                INSERT INTO Agent (Agency_code, Admin_id, Branch_id, Name, Mobile, Email, Password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                agency_code,
                admin[0],
                admin[1],
                name,
                generate_mobile(),
                generate_email(name),
                password_hash
            ))
            print(f"  ✓ Agent {agency_code} - {name} (password: agent{i+1})")
        except mysql.connector.IntegrityError:
            print(f"  ⊙ Agent {agency_code} already exists, skipping...")

def populate_plans(cursor):
    """Create diverse insurance plans"""
    print("\nCreating insurance plans...")
    
    plans = [
        ('101', 'Term Life Insurance', 70, 500000, 10000000, 18, 60, 10, 30, None, None, 10, 30, None, None, True, True, True, True),
        ('102', 'Whole Life Plan', 80, 100000, 5000000, 18, 65, 15, 40, None, None, 15, 40, None, None, True, True, False, False),
        ('103', 'Money Back Policy', 75, 200000, 3000000, 21, 55, 15, 20, 25, 30, 15, 20, 25, 30, True, True, True, False),
        ('104', 'Child Education Plan', 65, 300000, 2000000, 25, 50, 10, 15, 20, 25, 10, 15, 20, 25, True, True, True, True),
        ('105', 'Pension Plan', 75, 500000, 8000000, 30, 60, 10, 20, 25, 30, 10, 20, 25, 30, True, True, False, False),
        ('106', 'Unit Linked Plan', 70, 100000, 5000000, 18, 55, 10, 15, 20, None, 10, 15, 20, None, True, True, True, True),
        ('107', 'Endowment Plan', 75, 200000, 4000000, 20, 60, 10, 15, 20, 25, 10, 15, 20, 25, True, True, True, False),
        ('108', 'Health Plus Plan', 80, 300000, 10000000, 18, 65, 5, 10, 15, 20, 5, 10, 15, 20, True, True, True, True)
    ]
    
    for plan in plans:
        try:
            cursor.execute("""
                INSERT INTO Plan (Plan_no, Name, MMA, Min_SA, Max_SA, Min_Age, Max_Age, 
                T1, T2, T3, T4, P1, P2, P3, P4, Yearly, Half_yearly, Quarterly, Monthly)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, plan)
            print(f"  ✓ Plan {plan[0]} - {plan[1]}")
        except mysql.connector.IntegrityError:
            print(f"  ⊙ Plan {plan[0]} already exists, skipping...")

def populate_policies(cursor, count=100):
    """Create realistic policies with holders"""
    print(f"\nCreating {count} policies with holders...")
    
    # Get plans and agents
    cursor.execute("SELECT Plan_no, Min_SA, Max_SA, Min_Age, Max_Age, T1, T2, T3, MMA FROM Plan")
    plans = cursor.fetchall()
    
    cursor.execute("SELECT Agency_code FROM Agent")
    agents = [a[0] for a in cursor.fetchall()]
    
    modes = ['Yearly', 'Half-yearly', 'Quarterly', 'Monthly']
    genders = ['Male', 'Female']
    
    policy_start = 100000001
    policies_created = 0
    
    # Create policies spread across last 3 years
    for i in range(count):
        try:
            plan = random.choice(plans)
            agent = random.choice(agents)
            
            # Generate realistic dates (policies from last 3 years)
            doc = random_date(2022, 2024)
            
            # Applicant details
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            holder_name = f"{first_name} {last_name}"
            
            # Age within plan limits
            age = random.randint(plan[3], plan[4])
            dob = doc - timedelta(days=age*365)
            
            # Term selection
            if plan[6]:  # T3 exists (specific terms)
                term = random.choice([t for t in [plan[5], plan[6], plan[7]] if t])
            else:  # Range terms
                term = random.randint(plan[5], plan[6])
            
            # Check maturity age
            if age + term > plan[8]:
                term = plan[8] - age
            
            # Sum assured
            sum_assured = random.randint(int(plan[1]), int(plan[2]))
            sum_assured = round(sum_assured / 100000) * 100000  # Round to lakhs
            
            # Premium calculation (simplified)
            mode = random.choice(modes)
            base_premium = sum_assured / term
            if mode == 'Half-yearly':
                premium = base_premium / 2
            elif mode == 'Quarterly':
                premium = base_premium / 4
            elif mode == 'Monthly':
                premium = base_premium / 12
            else:
                premium = base_premium
            
            premium = round(premium, 2)
            
            # Calculate FUP based on mode and current date
            if mode == 'Yearly':
                fup = doc + timedelta(days=365)
            elif mode == 'Half-yearly':
                fup = doc + timedelta(days=182)
            elif mode == 'Quarterly':
                fup = doc + timedelta(days=91)
            else:  # Monthly
                fup = doc + timedelta(days=30)
            
            # Check if policy is still active
            maturity_date = doc + timedelta(days=term*365)
            today = datetime.now()
            
            if maturity_date < today:
                status = 0  # Matured
                fup = None
            elif fup < today:
                status = 1  # Active but payment overdue
            else:
                status = 1  # Active
            
            policy_no = str(policy_start + i).zfill(9)
            
            # Insert Policy
            cursor.execute("""
                INSERT INTO Policy (Policy_no, Plan_no, Agency_code, Premium, DOC, FUP, Status, Mode, Term, Sum_Assured)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                policy_no, plan[0], agent, premium, 
                doc.strftime('%Y-%m-%d'), 
                fup.strftime('%Y-%m-%d') if fup else None,
                status, mode, term, sum_assured
            ))
            
            # Insert Policy Holder
            city, state, pincode = random.choice(CITIES)
            
            cursor.execute("""
                INSERT INTO Policy_Holder (Policy_no, Name, Address, City, State, Pincode,
                Nominee_Name, Nominee_Relation, Gender, Occupation, DOB, Education)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                policy_no,
                holder_name,
                f"{random.randint(1, 999)} {random.choice(['MG Road', 'Park Street', 'Civil Lines', 'Main Road', 'Station Road'])}",
                city, state, pincode,
                f"{random.choice(FIRST_NAMES)} {last_name}",
                random.choice(RELATIONS),
                random.choice(genders),
                random.choice(OCCUPATIONS),
                dob.strftime('%Y-%m-%d'),
                random.choice(EDUCATION)
            ))
            
            policies_created += 1
            if policies_created % 10 == 0:
                print(f"  ✓ Created {policies_created} policies...")
                
        except Exception as e:
            print(f"  ✗ Error creating policy: {e}")
            continue
    
    print(f"  ✓ Total policies created: {policies_created}")

def populate_payments(cursor):
    """Create payment records for policies"""
    print("\nCreating payment records...")
    
    # Get all active policies
    cursor.execute("""
        SELECT Policy_no, Premium, DOC, Mode, Term 
        FROM Policy 
        WHERE Status = 1
        ORDER BY DOC
    """)
    policies = cursor.fetchall()
    
    payment_modes = ['Cash', 'Cheque', 'Online', 'Card']
    payments_created = 0
    
    for policy in policies:
        policy_no, premium, doc, mode, term = policy
        
        # Calculate how many payments should have been made
        today = datetime.now()
        doc_date = doc if isinstance(doc, datetime) else datetime.strptime(str(doc), '%Y-%m-%d')
        
        if mode == 'Yearly':
            interval_days = 365
        elif mode == 'Half-yearly':
            interval_days = 182
        elif mode == 'Quarterly':
            interval_days = 91
        else:  # Monthly
            interval_days = 30
        
        # Generate past payments
        payment_date = doc_date
        max_payments = (today - doc_date).days // interval_days
        
        # Create 70-90% of expected payments (some overdue)
        payments_to_create = random.randint(int(max_payments * 0.7), int(max_payments * 0.9))
        
        for _ in range(min(payments_to_create, term)):
            try:
                cursor.execute("""
                    INSERT INTO Payment (Policy_no, Payment_Mode, Timestamp, Amount)
                    VALUES (%s, %s, %s, %s)
                """, (
                    policy_no,
                    random.choice(payment_modes),
                    payment_date + timedelta(days=random.randint(0, 5)),  # Paid within 5 days
                    premium * random.uniform(1.0, 1.1)  # Sometimes pay a bit extra
                ))
                payments_created += 1
                
                payment_date += timedelta(days=interval_days)
                
                if payment_date > today:
                    break
                    
            except Exception as e:
                continue
    
    print(f"  ✓ Created {payments_created} payment records")

def main():
    """Main population function"""
    print("=" * 70)
    print("Insurance Management System - Database Population")
    print("=" * 70)
    print()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Connected to database successfully!\n")
        
        # Ask what to populate
        print("What would you like to populate?")
        print("  1. Everything (Recommended)")
        print("  2. Only Admins & Agents")
        print("  3. Only Plans")
        print("  4. Only Policies & Payments")
        print("  5. Custom")
        
        choice = input("\nEnter choice (1-5): ").strip()
        print()
        
        if choice == '1':
            populate_admins(cursor, 5)
            populate_agents(cursor, 15)
            populate_plans(cursor)
            populate_policies(cursor, 100)
            populate_payments(cursor)
            
        elif choice == '2':
            admins = int(input("Number of admins (default 5): ") or 5)
            agents = int(input("Number of agents (default 15): ") or 15)
            populate_admins(cursor, admins)
            populate_agents(cursor, agents)
            
        elif choice == '3':
            populate_plans(cursor)
            
        elif choice == '4':
            policies = int(input("Number of policies (default 100): ") or 100)
            populate_policies(cursor, policies)
            populate_payments(cursor)
            
        elif choice == '5':
            if input("Populate admins? (y/n): ").lower() == 'y':
                count = int(input("  How many? (default 5): ") or 5)
                populate_admins(cursor, count)
                
            if input("Populate agents? (y/n): ").lower() == 'y':
                count = int(input("  How many? (default 15): ") or 15)
                populate_agents(cursor, count)
                
            if input("Populate plans? (y/n): ").lower() == 'y':
                populate_plans(cursor)
                
            if input("Populate policies? (y/n): ").lower() == 'y':
                count = int(input("  How many? (default 100): ") or 100)
                populate_policies(cursor, count)
                
            if input("Populate payments? (y/n): ").lower() == 'y':
                populate_payments(cursor)
        
        conn.commit()
        
        # Show summary
        print("\n" + "=" * 70)
        print("Database Population Summary")
        print("=" * 70)
        
        cursor.execute("SELECT COUNT(*) FROM Admin")
        print(f"Total Admins: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Agent")
        print(f"Total Agents: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Plan")
        print(f"Total Plans: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Policy")
        print(f"Total Policies: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Policy_Holder")
        print(f"Total Policy Holders: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Payment")
        print(f"Total Payments: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT SUM(Premium * Term * 0.05) FROM Policy")
        total_commission = cursor.fetchone()[0] or 0
        print(f"Total Commission: ₹{total_commission:,.2f}")
        
        print("\n" + "=" * 70)
        print("✓ Database populated successfully!")
        print("=" * 70)
        print("\nYou can now:")
        print("  - Login with existing credentials")
        print("  - View realistic data in reports")
        print("  - See populated graphs and charts")
        print()
        print("New account credentials (if created):")
        print("  Admins: admin1, admin2, admin3, etc.")
        print("  Agents: agent1, agent2, agent3, etc.")
        print()
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"\n✗ Database error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()