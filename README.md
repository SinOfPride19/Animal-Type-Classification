# 🐄 Animal Type Classification (ATC) System
### AI-Based Cattle & Buffalo Classification using Computer Vision & Deep Learning

> A full-stack AI application that classifies cattle and buffalo using Convolutional Neural Networks (CNN), YOLOv8, and OpenCV. The system performs automated image classification, extracts animal morphometric measurements, calculates ATC scores, stores prediction records, and provides analytical reports through an interactive dashboard.

---

# 📌 Project Overview

The Animal Type Classification (ATC) System is an AI-powered livestock analysis platform developed to automate cattle and buffalo classification from images. The application combines deep learning, computer vision, and a modern web interface to assist researchers and livestock professionals in analyzing animals efficiently.

---

# 🏗 System Architecture

```
                    User
                      │
                      ▼
            Upload Animal Image
                      │
                      ▼
       ┌──────────────────────────────┐
       │ React + TypeScript Frontend  │
       │ Dashboard • Upload • Reports │
       └───────────────┬──────────────┘
                       │
                 REST API (FastAPI)
                       │
      ┌────────────────┴────────────────┐
      │                                 │
      ▼                                 ▼
 Image Classification            Database Storage
 (CNN + YOLOv8)                   SQLAlchemy ORM
      │                                 │
      └──────────────┬──────────────────┘
                     ▼
            OpenCV Measurements
                     │
                     ▼
             ATC Score Calculation
                     │
                     ▼
            Prediction & Reports
```

---

# 📂 Project Structure

```
ATC-PROJECT
│
├── backend
│   ├── app
│   │   ├── api
│   │   │   ├── upload.py
│   │   │   ├── classify.py
│   │   │   ├── records.py
│   │   │   └── reports.py
│   │   │
│   │   ├── core
│   │   │   ├── config.py
│   │   │   └── logging_config.py
│   │   │
│   │   ├── data
│   │   │   └── storage.py
│   │   │
│   │   ├── db
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   │
│   │   ├── ml
│   │   │   ├── inference.py
│   │   │   ├── pipeline.py
│   │   │   ├── cv_measurement.py
│   │   │   ├── scaling.py
│   │   │   └── scoring.py
│   │   │
│   │   ├── schemas
│   │   │   └── schemas.py
│   │   │
│   │   └── main.py
│   │
│   ├── services
│   │   ├── pipeline.py
│   │   └── atc_score.py
│   │
│   ├── tests
│   ├── runs
│   ├── requirements.txt
│   ├── Dockerfile
│   └── yolov8n.pt
│
├── frontend
│   ├── src
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker
├── docker-compose.yml
├── create_project_zip.py
└── README.md
```

---

# 🚀 Features

- AI-based Cattle & Buffalo Classification
- CNN-based Deep Learning Model
- YOLOv8 Animal Detection
- OpenCV Morphometric Measurement
- Automated ATC Score Calculation
- FastAPI REST APIs
- React Dashboard
- Upload & Analyze Images
- Record Management
- Analytical Reports
- Docker Support
- Modular Project Architecture

---

# 🤖 Machine Learning Pipeline

```
Animal Image
      │
      ▼
YOLOv8 Detection
      │
      ▼
Image Cropping
      │
      ▼
OpenCV Processing
      │
      ▼
CNN Classification
      │
      ▼
Feature Extraction
      │
      ▼
ATC Score Calculation
      │
      ▼
Store in Database
      │
      ▼
Display Result
```

---

# ⚙ Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | React, TypeScript, Tailwind CSS, Vite |
| Backend | FastAPI, Python |
| Object Detection | YOLOv8 |
| Computer Vision | OpenCV |
| Data Processing | NumPy, Pandas |
| Containerization | Docker |
| Version Control | Git & GitHub |

---

# 📊 AI Workflow

1. User uploads an animal image.
2. YOLOv8 detects the animal.
3. OpenCV preprocesses the image.
4. CNN classifies the image as Cattle or Buffalo.
5. Morphometric features are extracted.
6. ATC score is calculated.
7. Results are stored in the database.
8. Dashboard displays reports and analytics.

---

# 📈 Performance

| Metric | Value |
|---------|-------|
| Classification Accuracy | **88.89%** |
| Model | CNN |
| Detection | YOLOv8 |
| Image Processing | OpenCV |

---

# 💻 Running the Project

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Docker

```bash
docker-compose up --build
```

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /upload | Upload Animal Image |
| POST | /classify | Perform Classification |
| GET | /records | View Prediction Records |
| GET | /reports | Analytics Dashboard |

---

# 🔮 Future Enhancements

- Breed Identification
- Weight Estimation
- Disease Detection
- Mobile Application
- Cloud Deployment
- Real-time Camera Detection
- Multi-Animal Detection

---

# 👨‍💻 Developer

**Vidyadhar**

B.Tech Computer Science Engineering

SRM Institute of Science and Technology

Artificial Intelligence • Machine Learning • Computer Vision

---

# 📄 License

This project is developed for academic and research purposes.
