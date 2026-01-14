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
    curl \
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

# Fourth batch: Node.js for React frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend package files first for npm cache
COPY frontend/package*.json frontend/

# Install frontend dependencies
RUN cd frontend && npm ci --legacy-peer-deps

# Copy frontend source and build
COPY frontend/ frontend/
RUN cd frontend && npm run build

# Copy application code (Python backend)
COPY app/ app/
COPY assets/ assets/
COPY *.py ./
COPY *.sh ./
COPY *.json ./

# Create output directories
RUN mkdir -p output/videos output/thumbnails output/reels output/schedules

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run uvicorn directly - PORT defaults to 8000 if not set
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
