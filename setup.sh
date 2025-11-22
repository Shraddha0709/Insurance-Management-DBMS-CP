#!/bin/bash

# Insurance Management System - Automated Setup Script
# This script automates the installation and setup process

set -e  # Exit on any error

echo "=========================================="
echo "Insurance Management System Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if Python 3 is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check if MySQL is installed
echo "Checking MySQL installation..."
if ! command -v mysql &> /dev/null; then
    print_error "MySQL is not installed. Please install MySQL 8.0 or higher."
    exit 1
fi

MYSQL_VERSION=$(mysql --version | cut -d' ' -f6 | cut -d',' -f1)
print_success "MySQL $MYSQL_VERSION found"

# Create virtual environment
echo ""
print_info "Creating Python virtual environment..."
if [ -d "venv" ]; then
    print_info "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Install Python dependencies
echo ""
print_info "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Python dependencies installed"

# Setup .env file
echo ""
if [ -f ".env" ]; then
    print_info ".env file already exists. Skipping..."
else
    print_info "Creating .env file..."
    
    read -p "Enter MySQL host [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Enter MySQL username [root]: " DB_USER
    DB_USER=${DB_USER:-root}
    
    read -sp "Enter MySQL password: " DB_PASS
    echo ""
    
    read -p "Enter database name [insurance_db]: " DB_NAME
    DB_NAME=${DB_NAME:-insurance_db}
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    cat > .env << EOF
# Database Configuration
DB_HOST=$DB_HOST
DB_USER=$DB_USER
DB_PASS=$DB_PASS
DB_NAME=$DB_NAME

# Application Secret Key
SECRET_KEY=$SECRET_KEY
EOF
    
    print_success ".env file created"
fi

# Setup database
echo ""
print_info "Setting up database..."
read -p "Do you want to setup the database now? (y/n): " SETUP_DB

if [ "$SETUP_DB" = "y" ] || [ "$SETUP_DB" = "Y" ]; then
    # Load .env variables
    source .env
    
    print_info "Creating database and tables..."
    mysql -u $DB_USER -p$DB_PASS < database_setup.sql
    
    if [ $? -eq 0 ]; then
        print_success "Database setup completed successfully"
    else
        print_error "Database setup failed. Please check your credentials and try again."
        exit 1
    fi
else
    print_info "Skipping database setup. You can run 'mysql -u root -p < database_setup.sql' manually."
fi

# Create necessary directories
echo ""
print_info "Creating necessary directories..."
mkdir -p templates static logs
print_success "Directories created"

# Final instructions
echo ""
echo "=========================================="
print_success "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Default credentials for testing:"
echo "  Admin  - User ID: 10001, Password: admin123"
echo "  Agent  - User ID: 1000001, Password: agent123"
echo ""
echo "To start the application:"
echo "  Development: python app.py"
echo "  Production:  gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "Access the application at: http://localhost:5000"
echo ""
print_info "Remember to change default passwords in production!"
echo ""