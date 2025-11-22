-- Insurance Management System Database Schema
-- Drop existing database if needed
DROP DATABASE IF EXISTS insurance_db;
CREATE DATABASE insurance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE insurance_db;

-- ==================== TABLES ====================

-- Admin Table
CREATE TABLE Admin (
    Admin_id CHAR(5) PRIMARY KEY,
    Branch_id VARCHAR(20) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Mobile VARCHAR(15) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    DOB DATE NOT NULL,
    Designation VARCHAR(50) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_branch (Branch_id)
) ENGINE=InnoDB;

-- Agent Table
CREATE TABLE Agent (
    Agency_code CHAR(7) PRIMARY KEY,
    Admin_id CHAR(5),
    Branch_id VARCHAR(20) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Mobile VARCHAR(15) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Admin_id) REFERENCES Admin(Admin_id) ON DELETE SET NULL,
    INDEX idx_admin (Admin_id),
    INDEX idx_branch (Branch_id)
) ENGINE=InnoDB;

-- Plan Table
CREATE TABLE Plan (
    Plan_no CHAR(3) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    MMA INT NOT NULL COMMENT 'Max Maturity Age',
    Min_SA DECIMAL(12,2) NOT NULL COMMENT 'Minimum Sum Assured',
    Max_SA DECIMAL(12,2) NOT NULL COMMENT 'Maximum Sum Assured',
    Min_Age INT NOT NULL,
    Max_Age INT NOT NULL,
    T1 INT COMMENT 'Term 1',
    T2 INT COMMENT 'Term 2',
    T3 INT COMMENT 'Term 3',
    T4 INT COMMENT 'Term 4',
    P1 INT COMMENT 'Payment Term 1',
    P2 INT COMMENT 'Payment Term 2',
    P3 INT COMMENT 'Payment Term 3',
    P4 INT COMMENT 'Payment Term 4',
    Yearly BOOLEAN DEFAULT FALSE,
    Half_yearly BOOLEAN DEFAULT FALSE,
    Quarterly BOOLEAN DEFAULT FALSE,
    Monthly BOOLEAN DEFAULT FALSE,
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (Min_SA <= Max_SA),
    CHECK (Min_Age <= Max_Age)
) ENGINE=InnoDB;

-- Policy Table
CREATE TABLE Policy (
    Policy_no CHAR(9) PRIMARY KEY,
    Plan_no CHAR(3) NOT NULL,
    Agency_code CHAR(7) NOT NULL,
    Premium DECIMAL(12,2) NOT NULL,
    DOC DATE NOT NULL COMMENT 'Date of Commencement',
    FUP DATE COMMENT 'First Unpaid Payment',
    Status TINYINT DEFAULT 1 COMMENT '1=Active, 0=Inactive/Matured',
    Mode ENUM('Yearly', 'Half-yearly', 'Quarterly', 'Monthly') NOT NULL,
    Term INT NOT NULL,
    Sum_Assured DECIMAL(12,2) NOT NULL,
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Plan_no) REFERENCES Plan(Plan_no) ON DELETE RESTRICT,
    FOREIGN KEY (Agency_code) REFERENCES Agent(Agency_code) ON DELETE RESTRICT,
    INDEX idx_agent (Agency_code),
    INDEX idx_plan (Plan_no),
    INDEX idx_doc (DOC),
    INDEX idx_status (Status)
) ENGINE=InnoDB;

