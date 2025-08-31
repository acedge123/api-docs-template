#!/bin/bash

# Startup script for Django application on Railway

echo "=== Starting Django Application ==="
echo "Environment: $DJANGO_SETTINGS_MODULE"
echo "Port: $PORT"
echo "Debug: $DJANGO_DEBUG"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application immediately
echo "Starting Gunicorn..."
exec gunicorn hfcscoringengine.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug
