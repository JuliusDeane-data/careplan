# Test Data for CarePlan

This directory contains comprehensive test data for the CarePlan application that you can load into your development/test database.

## 📦 What's Included

The test data includes:

- **4 Locations** - Care facilities in Berlin, Hamburg, Munich, and Dresden
- **12 Employees** - Mix of admins, managers, nurses, and care workers
- **4 Qualifications** - RN, CNA, BLS, ACLS certifications
- **7 Public Holidays** - German national holidays for 2025
- **10 Vacation Requests** - Various states (pending, approved, denied)

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)

The easiest way to load test data:

```bash
# Make sure you're in the project root
cd /home/user/careplan

# Run the load script
python load_test_data.py
```

This script will:
1. Load all fixture data
2. Set all user passwords to `Test123!`
3. Assign managers to locations
4. Assign qualifications to employees
5. Display a summary of loaded data

### Option 2: Manual Fixture Loading

If you prefer to load just the fixtures without the helper script:

```bash
python manage.py loaddata test_data_fixtures.json
```

**Note:** You'll need to manually set user passwords afterward:

```python
python manage.py shell

from apps.accounts.models import User
for user in User.objects.all():
    user.set_password('Test123!')
    user.save()
```

## 🧹 Clearing Existing Data (Optional)

If you want to start fresh, you can reset your database:

```bash
# WARNING: This will delete ALL data in your database!

# Option A: Delete and recreate the database (SQLite)
rm db.sqlite3
python manage.py migrate

# Option B: Flush the database (keeps schema)
python manage.py flush --no-input

# Then load test data
python load_test_data.py
```

## 👥 Test User Accounts

All users have the password: **`Test123!`**

### Admin Account
- **Username:** `admin001`
- **Email:** `sarah.anderson@sunshinecare.de`
- **Role:** ADMIN
- **Location:** Sunshine Care Home - Central (Berlin)

### Manager Accounts
- **Username:** `mgr001` | **Email:** `michael.schmidt@sunshinecare.de` | **Location:** Central
- **Username:** `mgr002` | **Email:** `julia.becker@sunshinecare.de` | **Location:** North

### Nurse Accounts
- **Username:** `nurse001` | **Email:** `emma.mueller@sunshinecare.de` | **Location:** Central
- **Username:** `nurse002` | **Email:** `lisa.weber@sunshinecare.de` | **Location:** Central
- **Username:** `nurse003` | **Email:** `marcus.schneider@sunshinecare.de` | **Location:** North
- **Username:** `nurse004` | **Email:** `maria.richter@sunshinecare.de` | **Location:** South (ON_LEAVE)

### Care Worker Accounts
- **Username:** `care001` | **Email:** `thomas.fischer@sunshinecare.de` | **Location:** Central
- **Username:** `care002` | **Email:** `anna.hoffmann@sunshinecare.de` | **Location:** Central (Part-time)
- **Username:** `care003` | **Email:** `sophie.klein@sunshinecare.de` | **Location:** North
- **Username:** `care004` | **Email:** `lukas.wagner@sunshinecare.de` | **Location:** South
- **Username:** `care005` | **Email:** `daniel.koch@sunshinecare.de` | **Location:** East (Part-time)

## 🏥 Locations

1. **Sunshine Care Home - Central** (Berlin)
   - Capacity: 80 | Manager: Michael Schmidt
   - Employees: 6 staff members

2. **Sunshine Care Home - North** (Hamburg)
   - Capacity: 60 | Manager: Julia Becker
   - Employees: 3 staff members

3. **Sunshine Care Home - South** (Munich)
   - Capacity: 50 | Manager: Not assigned
   - Employees: 2 staff members

4. **Sunshine Care Home - East** (Dresden)
   - Capacity: 40 | Manager: Not assigned
   - Employees: 1 staff member

## 📅 Vacation Requests

The test data includes various vacation requests to test different scenarios:

