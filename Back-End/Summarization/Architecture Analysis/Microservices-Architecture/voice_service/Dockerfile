# Use a smaller base image to reduce size
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies efficiently and remove pip cache in the same line
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Install espeak-ng for text-to-speech and clean up unnecessary files
RUN apt-get update && apt-get install -y espeak-ng && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application files
COPY . .

# Expose the service port
EXPOSE 8003

# Run the FastAPI voice service with Uvicorn
CMD ["uvicorn", "voice_service:app", "--host", "0.0.0.0", "--port", "8003"]
