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

# Make startup script executable
RUN chmod +x start.sh

# Start with a simple test first
CMD ["sh", "-c", "echo 'Container starting...' && sleep 5 && echo 'Testing basic commands...' && python --version && echo 'Testing Django...' && python manage.py check --deploy && echo 'Starting gunicorn...' && gunicorn hfcscoringengine.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120"]
