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
python manage.py migrate --verbosity=2

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --verbosity=0

# Create admin user if it doesn't exist
echo "Creating admin user..."
python manage.py create_admin

# Start the application
echo "Starting Gunicorn..."
exec gunicorn hfcscoringengine.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level warning
