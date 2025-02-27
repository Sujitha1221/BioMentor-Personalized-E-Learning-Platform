FROM python:3.9
RUN apt-get update && apt-get install -y default-jre
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir easyocr 

CMD ["uvicorn", "text_extraction_service:app", "--host", "0.0.0.0", "--port", "8001"]
