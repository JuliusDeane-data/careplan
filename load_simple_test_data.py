#!/usr/bin/env python
"""
Load simplified test data into the database.
This script creates essential data for testing.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User
from apps.locations.models import Location
from apps.employees.models import Qualification
from apps.vacation.models import PublicHoliday, VacationRequest
from datetime import date, datetime
from django.utils import timezone

def main():
    print("=" * 70)
    print("LOADING SIMPLIFIED TEST DATA")
    print("=" * 70)

    # Create locations
    print('\n[1/5] Creating locations...')
    Location.objects.all().delete()
    locations = {
        'central': Location.objects.create(
            name='Sunshine Care Home - Central',
            address='123 Main Street',
            city='Berlin',
            postal_code='10115',
            country='Germany',
            phone='+49 30 12345678',
            email='central@sunshinecare.de',
            max_capacity=80,
            is_active=True
        ),
        'north': Location.objects.create(
            name='Sunshine Care Home - North',
            address='456 Oak Avenue',
            city='Hamburg',
            postal_code='20095',
            country='Germany',
            phone='+49 40 98765432',
            email='north@sunshinecare.de',
            max_capacity=60,
            is_active=True
        ),
        'south': Location.objects.create(
            name='Sunshine Care Home - South',
            address='789 Pine Road',
            city='Munich',
            postal_code='80331',
            country='Germany',
            phone='+49 89 55544433',
            email='south@sunshinecare.de',
            max_capacity=50,
            is_active=True
        ),
        'east': Location.objects.create(
            name='Sunshine Care Home - East',
            address='321 Elm Lane',
            city='Dresden',
            postal_code='01067',
            country='Germany',
            phone='+49 351 22233344',
            email='east@sunshinecare.de',
            max_capacity=40,
            is_active=True
        )
    }
    print(f'  ✓ Created {len(locations)} locations')

    # Create qualifications
    print('\n[2/5] Creating qualifications...')
    Qualification.objects.all().delete()
    quals = {
        'rn': Qualification.objects.create(
            code='RN',
            name='Registered Nurse',
            description='Licensed registered nurse',
            is_active=True
        ),
        'cna': Qualification.objects.create(
            code='CNA',
            name='Certified Nursing Assistant',
            description='Certified nursing assistant',
            is_active=True
        ),
        'bls': Qualification.objects.create(
            code='BLS',
            name='Basic Life Support',
            description='BLS certification',
            is_active=True
        ),
        'acls': Qualification.objects.create(
            code='ACLS',
            name='Advanced Cardiovascular Life Support',
            description='ACLS certification',
            is_active=True
        )
    }
    print(f'  ✓ Created {len(quals)} qualifications')

    # Create users
    print('\n[3/5] Creating users...')
    User.objects.all().delete()

    # Admin
    admin = User.objects.create_user(
        username='admin001',
        email='sarah.anderson@sunshinecare.de',
        password='Test123!',
        first_name='Sarah',
        last_name='Anderson',
        employee_id='EMP001',
        role='ADMIN',
        job_title='Administrator',
        hire_date=date(2020, 1, 15),
        primary_location=locations['central'],
        is_staff=True,
        is_superuser=True
    )
    print(f'  ✓ Created admin: {admin.username} ({admin.email})')

    # Manager 1
    manager1 = User.objects.create_user(
        username='mgr001',
        email='michael.schmidt@sunshinecare.de',
        password='Test123!',
        first_name='Michael',
        last_name='Schmidt',
        employee_id='MGR001',
        role='MANAGER',
        job_title='Care Manager',
        hire_date=date(2021, 3, 1),
        primary_location=locations['central'],
        is_staff=True
    )
    print(f'  ✓ Created manager: {manager1.username} ({manager1.email})')

    # Manager 2
    manager2 = User.objects.create_user(
        username='mgr002',
        email='julia.becker@sunshinecare.de',
        password='Test123!',
        first_name='Julia',
        last_name='Becker',
        employee_id='MGR002',
        role='MANAGER',
        job_title='Care Manager',
        hire_date=date(2021, 5, 15),
        primary_location=locations['north'],
        is_staff=True
    )
    print(f'  ✓ Created manager: {manager2.username} ({manager2.email})')

    # Nurses
    nurse1 = User.objects.create_user(
        username='nurse001',
        email='emma.mueller@sunshinecare.de',
        password='Test123!',
        first_name='Emma',
        last_name='Mueller',
        employee_id='NUR001',
        role='EMPLOYEE',
        job_title='Registered Nurse',
        hire_date=date(2022, 1, 10),
        primary_location=locations['central'],
        supervisor=manager1
    )
    nurse1.qualifications.add(quals['rn'], quals['bls'], quals['acls'])
    print(f'  ✓ Created nurse: {nurse1.username} ({nurse1.email})')

    nurse2 = User.objects.create_user(
        username='nurse002',
        email='lisa.weber@sunshinecare.de',
        password='Test123!',
        first_name='Lisa',
        last_name='Weber',
        employee_id='NUR002',
        role='EMPLOYEE',
        job_title='Registered Nurse',
        hire_date=date(2022, 3, 1),
        primary_location=locations['central'],
        supervisor=manager1
    )
    nurse2.qualifications.add(quals['rn'], quals['bls'])
    print(f'  ✓ Created nurse: {nurse2.username} ({nurse2.email})')

    # Care workers
    care1 = User.objects.create_user(
        username='care001',
        email='thomas.fischer@sunshinecare.de',
        password='Test123!',
        first_name='Thomas',
        last_name='Fischer',
        employee_id='CAR001',
        role='EMPLOYEE',
        job_title='Care Worker',
        hire_date=date(2022, 6, 1),
        primary_location=locations['central'],
        supervisor=manager1
    )
    care1.qualifications.add(quals['cna'], quals['bls'])
    print(f'  ✓ Created care worker: {care1.username} ({care1.email})')

    care2 = User.objects.create_user(
        username='care002',
        email='anna.hoffmann@sunshinecare.de',
        password='Test123!',
        first_name='Anna',
        last_name='Hoffmann',
        employee_id='CAR002',
        role='EMPLOYEE',
        job_title='Care Worker',
        hire_date=date(2023, 1, 15),
        primary_location=locations['north'],
        employment_type='PART_TIME',
        contract_hours_per_week=20,
        supervisor=manager2
    )
    care2.qualifications.add(quals['cna'])
    print(f'  ✓ Created care worker: {care2.username} ({care2.email})')

    # Update location managers
    print('\n[4/5] Assigning location managers...')
    locations['central'].manager = manager1
    locations['central'].save()
    locations['north'].manager = manager2
    locations['north'].save()
    print('  ✓ Location managers assigned')

    # Create public holidays
    print('\n[5/5] Creating public holidays...')
    PublicHoliday.objects.all().delete()
    holidays = [
        PublicHoliday.objects.create(
            name="New Year's Day",
            date=date(2025, 1, 1),
            is_nationwide=True,
            is_recurring=True,
            recurring_month=1,
            recurring_day=1
        ),
        PublicHoliday.objects.create(
            name="Good Friday",
            date=date(2025, 4, 18),
            is_nationwide=True
        ),
        PublicHoliday.objects.create(
            name="Easter Monday",
            date=date(2025, 4, 21),
            is_nationwide=True
        ),
        PublicHoliday.objects.create(
            name="Labour Day",
            date=date(2025, 5, 1),
            is_nationwide=True,
            is_recurring=True,
            recurring_month=5,
            recurring_day=1
        ),
        PublicHoliday.objects.create(
            name="Day of German Unity",
            date=date(2025, 10, 3),
            is_nationwide=True,
            is_recurring=True,
            recurring_month=10,
            recurring_day=3
        ),
        PublicHoliday.objects.create(
            name="Christmas Day",
            date=date(2025, 12, 25),
            is_nationwide=True,
            is_recurring=True,
            recurring_month=12,
            recurring_day=25
        ),
        PublicHoliday.objects.create(
            name="Boxing Day",
            date=date(2025, 12, 26),
            is_nationwide=True,
            is_recurring=True,
            recurring_month=12,
            recurring_day=26
        ),
    ]
    print(f'  ✓ Created {len(holidays)} public holidays')

    # Summary
    print("\n" + "=" * 70)
    print("TEST DATA LOADED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nLocations: {Location.objects.count()}")
    print(f"Qualifications: {Qualification.objects.count()}")
    print(f"Users: {User.objects.count()}")
    print(f"  - Admins: {User.objects.filter(role='ADMIN').count()}")
    print(f"  - Managers: {User.objects.filter(role='MANAGER').count()}")
    print(f"  - Employees: {User.objects.filter(role='EMPLOYEE').count()}")
    print(f"Public Holidays: {PublicHoliday.objects.count()}")

    print("\n" + "=" * 70)
    print("TEST ACCOUNTS (Password: Test123!)")
    print("=" * 70)
    print("\nAdmin:")
    print(f"  Username: admin001")
    print(f"  Email: sarah.anderson@sunshinecare.de")
    print("\nManagers:")
    print(f"  Username: mgr001 | Email: michael.schmidt@sunshinecare.de")
    print(f"  Username: mgr002 | Email: julia.becker@sunshinecare.de")
    print("\nEmployees:")
    print(f"  Username: nurse001 | Email: emma.mueller@sunshinecare.de")
    print(f"  Username: nurse002 | Email: lisa.weber@sunshinecare.de")
    print(f"  Username: care001 | Email: thomas.fischer@sunshinecare.de")
    print(f"  Username: care002 | Email: anna.hoffmann@sunshinecare.de")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
