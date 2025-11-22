from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import bcrypt
import mysql.connector
from mysql.connector import pooling
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from functools import wraps
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Database Connection Pool
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'kholna'),
    'database': os.getenv('DB_NAME', 'claude_db'),
    'pool_name': 'insurance_pool',
    'pool_size': 10
}

try:
    connection_pool = pooling.MySQLConnectionPool(**db_config)
except mysql.connector.Error as e:
    print(f"Error creating connection pool: {e}")
    connection_pool = None

def get_db_connection():
    """Get database connection from pool"""
    if connection_pool:
        return connection_pool.get_connection()
    return None

def login_required(role=None):
    """Decorator to protect routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Unauthorized access', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== AUTH ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')
        
        if not user_id or not password:
            flash('Please provide both User ID and Password', 'danger')
            return render_template('login.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return render_template('login.html')
        
        cursor = conn.cursor(dictionary=True)
        
        # Determine if Admin or Agent
        if len(user_id) == 5:
            query = "SELECT Admin_id as id, Name, Password, 'admin' as role FROM Admin WHERE Admin_id = %s"
        elif len(user_id) == 7:
            query = "SELECT Agency_code as id, Name, Password, 'agent' as role FROM Agent WHERE Agency_code = %s"
        else:
            flash('Invalid User ID format', 'danger')
            cursor.close()
            conn.close()
            return render_template('login.html')
        
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['name'] = user['Name']
            session['role'] = user['role']
            session['csrf_token'] = secrets.token_hex(16)
            flash(f'Welcome, {user["Name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')


@app.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    if role not in ['admin', 'agent']:
        flash('Invalid registration type', 'danger')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            cursor.close()
            conn.close()
            return render_template('register.html', role=role, admins=get_admins(cursor) if role == 'agent' else None)
        
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            if role == 'admin':
                # Auto-generate Admin ID
                cursor.execute("SELECT MAX(CAST(Admin_id AS UNSIGNED)) as max_id FROM Admin")
                result = cursor.fetchone()
                next_id = (result['max_id'] or 10000) + 1
                admin_id = str(next_id).zfill(5)
                
                query = """INSERT INTO Admin (Admin_id, Branch_id, Name, Mobile, Email, DOB, Designation, Password)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (
                    admin_id,
                    request.form.get('branch_id'),
                    request.form.get('name'),
                    request.form.get('mobile'),
                    request.form.get('email'),
                    request.form.get('dob'),
                    request.form.get('designation'),
                    hashed_password
                )
                
                cursor.execute(query, values)
                conn.commit()
                
                cursor.close()
                conn.close()
                
                # Show success page with generated ID
                return render_template('registration_success.html', 
                                     role='admin',
                                     user_id=admin_id,
                                     name=request.form.get('name'),
                                     email=request.form.get('email'))
                
            else:  # agent
                # Auto-generate Agency Code
                cursor.execute("SELECT MAX(CAST(Agency_code AS UNSIGNED)) as max_code FROM Agent")
                result = cursor.fetchone()
                next_code = (result['max_code'] or 1000000) + 1
                agency_code = str(next_code).zfill(7)
                
                query = """INSERT INTO Agent (Agency_code, Admin_id, Branch_id, Name, Mobile, Email, Password)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                values = (
                    agency_code,
                    request.form.get('admin_id'),
                    request.form.get('branch_id'),
                    request.form.get('name'),
                    request.form.get('mobile'),
                    request.form.get('email'),
                    hashed_password
                )
                
                cursor.execute(query, values)
                conn.commit()
                
                cursor.close()
                conn.close()
                
                # Show success page with generated code
                return render_template('registration_success.html',
                                     role='agent',
                                     user_id=agency_code,
                                     name=request.form.get('name'),
                                     email=request.form.get('email'))
            
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            cursor.close()
            conn.close()
    
    # GET request - show form
    admins = None
    if role == 'agent':
        admins = get_admins(cursor)
    
    cursor.close()
    conn.close()
    return render_template('register.html', role=role, admins=admins)

def get_admins(cursor):
    """Helper function to get all admins for agent registration"""
    cursor.execute("SELECT Admin_id, Name, Branch_id FROM Admin ORDER BY Admin_id")
    return cursor.fetchall()

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required()
def dashboard():
    return render_template('dashboard.html')

# ==================== PLAN MANAGEMENT (ADMIN) ====================

@app.route('/plans')
@login_required(role='admin')
def plans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Plan ORDER BY Plan_no")
    plans = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('plans.html', plans=plans)

@app.route('/plans/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_plan():
    if request.method == 'POST':
        # Validate Sum Assured
        min_sa = float(request.form.get('min_sa'))
        max_sa = float(request.form.get('max_sa'))
        if min_sa > max_sa:
            flash('Minimum Sum Assured cannot exceed Maximum', 'danger')
            return render_template('add_plan.html')
        
        # Validate Age
        min_age = int(request.form.get('min_age'))
        max_age = int(request.form.get('max_age'))
        if min_age > max_age:
            flash('Minimum Age cannot exceed Maximum', 'danger')
            return render_template('add_plan.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = """INSERT INTO Plan (Plan_no, Name, MMA, Min_SA, Max_SA, Min_Age, Max_Age, 
                       T1, T2, T3, T4, P1, P2, P3, P4, Yearly, Half_yearly, Quarterly, Monthly)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = (
                request.form.get('plan_no'),
                request.form.get('name'),
                request.form.get('mma'),
                min_sa, max_sa, min_age, max_age,
                request.form.get('t1'), request.form.get('t2'), 
                request.form.get('t3'), request.form.get('t4'),
                request.form.get('p1'), request.form.get('p2'),
                request.form.get('p3'), request.form.get('p4'),
                bool(request.form.get('yearly')),
                bool(request.form.get('half_yearly')),
                bool(request.form.get('quarterly')),
                bool(request.form.get('monthly'))
            )
            
            cursor.execute(query, values)
            conn.commit()
            flash('Plan added successfully', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('plans'))
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f'Error adding plan: {str(e)}', 'danger')
            cursor.close()
            conn.close()
    
    return render_template('add_plan.html')

