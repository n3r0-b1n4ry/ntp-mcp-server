# Use Python 3.11 alpine image as base
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Set default environment variables
ENV NTP_SERVER=pool.ntp.org
ENV TZ=UTC

# Run the application
CMD ["python", "app.py"] 