# Base image
FROM python:3.10-slim

# Enable swap to reduce OOM errors
RUN apt-get update && apt-get install -y util-linux \
    && fallocate -l 4G /swapfile && chmod 600 /swapfile \
    && mkswap /swapfile && swapon /swapfile

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
