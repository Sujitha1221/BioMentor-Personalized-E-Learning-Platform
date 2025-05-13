# Use a smaller and optimized base image
FROM python:3.9-slim

# Install required dependencies, including Java for additional processing if needed
RUN apt-get update && apt-get install -y default-jre && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies efficiently and remove pip cache in the same line
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Copy the rest of the application files
COPY . .

# Expose the service port
EXPOSE 8001

# Run the FastAPI text extraction service with Uvicorn
CMD ["uvicorn", "text_extraction_service:app", "--host", "0.0.0.0", "--port", "8001"]
