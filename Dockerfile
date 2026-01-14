FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Disable Python output buffering for Railway logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies in smaller batches to avoid resource exhaustion
# First batch: essential build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Second batch: image processing libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Third batch: ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directories
RUN mkdir -p output/videos output/thumbnails output/reels output/schedules

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run uvicorn directly - PORT defaults to 8000 if not set
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
