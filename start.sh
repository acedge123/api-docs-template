#!/bin/bash

# Startup script for Django application on Railway

echo "=== Starting Django Application ==="
echo "Environment: $DJANGO_SETTINGS_MODULE"
echo "Port: $PORT"
echo "Debug: $DJANGO_DEBUG"

# Create logs directory if it doesn't exist
mkdir -p logs

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --verbosity=1

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --verbosity=0

# Create admin user if it doesn't exist
echo "Creating admin user..."
python manage.py create_admin

# Verify admin user exists
echo "Verifying admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='admin')
    print(f'Admin user exists: {user.username} (staff: {user.is_staff}, superuser: {user.is_superuser})')
except User.DoesNotExist:
    print('Admin user does not exist!')
"

# Start the application
echo "Starting Gunicorn..."
exec gunicorn hfcscoringengine.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level warning
