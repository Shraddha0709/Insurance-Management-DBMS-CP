# Insurance Management System

A comprehensive web-based Insurance Management System built with Python Flask and MySQL.

## Features

### Admin Features
- Manage insurance plans (Create, Read, Update)
- View business reports (Yearly/Monthly)
- Analytics dashboard with charts
- **Auto-generated Admin IDs** - No manual ID entry required

### Agent Features
- Create and manage policies
- Process premium payments
- View commission reports
- Track policy status
- **Auto-generated Agency Codes** - System assigns unique codes
- **Admin Selection** - Choose managing admin from dropdown

## Technology Stack

- **Backend**: Python 3.10+ with Flask
- **Database**: MySQL/MariaDB
- **Authentication**: bcrypt password hashing
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js

## Installation

### Prerequisites
- Python 3.10 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or extract the project**

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup MySQL Database**
```bash
# Login to MySQL
mysql -u root -p

# Run the database setup script
source database_setup.sql
```

4. **Configure Environment Variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

5. **Generate Secret Key**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and paste it as SECRET_KEY in .env
```

6. **Setup Default Passwords**
```bash
# IMPORTANT: Run this to set correct password hashes
python fix_passwords.py
# Choose option 3 (Both) to update passwords and test login
```

7. **Run the Application**

Development mode:
```bash
python app.py
```

Production mode with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

7. **Access the Application**
Open your browser and navigate to: `http://localhost:5000`

## Default Credentials

The database comes with sample accounts for testing:

**Admin Account:**
- User ID: `10001`
- Password: `admin123`

**Agent Account:**
- User ID: `1000001`
- Password: `agent123`

**Important:** Change these passwords in production!

## Project Structure

```
insurance-management-system/
├── app.py                  # Main Flask application
├── database_setup.sql      # Database schema and sample data
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your environment variables (not in git)
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── plans.html
│   ├── add_plan.html
│   ├── edit_plan.html
│   ├── policies.html
│   ├── add_policy.html
│   ├── payments.html
│   ├── pay_premium.html
│   ├── commission_report.html
│   ├── business_report.html
│   ├── 404.html
│   └── 500.html
└── README.md
```

## Database Schema

### Main Tables
- **Admin**: Administrator accounts
- **Agent**: Insurance agent accounts
- **Plan**: Insurance plan definitions
- **Policy**: Individual insurance policies
- **Policy_Holder**: Policy holder information
- **Payment**: Premium payment records

### Stored Functions
- **COM(Premium, Term)**: Calculates commission (Premium × Term × 0.05)
- **SEL(PolicyNo)**: Calculates next payment due date

## Security Features

- ✅ Bcrypt password hashing
- ✅ Parameterized SQL queries (SQL injection prevention)
- ✅ Session management with CSRF tokens
- ✅ Connection pooling for database efficiency
- ✅ Role-based access control
- ✅ Input validation and sanitization

## Usage Guide

### For Admins

1. **Login** with your 5-digit Admin ID
2. **Manage Plans**: Create new insurance plans with terms and conditions
3. **View Reports**: Track business performance with yearly/monthly analytics

### For Agents

1. **Login** with your 7-digit Agency Code
2. **Create Policies**: Add new policies for customers
3. **Process Payments**: Record premium payments when due
4. **Track Commission**: View earnings from all policies

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register/<role>` - User registration
- `GET /logout` - User logout

### Admin Routes
- `GET /plans` - View all plans
- `GET/POST /plans/add` - Add new plan
- `GET/POST /plans/edit/<plan_no>` - Edit plan
- `GET /reports/business` - Business analytics

### Agent Routes
- `GET /policies` - View agent's policies
- `GET/POST /policies/add` - Create new policy
- `GET /payments` - View pending payments
- `GET/POST /payments/pay/<policy_no>` - Process payment
- `GET /reports/commission` - Commission report

## Database Configuration

Edit the `.env` file with your MySQL credentials:

```env
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASS=your_mysql_password
DB_NAME=insurance_db
SECRET_KEY=your_generated_secret_key
```

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### With Nginx (Recommended)

1. Install Nginx
2. Configure reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Variables for Production

- Set `DEBUG=False` in app.py
- Use strong SECRET_KEY
- Enable HTTPS
- Setup database backups
- Configure firewall rules

## Troubleshooting

### Database Connection Issues
```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u root -p -e "SELECT 1"
```

### Python Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Change port in app.py or kill process
lsof -ti:5000 | xargs kill -9
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed for educational and commercial use.

## Support

For issues and questions:
- Check the documentation above
- Review error logs in the console
- Verify database configuration

## Version History

- **v1.0.0** (2024) - Initial release
  - Complete CRUD operations
  - User authentication
  - Payment processing
  - Reporting dashboard

---