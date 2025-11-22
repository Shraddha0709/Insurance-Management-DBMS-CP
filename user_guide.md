# User Guide - Registration & Login

## 📝 New User Registration

### For Admins

#### Step 1: Access Registration Page
- Go to: `http://localhost:5000`
- Click **"Register as Admin"**

#### Step 2: Fill Registration Form
Required information:
- **Branch ID** (e.g., BR001)
- **Full Name**
- **Mobile Number** (10 digits)
- **Email Address**
- **Date of Birth**
- **Designation** (e.g., Manager, Team Lead)
- **Password** (minimum 6 characters)
- **Confirm Password**

> ⚠️ **Note:** You don't need to enter an Admin ID - it will be auto-generated!

#### Step 3: Submit & Save Your ID
After successful registration:
- ✅ You'll see your **5-digit Admin ID** (e.g., `10001`)
- 📋 **IMPORTANT:** Click "Copy User ID" or write it down
- 🔐 Use this ID to login

#### Step 4: Login
- Go to login page
- Enter your **Admin ID** (5 digits)
- Enter your **password**
- Click **Login**

---

### For Agents

#### Step 1: Access Registration Page
- Go to: `http://localhost:5000`
- Click **"Register as Agent"**

#### Step 2: Fill Registration Form
Required information:
- **Select Managing Admin** (dropdown)
- **Branch ID** (e.g., BR001)
- **Full Name**
- **Mobile Number** (10 digits)
- **Email Address**
- **Date of Birth**
- **Password** (minimum 6 characters)
- **Confirm Password**

> ⚠️ **Note:** You don't need to enter an Agency Code - it will be auto-generated!

#### Step 3: Submit & Save Your Code
After successful registration:
- ✅ You'll see your **7-digit Agency Code** (e.g., `1000001`)
- 📋 **IMPORTANT:** Click "Copy User ID" or write it down
- 🔐 Use this code to login

#### Step 4: Login
- Go to login page
- Enter your **Agency Code** (7 digits)
- Enter your **password**
- Click **Login**

---

## 🔐 Login Instructions

### Identifying Your User Type

The system automatically identifies whether you're an Admin or Agent based on ID length:
- **5 digits** → Admin account
- **7 digits** → Agent account

### Login Steps

1. Go to: `http://localhost:5000/login`

2. Enter your User ID:
   - Admin: 5-digit ID (e.g., `10001`)
   - Agent: 7-digit code (e.g., `1000001`)

3. Enter your password

4. Click **Login**

5. You'll be redirected to your dashboard

---

## 🎯 Default Test Accounts

For testing purposes, the system comes with pre-configured accounts:

### Admin Account
```
User ID:  10001
Password: admin123
```

### Agent Account
```
User ID:  1000001
Password: agent123
```

> 🔒 **Security:** Change these passwords in production!

---

## 🛠️ What Can Each User Do?

### Admin Dashboard

After logging in as Admin, you can:

1. **Manage Plans**
   - View all insurance plans
   - Create new plans
   - Edit existing plans
   - Set terms, premiums, and conditions

2. **View Reports**
   - Yearly business reports
   - Monthly business reports
   - Visual charts and graphs
   - Commission overview

3. **Analytics**
   - Total policies count
   - Revenue statistics
   - Performance metrics

### Agent Dashboard

After logging in as Agent, you can:

1. **Manage Policies**
   - Create new policies for customers
   - View all your policies
   - Track policy status
   - See policy details

2. **Process Payments**
   - View pending payments
   - Record premium payments
   - Track overdue policies
   - Update payment status

3. **Commission Reports**
   - View your earnings
   - See commission breakdown
   - Track total commission
   - Policy-wise commission details

---

## 📊 Sample Workflow

### Admin Workflow

```
Login → Dashboard → Manage Plans
                  ↓
         Create Insurance Plan
                  ↓
         View Business Reports
                  ↓
         Analyze Performance
```

### Agent Workflow

```
Login → Dashboard → Create Policy
                  ↓
         Enter Customer Details
                  ↓
         Select Plan & Terms
                  ↓
         Policy Created
                  ↓
         Process Payments
                  ↓
         View Commission
```

---

## 🔍 Policy Creation Guide (For Agents)

### Step 1: Navigate to Policies
- Click **"My Policies"** in navigation
- Click **"Create New Policy"** button

### Step 2: Select Plan
- Choose from available insurance plans
- Each plan has different terms and conditions

### Step 3: Policy Details
Enter:
- **Policy Term** (years)
- **Sum Assured** (insurance amount)
- **Payment Mode** (Yearly/Half-yearly/Quarterly/Monthly)

### Step 4: Customer Information
Enter customer details:
- Full Name
- Date of Birth (for age validation)
- Gender
- Occupation
- Education

### Step 5: Address Details
- Street Address
- City
- State
- Pincode (6 digits)

