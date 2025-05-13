# Use a smaller base image (~25MB instead of ~1GB)
FROM python:3.9-slim

# Install necessary system dependencies (Java + essential libs)
RUN apt-get update && apt-get install -y --no-install-recommends default-jre libgomp1 && rm -rf /var/lib/apt/lists/*  

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip  


# Copy the entire project AFTER installing dependencies (improves caching)
COPY . .

# Expose the service port
EXPOSE 8002

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "summarization_service:app", "--host", "0.0.0.0", "--port", "8002"]
