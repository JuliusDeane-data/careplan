# 🔑 Quick Reference - Test Credentials

**All users have password:** `Test123!`

## 🎯 Quick Login Credentials

### For System Admin Testing
```
Username: admin001
Email:    sarah.anderson@sunshinecare.de
Password: Test123!
Role:     ADMIN
```

### For Manager Testing (Central Location)
```
Username: mgr001
Email:    michael.schmidt@sunshinecare.de
Password: Test123!
Role:     MANAGER
Location: Sunshine Care Home - Central (Berlin)
```

### For Manager Testing (North Location)
```
Username: mgr002
Email:    julia.becker@sunshinecare.de
Password: Test123!
Role:     MANAGER
Location: Sunshine Care Home - North (Hamburg)
```

### For Nurse Testing
```
Username: nurse001
Email:    emma.mueller@sunshinecare.de
Password: Test123!
Role:     EMPLOYEE (Registered Nurse)
Location: Central
Note:     Has approved and pending vacation requests
```

### For Care Worker Testing
```
Username: care001
Email:    thomas.fischer@sunshinecare.de
Password: Test123!
Role:     EMPLOYEE (Care Worker)
Location: Central
```

### For Part-Time Employee Testing
```
Username: care002
Email:    anna.hoffmann@sunshinecare.de
Password: Test123!
Role:     EMPLOYEE (Care Worker, Part-time)
Location: Central
Hours:    30/week
```

### For On-Leave Employee Testing
```
Username: nurse004
Email:    maria.richter@sunshinecare.de
Password: Test123!
Role:     EMPLOYEE (Registered Nurse)
Status:   ON_LEAVE (Parental Leave)
Location: South
```

## 📋 Complete User List

| Username   | Email                              | Role     | Location | Status     |
|------------|------------------------------------|----------|----------|------------|
| admin001   | sarah.anderson@sunshinecare.de    | ADMIN    | Central  | ACTIVE     |
| mgr001     | michael.schmidt@sunshinecare.de   | MANAGER  | Central  | ACTIVE     |
| mgr002     | julia.becker@sunshinecare.de      | MANAGER  | North    | ACTIVE     |
| nurse001   | emma.mueller@sunshinecare.de      | EMPLOYEE | Central  | ACTIVE     |
| nurse002   | lisa.weber@sunshinecare.de        | EMPLOYEE | Central  | ACTIVE     |
| nurse003   | marcus.schneider@sunshinecare.de  | EMPLOYEE | North    | ACTIVE     |
| nurse004   | maria.richter@sunshinecare.de     | EMPLOYEE | South    | ON_LEAVE   |
| care001    | thomas.fischer@sunshinecare.de    | EMPLOYEE | Central  | ACTIVE     |
| care002    | anna.hoffmann@sunshinecare.de     | EMPLOYEE | Central  | ACTIVE     |
| care003    | sophie.klein@sunshinecare.de      | EMPLOYEE | North    | ACTIVE     |
| care004    | lukas.wagner@sunshinecare.de      | EMPLOYEE | South    | ACTIVE     |
| care005    | daniel.koch@sunshinecare.de       | EMPLOYEE | East     | ACTIVE     |

## 🧪 Testing Scenarios

### Test Admin Features
- Login as `admin001`
- View all employees across all locations
- View system-wide statistics
- Access all areas of the application

### Test Manager Features
- Login as `mgr001` (Central) or `mgr002` (North)
- View team members
- Approve/deny vacation requests
- View team statistics

### Test Employee Features
- Login as any nurse or care worker
- Request vacation
- View own vacation balance
- View personal statistics

### Test Vacation Approval Workflow
1. Login as `nurse002` (has pending request)
2. View pending request for Mar 17-21, 2025
3. Logout
4. Login as `mgr001` (manager)
5. Approve or deny the request
6. Logout
7. Login as `nurse002` again
8. View updated request status

### Test Denied Request
- Login as `care003` (Sophie Klein)
- View denied vacation request (Feb 3-7)
- See denial reason
- Submit new request for different dates

## 💡 Tips

- **Reset password:** All users can reset to `Test123!` via the load_test_data.py script
- **Email login:** You can login with email OR username
- **Role-based access:** Different users see different dashboard widgets based on role
- **Multiple locations:** Test multi-location features with employees across 4 facilities

## 🔄 Reload Test Data

If you need to reset everything:

```bash
# Clear database
python manage.py flush --no-input

# Reload test data
python load_test_data.py
```

---

**Remember:** These are TEST credentials only! Never use in production! 🔒
