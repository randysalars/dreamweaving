FROM python:3.11-slim

# Install system dependencies (ffmpeg is crucial for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set Python path to include project root
ENV PYTHONPATH=/app

# Default command to run the worker
CMD ["python", "worker.py"]
