
# 🧠 BioMentor Summarization Module

A modular AI-powered backend component designed for the **BioMentor Personalized E-Learning Platform**. It processes educational content through document parsing, summarization, note structuring, and audio generation for A/L Biology students.

## 📌 Overview

This service allows users to:
- Upload documents (`.pdf`, `.docx`, `.pptx`, `.txt`)
- Generate concise **summaries**
- Create **structured notes** 
- Listen to **audio summaries**
- Download results in **PDF** and **MP3** formats

The system leverages a **fine-tuned Flan-T5-Base model** hosted on Hugging Face and a **Retrieval-Augmented Generation (RAG)** approach for content retrieval.

## 🚀 Features

- 📝 **Text & Document Summarization**
- ❓ **Query-Based Retrieval**
- 🧾 **Structured Notes Generator**
- 🔊 **Text-to-Speech**
- 📄 **PDF Export**
- 🌐 **Multilingual Support**
- 📡 **Hosted on Azure VM**
- 🔄 **CI/CD via GitHub Actions**

## 📁 Project Structure

```
BioMentor-Summarization/
├── summarization.py
├── summarization_functions.py
├── file_handler.py
├── voice_service.py
├── text_extraction_service.py
├── rag.py
├── requirements.txt
├── tests/
│   ├── test_file_handler.py
│   ├── test_integration.py
│   ├── test_rag.py
│   ├── test_text_extraction.py
│   └── test_voice_service.py
└── utils/
    └── dangerous_keywords.py
```

## 🔌 API Endpoints

| Endpoint                    | Method | Description |
|----------------------------|--------|-------------|
| `/process-document/`       | POST   | Summarize a file |
| `/process-query/`          | POST   | Query-based summary |
| `/summarize-text/`         | POST   | Plain text summary |
| `/generate-notes/`         | POST   | Structured notes |
| `/download-summary-text/`  | GET    | Download summary PDF |
| `/download-summary-audio/` | GET    | Download MP3 |
| `/download-notes/`         | GET    | Download notes PDF |


## ⚙️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/BioMentor-Personalized-E-Learning-Platform.git
cd BioMentor-Personalized-E-Learning-Platform/Back-End/Summarization/Monolithic-Architecture
```

### 2. Create & Activate Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install System Packages (Linux)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

## 🖥️ Running the Service

```bash
uvicorn summarization:app --host 0.0.0.0 --port 8002
```


## 🛠️ Deployment (Azure)

- OS: Ubuntu 24.04 LTS
- Port Rules: 8002 (API), 80 (Nginx)
- Hosted on Azure VM with static IP
- Managed using systemd (`summarize.service`)
- Reverse proxy through Nginx

## 🌐 Nginx Config

```nginx
server {
    listen 80;
    server_name <Your-VM-IP>;
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_read_timeout 600;
        proxy_connect_timeout 600;
    }
}
```

## ⚙️ Systemd Service

```ini
[Service]
WorkingDirectory=/home/azureuser/...
ExecStart=/path/to/venv/bin/uvicorn summarization:app --host 0.0.0.0 --port 8002
Restart=always
```

## 🔁 CI/CD (GitHub Actions)

Triggered on push to `main`, auto-deploys to VM:
- Pulls latest code
- Installs dependencies
- Restarts service

## 🧪 Testing

Run with:

```bash
pytest tests/
```

Covers:
- PDF/text extraction
- Audio generation
- Summarization logic
- RAG model output

## 🔍 Example Request

```bash
curl -X POST http://<VM-IP>/summarize-text/ -F "text=The mitochondria is the powerhouse of the cell" -F "word_count=150"
```


