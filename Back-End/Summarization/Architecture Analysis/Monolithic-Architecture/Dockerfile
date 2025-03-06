# Use a smaller base image for efficiency
FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends default-jre libgomp1 && rm -rf /var/lib/apt/lists/*  


# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install dependencies efficiently and remove pip cache in the same line
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Copy the entire application after dependencies are installed
COPY . .

# Expose the application port
EXPOSE 8070

# Run the monolith backend using Uvicorn
CMD ["uvicorn", "summarization:app", "--host", "0.0.0.0", "--port", "8070"]
