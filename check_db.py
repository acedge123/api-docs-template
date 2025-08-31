#!/usr/bin/env python
"""Check database status and migrations."""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfcscoringengine.settings.railway")
django.setup()

from django.core.management import call_command
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()

def check_database():
    """Check database status."""
    print("=== Database Status Check ===")
    
    # Check if we can connect to the database
    try:
        with connection.cursor() as cursor:
            # Check database type
            db_engine = connection.settings_dict['ENGINE']
            print(f"Database engine: {db_engine}")
            
            if 'sqlite' in db_engine:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            elif 'postgresql' in db_engine:
                cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
            else:
                cursor.execute("SHOW TABLES;")
                
            tables = cursor.fetchall()
            print(f"✓ Database connection successful")
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            # Check for auth_user table specifically
            if any('auth_user' in table[0] for table in tables):
                print("✓ auth_user table exists")
            else:
                print("✗ auth_user table does not exist")
                
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    # Check migration status
    print("\n=== Migration Status ===")
    try:
        call_command('showmigrations', '--verbosity=0')
        print("✓ Migration check completed")
    except Exception as e:
        print(f"✗ Migration check failed: {e}")
    
    # Try to run migrations
    print("\n=== Running Migrations ===")
    try:
        call_command('migrate', '--verbosity=2')
        print("✓ Migrations completed successfully")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
    
    # Check if admin user exists
    print("\n=== Admin User Check ===")
    try:
        user_count = User.objects.count()
        print(f"Total users in database: {user_count}")
        
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            print("✓ Admin user exists")
            print(f"  Username: {admin_user.username}")
            print(f"  Email: {admin_user.email}")
            print(f"  Is staff: {admin_user.is_staff}")
            print(f"  Is superuser: {admin_user.is_superuser}")
        else:
            print("✗ Admin user does not exist")
            
    except Exception as e:
        print(f"✗ User check failed: {e}")

if __name__ == "__main__":
    check_database()
