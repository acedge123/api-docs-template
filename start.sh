#!/bin/bash

echo "=== Starting Django Application ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Django settings: $DJANGO_SETTINGS_MODULE"

# Check Django configuration
echo "=== Checking Django configuration ==="
python manage.py check
if [ $? -ne 0 ]; then
    echo "ERROR: Django configuration check failed"
    exit 1
fi

# Run migrations
echo "=== Running migrations ==="
python manage.py migrate --run-syncdb
if [ $? -ne 0 ]; then
    echo "ERROR: Database migrations failed"
    exit 1
fi

# Collect static files
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "ERROR: Static file collection failed"
    exit 1
fi

# Start gunicorn
echo "=== Starting Gunicorn ==="
echo "Port: $PORT"
echo "Workers: 1"
echo "Timeout: 120"

exec gunicorn hfcscoringengine.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -
