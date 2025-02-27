# Use Python as base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the service port
EXPOSE 8000

# Run the monolith backend
CMD ["uvicorn", "monolith_backend:app", "--host", "0.0.0.0", "--port", "8000"]
