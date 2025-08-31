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

# Start the application with immediate logging
CMD ["sh", "-c", "echo '=== RAILWAY DEPLOYMENT STARTING ===' && echo 'Current directory:' && pwd && echo 'Files in current directory:' && ls -la && echo '=== RUNNING STARTUP SCRIPT ===' && ./start.sh"]
