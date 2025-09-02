FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements/ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r base.txt

# Copy the rest of the application
COPY backend/ .

# Expose port
EXPOSE 8000

# Create logs directory
RUN mkdir -p logs

# Make startup script executable
RUN chmod +x start.sh

# Start the application
CMD ["./start.sh"]