-- Policy Holder Table
CREATE TABLE Policy_Holder (
    Policy_no CHAR(9) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(50) NOT NULL,
    State VARCHAR(50) NOT NULL,
    Pincode VARCHAR(10) NOT NULL,
    Nominee_Name VARCHAR(100) NOT NULL,
    Nominee_Relation VARCHAR(50) NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Occupation VARCHAR(100),
    DOB DATE NOT NULL,
    Education VARCHAR(100),
    FOREIGN KEY (Policy_no) REFERENCES Policy(Policy_no) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Payment Table
CREATE TABLE Payment (
    Payment_id INT AUTO_INCREMENT PRIMARY KEY,
    Policy_no CHAR(9) NOT NULL,
    Payment_Mode VARCHAR(50) NOT NULL,
    Timestamp DATETIME NOT NULL,
    Amount DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (Policy_no) REFERENCES Policy(Policy_no) ON DELETE CASCADE,
    INDEX idx_policy (Policy_no),
    INDEX idx_timestamp (Timestamp)
) ENGINE=InnoDB;

-- ==================== STORED FUNCTIONS ====================

-- Commission Calculation Function
DELIMITER //
CREATE FUNCTION COM(premium DECIMAL(12,2), term INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
BEGIN
    RETURN premium * term * 0.05;
END//
DELIMITER ;

-- Next Due Date Calculation Function
DELIMITER //
CREATE FUNCTION SEL(policy_no CHAR(9))
RETURNS DATE
DETERMINISTIC
BEGIN
    DECLARE current_fup DATE;
    DECLARE payment_mode VARCHAR(20);
    DECLARE doc_date DATE;
    DECLARE term_years INT;
    DECLARE maturity_date DATE;
    DECLARE next_due DATE;
    
    -- Get policy details
    SELECT FUP, Mode, DOC, Term INTO current_fup, payment_mode, doc_date, term_years
    FROM Policy
    WHERE Policy_no = policy_no;
    
    -- Calculate maturity date
    SET maturity_date = DATE_ADD(doc_date, INTERVAL term_years YEAR);
    
    -- If no current FUP or already matured, return NULL
    IF current_fup IS NULL OR current_fup >= maturity_date THEN
        RETURN NULL;
    END IF;
    
    -- Calculate next due date based on mode
    CASE payment_mode
        WHEN 'Yearly' THEN
            SET next_due = DATE_ADD(current_fup, INTERVAL 1 YEAR);
        WHEN 'Half-yearly' THEN
            SET next_due = DATE_ADD(current_fup, INTERVAL 6 MONTH);
        WHEN 'Quarterly' THEN
            SET next_due = DATE_ADD(current_fup, INTERVAL 3 MONTH);
        WHEN 'Monthly' THEN
            SET next_due = DATE_ADD(current_fup, INTERVAL 1 MONTH);
        ELSE
            SET next_due = NULL;
    END CASE;
    
    -- If next due is beyond maturity, return NULL
    IF next_due >= maturity_date THEN
        RETURN NULL;
    END IF;
    
    RETURN next_due;
END//
DELIMITER ;

-- ==================== SAMPLE DATA ====================

-- Insert Sample Admin
-- Note: Run fix_passwords.py after database setup to set correct password hashes
INSERT INTO Admin (Admin_id, Branch_id, Name, Mobile, Email, DOB, Designation, Password)
VALUES 
('10001', 'BR001', 'John Admin', '9876543210', 'admin@insurance.com', '1985-05-15', 'Manager', 
 'temp_password_run_fix_script'); -- password will be: admin123

-- Insert Sample Agent
INSERT INTO Agent (Agency_code, Admin_id, Branch_id, Name, Mobile, Email, Password)
VALUES 
('1000001', '10001', 'BR001', 'Jane Agent', '9876543211', 'agent@insurance.com',
 'temp_password_run_fix_script'); -- password will be: agent123

-- Insert Sample Plans
INSERT INTO Plan (Plan_no, Name, MMA, Min_SA, Max_SA, Min_Age, Max_Age, T1, T2, T3, T4, P1, P2, P3, P4, Yearly, Half_yearly, Quarterly, Monthly)
VALUES 
('101', 'Whole Life Plan', 80, 100000, 5000000, 18, 65, 10, 30, NULL, NULL, 10, 30, NULL, NULL, TRUE, TRUE, FALSE, FALSE),
('102', 'Term Insurance', 70, 50000, 10000000, 18, 60, 5, 40, NULL, NULL, 5, 40, NULL, NULL, TRUE, TRUE, TRUE, TRUE),
('103', 'Money Back Plan', 75, 200000, 3000000, 21, 55, 15, 20, 25, 30, 15, 20, 25, 30, TRUE, TRUE, TRUE, FALSE);

-- Insert Sample Policy
INSERT INTO Policy (Policy_no, Plan_no, Agency_code, Premium, DOC, FUP, Status, Mode, Term, Sum_Assured)
VALUES 
('100000001', '101', '1000001', 50000.00, '2024-01-01', '2025-01-01', 1, 'Yearly', 20, 1000000.00);

-- Insert Sample Policy Holder
INSERT INTO Policy_Holder (Policy_no, Name, Address, City, State, Pincode, Nominee_Name, Nominee_Relation, Gender, Occupation, DOB, Education)
VALUES 
('100000001', 'Rajesh Kumar', '123 MG Road', 'Mumbai', 'Maharashtra', '400001', 'Priya Kumar', 'Spouse', 'Male', 'Software Engineer', '1990-03-15', 'Graduate');

-- ==================== VIEWS FOR REPORTING ====================

-- View for Active Policies
CREATE VIEW active_policies AS
SELECT 
    p.Policy_no,
    p.Premium,
    p.DOC,
    p.FUP,
    p.Mode,
    p.Term,
    p.Sum_Assured,
    pl.Name as Plan_Name,
    ph.Name as Holder_Name,
    a.Name as Agent_Name,
    COM(p.Premium, p.Term) as Commission
FROM Policy p
JOIN Plan pl ON p.Plan_no = pl.Plan_no
JOIN Policy_Holder ph ON p.Policy_no = ph.Policy_no
JOIN Agent a ON p.Agency_code = a.Agency_code
WHERE p.Status = 1;

-- View for Payment History
CREATE VIEW payment_history AS
SELECT 
    pm.Payment_id,
    pm.Policy_no,
    ph.Name as Holder_Name,
    pm.Amount,
    pm.Payment_Mode,
    pm.Timestamp,
    p.Premium
FROM Payment pm
JOIN Policy p ON pm.Policy_no = p.Policy_no
JOIN Policy_Holder ph ON p.Policy_no = ph.Policy_no
ORDER BY pm.Timestamp DESC;

-- ==================== INDEXES FOR PERFORMANCE ====================

-- Additional indexes for common queries
CREATE INDEX idx_policy_fup_status ON Policy(FUP, Status);
CREATE INDEX idx_payment_timestamp ON Payment(Timestamp);
CREATE INDEX idx_policy_doc_year ON Policy((YEAR(DOC)));

-- ==================== GRANTS ====================
-- Grant privileges (adjust username/password as needed)
-- GRANT ALL PRIVILEGES ON insurance_db.* TO 'insurance_user'@'localhost' IDENTIFIED BY 'secure_password';
-- FLUSH PRIVILEGES;