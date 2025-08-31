#!/usr/bin/env python
"""Test script to check static files configuration."""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hfcscoringengine.settings.railway")
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.contrib.staticfiles.finders import find

def test_static_files():
    """Test static files configuration."""
    print("=== Static Files Test ===")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    print(f"DEBUG: {settings.DEBUG}")
    
    # Check if staticfiles directory exists
    if os.path.exists(settings.STATIC_ROOT):
        print(f"✓ STATIC_ROOT directory exists: {settings.STATIC_ROOT}")
        files = os.listdir(settings.STATIC_ROOT)
        print(f"Files in STATIC_ROOT: {files}")
    else:
        print(f"✗ STATIC_ROOT directory does not exist: {settings.STATIC_ROOT}")
    
    # Try to find a specific admin CSS file
    admin_css = find('admin/css/base.css')
    if admin_css:
        print(f"✓ Found admin CSS: {admin_css}")
    else:
        print("✗ Could not find admin CSS")
    
    # List all static files finders
    print(f"STATICFILES_FINDERS: {settings.STATICFILES_FINDERS}")
    
    # Try to collect static files
    print("\n=== Collecting Static Files ===")
    try:
        call_command('collectstatic', '--noinput', '--verbosity=2')
        print("✓ Static files collected successfully")
    except Exception as e:
        print(f"✗ Error collecting static files: {e}")

if __name__ == "__main__":
    test_static_files()
