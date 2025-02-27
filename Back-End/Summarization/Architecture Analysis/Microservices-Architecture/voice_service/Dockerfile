FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install espeak-ng for text-to-speech
RUN apt-get update && apt-get install -y espeak-ng

COPY . .

CMD ["uvicorn", "voice_service:app", "--host", "0.0.0.0", "--port", "8003"]