### Step 6: Nominee Information
- Nominee Name
- Relationship with customer

### Step 7: Submit
- System validates all details
- Checks age, term, and sum assured limits
- Creates policy if valid
- Shows policy number

---

## 💳 Payment Processing Guide (For Agents)

### View Due Payments
1. Click **"Payments"** in navigation
2. See all policies with pending payments
3. Check due dates and amounts

### Process a Payment
1. Click **"Pay Now"** for a policy
2. Verify policy details
3. Enter payment amount (minimum = premium amount)
4. Select payment method:
   - Cash
   - Cheque
   - Online Transfer
   - Card
5. Click **"Process Payment"**
6. System records payment and updates due date

---

## 📈 Viewing Reports

### Commission Report (Agents)
1. Click **"Commission"** in navigation
2. View all your policies
3. See commission for each policy
4. Check total earnings

### Business Report (Admins)
1. Click **"Reports"** in navigation
2. Choose report type:
   - **Yearly** - Annual performance
   - **Monthly** - Month-wise breakdown
3. View statistics:
   - Total policies
   - Total commission
4. See visual charts

---

## ⚠️ Common Issues & Solutions

### "Invalid Credentials" Error

**Problem:** Login fails even with correct credentials

**Solutions:**
1. Verify you're using the correct User ID:
   - Admin: 5 digits
   - Agent: 7 digits
2. Check for typing errors
3. Ensure password is correct (case-sensitive)
4. If new user, verify you saved the correct ID from registration

### "Policy Creation Failed" Error

**Problem:** Unable to create policy

**Common Reasons:**
1. **Age not in range** - Customer age outside plan limits
2. **Term invalid** - Term doesn't match plan's allowed terms
3. **Sum Assured out of range** - Amount below minimum or above maximum
4. **Maturity age exceeded** - Age + Term > Plan's maximum maturity age

**Solution:** Double-check plan requirements and adjust inputs

### Forgot User ID

**Problem:** Can't remember Admin ID or Agency Code

**Solutions:**
1. Check your registration confirmation email (if saved)
2. Check registration success page (if you bookmarked it)
3. Contact system administrator to look up by email
4. In development: Check database directly

---

## 🔒 Security Best Practices

### For All Users

1. **Strong Passwords**
   - Use at least 8 characters
   - Mix letters, numbers, symbols
   - Avoid common words
   - Don't share with others

2. **Keep ID Secure**
   - Don't share your User ID publicly
   - Store it in a password manager
   - Don't write it on sticky notes

3. **Logout After Use**
   - Always click "Logout" when done
   - Especially on shared computers
   - Clear browser cache on public PCs

4. **Regular Updates**
   - Change password periodically
   - Update contact information
   - Keep email current

---

## 📞 Getting Help

### In-App Help
- Hover over field labels for tooltips
- Error messages explain what went wrong
- Flash messages guide you through actions

### Technical Support
- Check documentation files
- Review error logs
- Contact system administrator

### Feature Requests
- Suggest improvements
- Report bugs
- Request new features

---

## 🎓 Training Tips

### For New Admins
1. Start by exploring the Plans section
2. Create a test plan
3. View sample reports
4. Practice editing plans

### For New Agents
1. Review available plans first
2. Create a test policy with dummy data
3. Practice payment processing
4. Check your commission report

### General Tips
- ✅ Use the test accounts first
- ✅ Familiarize yourself with the interface
- ✅ Practice on sample data before real entries
- ✅ Keep documentation handy

---

## 📋 Quick Reference Card

### Admin Quick Reference
| Action | Navigation |
|--------|------------|
| View Plans | Dashboard → Plans |
| Create Plan | Plans → Add New Plan |
| Edit Plan | Plans → Edit (on plan row) |
| Business Report | Dashboard → Reports |

### Agent Quick Reference
| Action | Navigation |
|--------|------------|
| Create Policy | Dashboard → My Policies → Create New |
| View Policies | Dashboard → My Policies |
| Process Payment | Dashboard → Payments → Pay Now |
| View Commission | Dashboard → Commission |

---

## 🎉 Success Indicators

You're using the system correctly when:
- ✅ Login is successful on first try
- ✅ Dashboard loads with your data
- ✅ Actions complete without errors
- ✅ Flash messages are green (success)
- ✅ Reports show expected data

---

## 🚀 Getting Started Checklist

### For New Admins
- [ ] Register and save Admin ID
- [ ] Login successfully
- [ ] Explore dashboard
- [ ] Create first plan
- [ ] View business report
- [ ] Understand plan management

### For New Agents
- [ ] Register and save Agency Code
- [ ] Login successfully
- [ ] Review available plans
- [ ] Create test policy
- [ ] Process sample payment
- [ ] View commission report

---

**Need more help?** Check the technical documentation or contact your system administrator.

**Happy Insurance Managing! 🎯**