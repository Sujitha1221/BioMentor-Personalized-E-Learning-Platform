# BioMentor Q&A Service - Deployment Guide

This README provides detailed instructions to deploy the **BioMentor Q&A FastAPI microservice** on an **Azure VM** running Ubuntu. The service is exposed through **Nginx** and runs persistently using **systemd**.

---

## 🌟 Features

This project includes the following key features:

- 🔍 **AI-Powered Answer Generation**  
  Generate structured and essay-type answers using a custom-trained language model with Gemini refinement.

- 🧠 **Hybrid Answer Evaluation**  
  Uses SciBERT, TF-IDF, Jaccard similarity, and grammar analysis to score student answers.

- 🔐 **Content Moderation**  
  Detects inappropriate or toxic questions using a combination of rule-based and ML-based moderation techniques.

- 📊 **Student Analytics Dashboard**  
  Offers individual and group-level insights, including average scores, trends, feedback, and keyword-based recommendations.

- 🔄 **Question Assignment System**  
  Automatically assigns random structured and essay questions from a CSV dataset to each student.

- 🗂️ **MongoDB-Backed History**  
  All evaluations and assigned questions are stored for auditing and performance tracking.

- 🔁 **Personalized Learning Paths**  
  Based on student weaknesses, it generates suggestions and recommended reading material using semantic search (FAISS).

- 🚀 **REST API Interface**  
  Exposes endpoints for answer generation, evaluation, and analytics consumption.

- 🌐 **Production-Ready Deployment**  
  Configured with systemd and Nginx for stable service hosting and reverse proxy access.

---


## 📁 Project Structure

```
BioMentor-Personalized-E-Learning-Platform/
├── Back-End/
│   └── QnA/
│       ├── question_and_answer_api.py
│       ├── evaluate_answers.py
│       ├── exam_practice.py
│       ├── store_embeddings.py
│       ├── generate_answers.py
│       ├── predict_question_acceptability.py
│       ├── answer_evaluation_tool.py
│       ├── check_user_availability.py
│       └── requirements.txt
```

---

## ⚙️ Prerequisites

### 1. SSH Access
```bash
ssh-keygen
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 2. System Update & Dependencies
```bash
sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.10 openjdk-11-jdk python3.12-venv -y
```

### 3. Confirm Installations
```bash
python3.10 --version
java -version
```

---

## 🐍 Python Virtual Environment Setup

```bash
cd ~/BioMentor-Personalized-E-Learning-Platform/Back-End/QnA
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 🚀 Run the FastAPI App

### Dev Server (Hot Reload)
```bash
uvicorn question_and_answer_api:app --reload
```

### Production Server (Gunicorn)
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 question_and_answer_api:app
```

---

## 🛠️ Deploy as a Systemd Service

### 1. Create Service File
```bash
sudo nano /etc/systemd/system/qna.service
```

### 2. Paste Configuration
```ini
[Unit]
Description=Q&A FastAPI Service
After=network.target

[Service]
User=azureuser
WorkingDirectory=/home/azureuser/BioMentor-Personalized-E-Learning-Platform/Back-End/QnA
ExecStart=/home/azureuser/BioMentor-Personalized-E-Learning-Platform/Back-End/QnA/venv/bin/uvicorn question_and_answer_api:app --host 0.0.0.0 --port 8000
Restart=always
Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
Environment="PATH=/usr/lib/jvm/java-11-openjdk-amd64/bin:/home/azureuser/BioMentor-Personalized-E-Learning-Platform/Back-End/QnA/venv/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Service
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable qna
sudo systemctl start qna
```

---

## 🌐 Configure Nginx as Reverse Proxy

### 1. Install Nginx
```bash
sudo apt install nginx -y
```

### 2. Configure Site
```bash
sudo nano /etc/nginx/sites-available/api-gateway
```

Paste this config:
```nginx
server {
    listen 80;
    server_name <Public IP Address>;

    location /QnA/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable Config and Restart
```bash
sudo ln -s /etc/nginx/sites-available/api-gateway /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔐 Environment Variables (.env)
Set the variables in a `.env` file in your working directory:


---

## ✅ Health Check
Once deployed, visit:
```
http://<Public IP Address>/QnA/
```
Expected response:
```json
{"message": "Question and Answer API is running!"}
```

---

## 🧪 Running Tests

All test cases are written using `pytest`. To run them:

```bash
pytest
```

Make sure the environment is properly configured and MongoDB is running.

Test coverage includes:
- Answer generation and evaluation logic
- Question moderation and toxicity detection
- API endpoints and edge cases
- Analytics and scoring trends

---

## 📡 API Endpoints

### `GET /`
Health check.

### `POST /generate-answer`
Generate structured or essay answer.

### `POST /evaluate-answer`
Evaluate a user's answer using an AI-generated model answer.

### `POST /evaluate-passpaper-answer`
Evaluate a user's answer using a fixed stored pass paper answer.

### `GET /get-student-question/{student_id}`
Retrieve assigned structured and essay question.

### `POST /student-analytics`
Get performance analytics and personalized feedback.

