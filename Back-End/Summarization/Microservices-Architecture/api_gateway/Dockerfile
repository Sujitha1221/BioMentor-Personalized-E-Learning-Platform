# Use a smaller base image to reduce size (~200MB instead of ~1GB)
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies efficiently
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip  

# Copy the rest of the application files
COPY . .

# Expose the API gateway service port
EXPOSE 8080

# Run the FastAPI API gateway with Uvicorn
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8080"]