@app.route('/plans/edit/<plan_no>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_plan(plan_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            query = """UPDATE Plan SET Name=%s, MMA=%s, Min_SA=%s, Max_SA=%s, Min_Age=%s, Max_Age=%s,
                       T1=%s, T2=%s, T3=%s, T4=%s, P1=%s, P2=%s, P3=%s, P4=%s,
                       Yearly=%s, Half_yearly=%s, Quarterly=%s, Monthly=%s WHERE Plan_no=%s"""
            
            values = (
                request.form.get('name'), request.form.get('mma'),
                request.form.get('min_sa'), request.form.get('max_sa'),
                request.form.get('min_age'), request.form.get('max_age'),
                request.form.get('t1'), request.form.get('t2'),
                request.form.get('t3'), request.form.get('t4'),
                request.form.get('p1'), request.form.get('p2'),
                request.form.get('p3'), request.form.get('p4'),
                bool(request.form.get('yearly')), bool(request.form.get('half_yearly')),
                bool(request.form.get('quarterly')), bool(request.form.get('monthly')),
                plan_no
            )
            
            cursor.execute(query, values)
            conn.commit()
            flash('Plan updated successfully', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('plans'))
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f'Error updating plan: {str(e)}', 'danger')
    
    cursor.execute("SELECT * FROM Plan WHERE Plan_no = %s", (plan_no,))
    plan = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_plan.html', plan=plan)

# ==================== POLICY MANAGEMENT (AGENT) ====================

@app.route('/policies')
@login_required(role='agent')
def policies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT p.*, pl.Name as Plan_Name, ph.Name as Holder_Name 
               FROM Policy p 
               JOIN Plan pl ON p.Plan_no = pl.Plan_no 
               LEFT JOIN Policy_Holder ph ON p.Policy_no = ph.Policy_no
               WHERE p.Agency_code = %s ORDER BY p.Policy_no DESC"""
    cursor.execute(query, (session['user_id'],))
    policies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('policies.html', policies=policies)

@app.route('/policies/add', methods=['GET', 'POST'])
@login_required(role='agent')
def add_policy():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        plan_no = request.form.get('plan_no')
        term = int(request.form.get('term'))
        sum_assured = float(request.form.get('sum_assured'))
        
        # Get DOB and calculate age
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        # Fetch Plan details
        cursor.execute("SELECT * FROM Plan WHERE Plan_no = %s", (plan_no,))
        plan = cursor.fetchone()
        
        if not plan:
            flash('Invalid Plan selected', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('add_policy'))
        
        # Validation
        errors = []
        
        # Age check
        if age < plan['Min_Age'] or age > plan['Max_Age']:
            errors.append(f"Age must be between {plan['Min_Age']} and {plan['Max_Age']}")
        
        # Term check
        if plan['T3'] and plan['T4']:  # Specific type
            valid_terms = [plan['T1'], plan['T2'], plan['T3'], plan['T4']]
            if term not in valid_terms:
                errors.append(f"Term must be one of: {', '.join(map(str, valid_terms))}")
        else:  # Range type
            if term < plan['T1'] or term > plan['T2']:
                errors.append(f"Term must be between {plan['T1']} and {plan['T2']}")
        
        # Sum Assured check
        if sum_assured < plan['Min_SA'] or sum_assured > plan['Max_SA']:
            errors.append(f"Sum Assured must be between {plan['Min_SA']} and {plan['Max_SA']}")
        
        # Maturity check
        if age + term > plan['MMA']:
            errors.append(f"Age + Term cannot exceed Maturity Age of {plan['MMA']}")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('add_policy'))
        
        # Calculate Premium (simplified)
        mode = request.form.get('mode')
        premium = sum_assured / term
        if mode == 'Half-yearly':
            premium = premium / 2
        elif mode == 'Quarterly':
            premium = premium / 4
        elif mode == 'Monthly':
            premium = premium / 12
        
        # Transaction
        try:
            conn.start_transaction()
            
            # Generate Policy Number
            cursor.execute("SELECT MAX(CAST(Policy_no AS UNSIGNED)) as max_no FROM Policy")
            result = cursor.fetchone()
            policy_no = str((result['max_no'] or 100000000) + 1).zfill(9)
            
            # Insert Policy
            doc = datetime.now().strftime('%Y-%m-%d')
            fup = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            policy_query = """INSERT INTO Policy (Policy_no, Plan_no, Agency_code, Premium, DOC, FUP, Status, Mode, Term, Sum_Assured)
                              VALUES (%s, %s, %s, %s, %s, %s, 1, %s, %s, %s)"""
            cursor.execute(policy_query, (policy_no, plan_no, session['user_id'], premium, doc, fup, mode, term, sum_assured))
            
            # Insert Policy Holder
            holder_query = """INSERT INTO Policy_Holder (Policy_no, Name, Address, City, State, Pincode, 
                              Nominee_Name, Nominee_Relation, Gender, Occupation, DOB, Education)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            holder_values = (
                policy_no,
                request.form.get('name'),
                request.form.get('address'),
                request.form.get('city'),
                request.form.get('state'),
                request.form.get('pincode'),
                request.form.get('nominee_name'),
                request.form.get('nominee_relation'),
                request.form.get('gender'),
                request.form.get('occupation'),
                dob_str,
                request.form.get('education')
            )
            cursor.execute(holder_query, holder_values)
            
            # Verify
            cursor.execute("SELECT * FROM Policy_Holder WHERE Policy_no = %s", (policy_no,))
            if cursor.fetchone():
                conn.commit()
                flash(f'Policy {policy_no} created successfully!', 'success')
            else:
                conn.rollback()
                flash('Policy creation verification failed', 'danger')
            
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f'Error creating policy: {str(e)}', 'danger')
        
        cursor.close()
        conn.close()
        return redirect(url_for('policies'))
    
    # GET request - show form
    cursor.execute("SELECT Plan_no, Name FROM Plan ORDER BY Plan_no")
    plans = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_policy.html', plans=plans)

# ==================== PAYMENT MANAGEMENT ====================

@app.route('/payments')
@login_required(role='agent')
def payments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT p.Policy_no, p.Premium, p.FUP, p.Status, ph.Name as Holder_Name
               FROM Policy p
               JOIN Policy_Holder ph ON p.Policy_no = ph.Policy_no
               WHERE p.Agency_code = %s AND p.Status = 1 AND p.FUP IS NOT NULL
               ORDER BY p.FUP"""
    cursor.execute(query, (session['user_id'],))
    policies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('payments.html', policies=policies)

