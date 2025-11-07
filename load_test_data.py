#!/usr/bin/env python
"""
Load test data into the database for development/testing.

This script:
1. Loads the fixture data from test_data_fixtures.json
2. Sets all user passwords to 'Test123!'
3. Updates manager references for locations

Usage:
    python load_test_data.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careplan.settings')
django.setup()

from django.core.management import call_command
from apps.accounts.models import User
from apps.locations.models import Location


def main():
    print("=" * 70)
    print("LOADING TEST DATA")
    print("=" * 70)

    # Step 1: Load fixtures
    print("\n[1/4] Loading fixture data from test_data_fixtures.json...")
    try:
        call_command('loaddata', 'test_data_fixtures.json', verbosity=2)
        print("✓ Fixtures loaded successfully")
    except Exception as e:
        print(f"✗ Error loading fixtures: {e}")
        return

    # Step 2: Set passwords for all users
    print("\n[2/4] Setting passwords for all test users...")
    test_password = 'Test123!'
    users = User.objects.all()

    for user in users:
        user.set_password(test_password)
        user.save(update_fields=['password'])
        print(f"  ✓ Set password for {user.username} ({user.email})")

    print(f"\n✓ All {users.count()} users now have password: {test_password}")

    # Step 3: Update location managers
    print("\n[3/4] Assigning managers to locations...")

    # Set Michael Schmidt as manager for Central location
    central = Location.objects.get(pk=1)
    central.manager = User.objects.get(pk=2)
    central.save()
    print(f"  ✓ {central.name} -> Manager: {central.manager.get_full_name()}")

    # Set Julia Becker as manager for North location
    north = Location.objects.get(pk=2)
    north.manager = User.objects.get(pk=7)
    north.save()
    print(f"  ✓ {north.name} -> Manager: {north.manager.get_full_name()}")

    # Step 4: Assign qualifications to employees
    print("\n[4/4] Assigning qualifications to employees...")

    from apps.employees.models import Qualification

    # Get qualifications
    rn = Qualification.objects.get(code='RN')
    cna = Qualification.objects.get(code='CNA')
    bls = Qualification.objects.get(code='BLS')
    acls = Qualification.objects.get(code='ACLS')

    # Assign to nurses
    nurses = User.objects.filter(job_title='Registered Nurse')
    for nurse in nurses:
        nurse.qualifications.add(rn, bls, acls)
        print(f"  ✓ {nurse.get_full_name()} -> RN, BLS, ACLS")

    # Assign to care workers
    care_workers = User.objects.filter(job_title='Care Worker')
    for worker in care_workers:
        worker.qualifications.add(cna, bls)
        print(f"  ✓ {worker.get_full_name()} -> CNA, BLS")

    # Print summary
    print("\n" + "=" * 70)
    print("TEST DATA LOADED SUCCESSFULLY")
    print("=" * 70)
    print("\n📊 Summary:")
    print(f"  • Locations:        {Location.objects.count()}")
    print(f"  • Employees:        {User.objects.count()}")
    print(f"  • Qualifications:   {Qualification.objects.count()}")

    from apps.vacation.models import VacationRequest, PublicHoliday
    print(f"  • Vacation Requests: {VacationRequest.objects.count()}")
    print(f"  • Public Holidays:  {PublicHoliday.objects.count()}")

    print("\n👥 Test User Credentials:")
    print("-" * 70)
    print(f"{'Username':<15} {'Email':<35} {'Role':<10}")
    print("-" * 70)

    for user in User.objects.order_by('role', 'employee_id'):
        print(f"{user.username:<15} {user.email:<35} {user.role:<10}")

    print("-" * 70)
    print(f"\n🔑 Password for ALL users: {test_password}")
    print("\n✅ You can now login with any of the above credentials!")
    print("=" * 70)


if __name__ == '__main__':
    main()
