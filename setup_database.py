#!/usr/bin/env python
"""Script to set up database and admin user."""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfcscoringengine.settings.railway")
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_database():
    """Set up database and admin user."""
    print("=== Database Setup ===")
    
    # Run migrations
    print("Running migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✓ Migrations completed successfully")
    except Exception as e:
        print(f"✗ Migration error: {e}")
        return False
    
    # Create admin user
    print("Creating admin user...")
    username = 'admin'
    email = 'alan@thegig.agency'
    password = '123456@@@'
    
    try:
        # Check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"✓ Updated existing admin user: {username}")
        else:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True
            )
            print(f"✓ Created new admin user: {username}")
        
        # Verify user
        user = User.objects.get(username=username)
        print(f"✓ Admin user verified: {user.username} (staff: {user.is_staff}, superuser: {user.is_superuser})")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n=== Setup Complete ===")
        print("You can now login at /admin/ with:")
        print("Username: admin")
        print("Password: 123456@@@")
    else:
        print("\n=== Setup Failed ===")
        sys.exit(1)