1. **Emma Mueller** (nurse001) - Feb 10-14, 2025 - ✅ APPROVED
2. **Lisa Weber** (nurse002) - Mar 17-21, 2025 - ⏳ PENDING
3. **Thomas Fischer** (care001) - Apr 7-11, 2025 - ✅ APPROVED
4. **Anna Hoffmann** (care002) - Jun 23-Jul 4, 2025 - ⏳ PENDING
5. **Marcus Schneider** (nurse003) - May 5-9, 2025 - ✅ APPROVED
6. **Sophie Klein** (care003) - Feb 3-7, 2025 - ❌ DENIED
7. **Lukas Wagner** (care004) - Aug 11-22, 2025 - ⏳ PENDING
8. **Maria Richter** (nurse004) - Dec 20-Jan 10 - ✅ APPROVED (Parental)
9. **Daniel Koch** (care005) - Sep 15-19, 2025 - ⏳ PENDING
10. **Emma Mueller** (nurse001) - Dec 23-27, 2024 - ✅ APPROVED (Past)

## 🎓 Qualifications

- **RN** (Registered Nurse) - Assigned to all nurses
- **CNA** (Certified Nursing Assistant) - Assigned to all care workers
- **BLS** (Basic Life Support) - Assigned to nurses and care workers
- **ACLS** (Advanced Cardiovascular Life Support) - Assigned to nurses only

## 📆 Public Holidays (2025)

- New Year's Day - Jan 1
- Good Friday - Apr 18
- Easter Monday - Apr 21
- Labour Day - May 1
- Day of German Unity - Oct 3
- Christmas Day - Dec 25
- Boxing Day - Dec 26

## 🧪 Testing Scenarios

The test data enables you to test:

### Employee Directory
- ✅ Search and filter employees
- ✅ View employee profiles
- ✅ Different employment types (full-time, part-time)
- ✅ Different employment statuses (active, on leave)
- ✅ Multiple locations
- ✅ Qualifications and certifications

### Vacation Management
- ✅ Pending requests (manager can approve/deny)
- ✅ Approved requests
- ✅ Denied requests with reasons
- ✅ Different leave types (annual, parental)
- ✅ Past, current, and future vacations
- ✅ Vacation balance calculations

### Dashboard
- ✅ Personal vacation statistics
- ✅ Team management (for managers)
- ✅ System-wide stats (for admin)
- ✅ Activity feed
- ✅ Upcoming events

### Access Control
- ✅ Admin can access everything
- ✅ Managers can view team data
- ✅ Employees can only see their own data

## 🔧 Customization

You can modify `test_data_fixtures.json` to:

- Add more employees
- Change vacation dates
- Add more locations
- Modify employee details
- Add additional vacation requests

After making changes, reload with:

```bash
python manage.py flush --no-input
python load_test_data.py
```

## 📝 Notes

- **Passwords are hashed:** All passwords in the fixture are dummy hashes. The `load_test_data.py` script properly sets them to `Test123!`
- **Dates are realistic:** Vacation requests span 2024-2025 to show past, current, and future requests
- **Vacation days are calculated:** Remaining vacation days reflect approved requests
- **Many-to-many relationships:** Employee qualifications are set via the loading script
- **Foreign keys:** All relationships (managers, approvers, locations) are properly linked

## ⚠️ Important

**This is TEST DATA ONLY!**

- Do NOT use in production
- Do NOT use these passwords in production
- Employee names and data are fictional
- Email addresses use a fictional domain

## 🆘 Troubleshooting

### Error: "Duplicate key value"
Solution: Clear the database first with `python manage.py flush --no-input`

### Error: "No such table"
Solution: Run migrations first with `python manage.py migrate`

### Error: "Foreign key constraint failed"
Solution: Make sure you're loading the complete fixture file and the database is empty

### Passwords don't work
Solution: Use the `load_test_data.py` script instead of loading fixtures directly

## 📚 Additional Resources

- [Django Fixtures Documentation](https://docs.djangoproject.com/en/stable/howto/initial-data/)
- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)

---

**Happy Testing! 🎉**
