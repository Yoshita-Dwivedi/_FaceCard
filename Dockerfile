# Base Python image (3.10 works with dlib & face_recognition)
FROM python:3.10-slim

# Install system dependencies required for dlib and opencv
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    libpng-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the whole project
COPY . .

# Expose Flask/Gunicorn port
EXPOSE 8080

# Run app with Gunicorn (change app:app if entry point differs)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