@app.route('/payments/pay/<policy_no>', methods=['GET', 'POST'])
@login_required(role='agent')
def pay_premium(policy_no):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        mode = request.form.get('mode')
        
        # Fetch Policy
        cursor.execute("SELECT * FROM Policy WHERE Policy_no = %s", (policy_no,))
        policy = cursor.fetchone()
        
        if not policy:
            flash('Policy not found', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('payments'))
        
        # Validation
        if policy['Agency_code'] != session['user_id']:
            flash('Unauthorized access to this policy', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('payments'))
        
        if policy['FUP'] is None:
            flash('Policy is matured or inactive', 'warning')
            cursor.close()
            conn.close()
            return redirect(url_for('payments'))
        
        if amount < policy['Premium']:
            flash(f'Payment amount must be at least {policy["Premium"]}', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('pay_premium', policy_no=policy_no))
        
        # Record Payment
        try:
            payment_query = """INSERT INTO Payment (Policy_no, Payment_Mode, Timestamp, Amount)
                               VALUES (%s, %s, %s, %s)"""
            cursor.execute(payment_query, (policy_no, mode, datetime.now(), amount))
            
            # Update FUP using SEL function
            cursor.execute("UPDATE Policy SET FUP = SEL(Policy_no) WHERE Policy_no = %s", (policy_no,))
            
            # Check if policy matured
            cursor.execute("SELECT FUP FROM Policy WHERE Policy_no = %s", (policy_no,))
            updated_policy = cursor.fetchone()
            
            if updated_policy['FUP'] is None:
                cursor.execute("UPDATE Policy SET Status = 0 WHERE Policy_no = %s", (policy_no,))
            
            conn.commit()
            flash('Payment recorded successfully', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('payments'))
            
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f'Payment failed: {str(e)}', 'danger')
    
    # GET request
    cursor.execute("""SELECT p.*, ph.Name as Holder_Name 
                      FROM Policy p 
                      JOIN Policy_Holder ph ON p.Policy_no = ph.Policy_no 
                      WHERE p.Policy_no = %s""", (policy_no,))
    policy = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('pay_premium.html', policy=policy)

