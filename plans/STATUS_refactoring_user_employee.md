# User-Employee Refactoring Status

**Date**: 2025-11-04
**Status**: In Progress - Migration Issues ⚠️

---

## Summary

Refactoring the architecture to merge Employee model into User model (User IS Employee, not separate entities).

---

## Completed ✅

1. **Updated User Model** (apps/accounts/models.py)
   - Added all employee fields directly to User model
   - Changed role choices from EMPLOYEE/SUPERVISOR/PLANNER/ADMIN to EMPLOYEE/MANAGER/ADMIN
   - Made employee fields optional (null=True, blank=True)
   - Added employee methods: `get_age()`, `get_years_of_service()`, `can_work_at_location()`, `update_vacation_balance()`

2. **Updated Employees App Models** (apps/employees/models.py)
   - Removed Employee model entirely
   - Kept Qualification model
   - Updated EmployeeDocument to reference User instead of Employee
   - Deleted managers.py (no longer needed)

3. **Updated Admin Interfaces**
   - Created UserAdmin in apps/accounts/admin.py with all employee fieldsets
   - Updated EmployeeAdmin (removed)
   - Updated EmployeeDocumentAdmin to search by employee__first_name instead of employee__user__first_name
   - Temporarily removed `manager` field from LocationAdmin

4. **Deleted Old Database Tables**
   - Dropped `employees` table
   - Dropped `employee_documents` table
   - Dropped `qualifications` table
   - Dropped M2M junction tables
   - Faked migration reversals for accounts and employees apps

---

## Current Issue ⚠️

**Circular Dependency Between accounts and locations**:

```
accounts.0001_initial depends on locations.0001_initial (User.primary_location → Location)
locations.0001_initial depends on accounts (Location.created_by → User via BaseModel)
```

This creates a circular dependency that Django cannot resolve.

---

## Solution Strategy

**Three-Step Migration Approach**:

1. **Step 1**: Create User model WITHOUT location-related fields
   - Create accounts.0001_initial (User without primary_location/additional_locations)
   - Create locations.0001_initial (Location without manager field)
   - Apply these migrations

2. **Step 2**: Add location fields to User
   - Create accounts.0002_add_location_fields
   - Add primary_location ForeignKey
   - Add additional_locations ManyToManyField
   - Apply migration

3. **Step 3**: Add manager field back to Location
   - Create locations.0002_add_manager_field
   - Add manager ForeignKey
   - Apply migration

---

## Files Modified

- `/home/philip/projects/careplan/apps/accounts/models.py` - User model with all employee fields
- `/home/philip/projects/careplan/apps/employees/models.py` - Removed Employee, kept Qualification & EmployeeDocument
- `/home/philip/projects/careplan/apps/accounts/admin.py` - Complete UserAdmin created
- `/home/philip/projects/careplan/apps/employees/admin.py` - Removed EmployeeAdmin
- `/home/philip/projects/careplan/apps/locations/models.py` - Temporarily removed manager field (commented out)
- `/home/philip/projects/careplan/apps/locations/admin.py` - Removed manager from list_display and fieldsets

---

## Next Steps

1. Temporarily comment out location-related fields in User model
2. Create initial migrations for both apps
3. Apply initial migrations
4. Uncomment location fields in User model
5. Create second migration for User (add location fields)
6. Apply second migration
7. Add back manager field to Location model
8. Create third migration for Location (add manager field)
9. Apply third migration
10. Test the refactored models
11. Create superuser
12. Test admin interface

---

## Database State

- Old `employees`, `qualifications`, `employee_documents` tables: DROPPED ✅
- Old `users` table: EXISTS (not modified yet)
- Old `locations` table: EXISTS (not modified yet)
- Migration history for `employees` app: FAKED TO ZERO ✅
- Migration history for `accounts` app: FAKED TO ZERO ✅
- Migration history for `locations` app: FAKED TO ZERO ✅

---

## Key Architecture Changes

### Before:
```
User (authentication only)
  └─ OneToOne → Employee (all employee data)
                  ├─ ForeignKey → Location (primary)
                  ├─ ManyToMany → Location (additional)
                  ├─ ForeignKey → User (supervisor)
                  └─ ManyToMany → Qualification

Location
  └─ ForeignKey → User (manager)
```

### After:
```
User (authentication + employee data combined)
  ├─ ForeignKey → Location (primary)
  ├─ ManyToMany → Location (additional)
  ├─ ForeignKey → User (supervisor - self-referential)
  └─ ManyToMany → Qualification

Location
  └─ ForeignKey → User (manager)

EmployeeDocument
  └─ ForeignKey → User (instead of Employee)
```

---

## Benefits of New Architecture

1. **Simplified**: No need to create User then Employee separately
2. **Direct Access**: User IS the employee, direct field access
3. **Cleaner API**: No employee_profile navigation needed
4. **Easier Queries**: No joins between User and Employee
5. **Better DX**: More intuitive for developers

---

**Next Action**: Implement three-step migration strategy
