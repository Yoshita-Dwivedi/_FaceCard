FROM python:3.10-slim

# Install system dependencies required for dlib and face-recognition
RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libsm6 libxext6 libxrender-dev libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