# ==================== REPORTS ====================

@app.route('/reports/commission')
@login_required(role='agent')
def commission_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """SELECT Policy_no, Premium, Term, COM(Premium, Term) as Commission 
               FROM Policy WHERE Agency_code = %s"""
    cursor.execute(query, (session['user_id'],))
    policies = cursor.fetchall()
    
    total_commission = sum(p['Commission'] for p in policies)
    
    cursor.close()
    conn.close()
    return render_template('commission_report.html', policies=policies, total=total_commission)

@app.route('/reports/business')
@login_required(role='admin')
def business_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    report_type = request.args.get('type', 'yearly')
    
    if report_type == 'yearly':
        query = """SELECT YEAR(DOC) as Period, COUNT(*) as Policy_Count, 
                   SUM(COM(Premium, Term)) as Total_Commission
                   FROM Policy GROUP BY YEAR(DOC) ORDER BY Period DESC"""
    else:  # monthly
        query = """SELECT DATE_FORMAT(DOC, '%Y-%m') as Period, COUNT(*) as Policy_Count,
                   SUM(COM(Premium, Term)) as Total_Commission
                   FROM Policy GROUP BY DATE_FORMAT(DOC, '%Y-%m') ORDER BY Period DESC"""
    
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('business_report.html', data=data, report_type=report_type)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)