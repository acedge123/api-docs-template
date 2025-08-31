FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r base.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Start the application with migrations and static collection
CMD ["sh", "-c", "python manage.py migrate --run-syncdb && python manage.py collectstatic --noinput && python manage.py check && gunicorn hfcscoringengine.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 1"]
