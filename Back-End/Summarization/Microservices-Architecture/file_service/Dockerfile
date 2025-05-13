# Use a smaller base image to reduce size
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies efficiently
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip 

# Copy the rest of the application files
COPY . .

# Expose the service port
EXPOSE 8004

# Run the FastAPI file service with Uvicorn
CMD ["uvicorn", "file_service:app", "--host", "0.0.0.0", "--port", "8004"]
