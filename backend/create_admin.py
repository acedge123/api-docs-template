#!/usr/bin/env python
"""Script to create admin user for Django application."""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfcscoringengine.settings.railway")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin_user():
    """Create admin user with specified credentials."""
    username = 'admin'
    email = 'alan@thegig.agency'
    password = '123456@@@'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print("User '{}' already exists. Updating password...".format(username))
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("Updated user '{}' with new password and email.".format(username))
    else:
        # Create new superuser
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        print("Created superuser '{}' with email '{}'.".format(username, email))
    
    print("Username: {}".format(username))
    print("Email: {}".format(email))
    print("Password: {}".format(password))
    print("You can now login at /admin/")

if __name__ == "__main__":
    create_admin_user()
