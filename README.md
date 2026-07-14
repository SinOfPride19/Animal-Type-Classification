# 🐄 Animal Type Classification (ATC) System
### Rashtriya Gokul Mission | IEEE Research Project

> AI-powered bovine morphometric classification using YOLOv8 + ResNet50 + OpenCV.
> Classifies Cow vs Buffalo and computes ATC scores using real geometric measurements.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend  (React 18 + TypeScript + Tailwind + Recharts)        │
│  Dashboard · New Classification · Records · Reports             │
└─────────────────┬───────────────────────────────────────────────┘
                  │  REST API (JSON)
┌─────────────────▼───────────────────────────────────────────────┐
│  Backend  (FastAPI + SQLAlchemy async)                          │
│  POST /upload  POST /classify  GET /records  GET /reports       │
└────────┬──────────────┬────────────────────────────────────────-┘
         │              │
┌────────▼──────┐  ┌────▼────────────────────────────────────────┐
│  MySQL 8.0    │  │  ML Pipeline                                 │
│  animals      │  │  1. YOLOv8n  → detect animal                │
│  images       │  │  2. ResNet50 → cow vs buffalo               │
│  classif.     │  │  3. OpenCV   → contour + keypoints          │
│  scores       │  │  4. Geometry → body_length, height, girth   │
└───────────────┘  │  5. ATC formula → final score + grade       │
                   └─────────────────────────────────────────────┘
```

## 📦 Project Structure

```
atc-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings
│   │   │   └── logging_config.py
│   │   ├── db/
│   │   │   ├── database.py      # Async SQLAlchemy engine
│   │   │   └── models.py        # ORM models (4 tables)
│   │   ├── ml/
│   │   │   ├── pipeline.py      # OpenCV morphometric pipeline
│   │   │   ├── scoring.py       # ATC weighted formula
│   │   │   └── inference.py     # YOLOv8 + ResNet50 orchestrator
│   │   ├── api/
│   │   │   ├── upload.py        # POST /upload
│   │   │   ├── classify.py      # POST /classify
│   │   │   ├── records.py       # GET /records
│   │   │   └── reports.py       # GET /reports
│   │   └── schemas/schemas.py   # Pydantic request/response models
│   ├── tests/test_system.py     # pytest test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Router
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx    # Stats + charts
│   │   │   ├── ClassifyPage.tsx # 4-step wizard
│   │   │   ├── RecordsPage.tsx  # Paginated table
│   │   │   └── ReportsPage.tsx  # Analytics charts
│   │   ├── components/
│   │   │   ├── layout/Layout.tsx
│   │   │   └── charts/ScoreRadarChart.tsx
│   │   ├── services/api.ts      # Axios API client
│   │   └── types/index.ts       # TypeScript interfaces
│   ├── Dockerfile
│   └── nginx.conf
├── ml/
│   ├── scripts/
│   │   ├── train.py             # ResNet50 training pipeline
│   │   └── prepare_dataset.py   # Dataset split + dummy gen
│   └── dataset/                 # train/val/test splits
│       ├── train/{cow,buffalo}/
│       ├── val/{cow,buffalo}/
│       └── test/
├── docker/
│   └── mysql/init.sql           # Full MySQL schema
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start (Docker — Recommended)

### Prerequisites
- Docker ≥ 24.0
- Docker Compose ≥ 2.0
- 8 GB RAM recommended (PyTorch)

### 1. Clone / extract the project
```bash
unzip atc-system.zip
cd atc-system
```

### 2. Configure environment
```bash
cp backend/.env.example backend/.env
# Edit backend/.env if needed (default values work for Docker)
```

### 3. Launch full stack
```bash
docker-compose up --build
```

First build takes ~5–10 minutes (PyTorch download + YOLOv8 weights).

### 4. Access the system
| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:3000      |
| API Docs | http://localhost:8000/api/docs |
| Health   | http://localhost:8000/api/health |

---

## 🛠️ Local Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start MySQL (or update .env to point to your instance)
cp .env.example .env
# Edit .env: set DB_HOST=localhost

uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Starts on http://localhost:3000
```

### Run Tests
```bash
cd backend
pytest tests/ -v --tb=short
```

---

## 🤖 ML Pipeline Details

### ATC Scoring Formula
```
Final Score = 0.15 × Body Length Score
            + 0.15 × Height Score
            + 0.15 × Chest Girth Score
            + 0.10 × Rump Angle Score
            + 0.10 × Rump Width Score
            + 0.10 × Body Depth Score
            + 0.10 × Dairy Character Score
            + 0.075 × Feet & Legs Score
            + 0.075 × Udder Score
```

### Grading
| Score Range | Grade      |
|-------------|------------|
| 85 – 100    | Excellent  |
| 70 – 84     | Good Plus  |
| 50 – 69     | Good       |
| < 50        | Average    |

### Image Processing Pipeline
1. **YOLOv8n** detects the animal and returns a bounding box
2. **GrabCut + Canny** extracts foreground mask and contour
3. **Keypoint estimation** locates head, tail, withers, hoof from convex hull
4. **Geometric measurement** computes pixel distances for all traits
5. **Pixel → cm normalisation** using reference body length (160 cm)
6. **ATC scoring** applies weighted formula with Gaussian and range-based scorers

### Training Your Own Classifier
```bash
# 1. Prepare dataset
cd ml/scripts
python prepare_dataset.py --src /path/to/raw_images --dst ../dataset

# OR generate dummy images for testing:
python prepare_dataset.py --generate_dummy --dst ../dataset --count 100

# 2. Train
python train.py --data_dir ../dataset --model_dir ../models --epochs 30

# 3. Model saved to:
#    ml/models/classifier.pt
```

---

## 🗄️ Database Tables

| Table           | Description                            |
|-----------------|----------------------------------------|
| `animals`       | Animal master record (tag, breed, owner) |
| `images`        | Uploaded image metadata               |
| `classifications` | AI inference results + measurements |
| `scores`        | ATC component + final scores          |

---

## 🔌 API Reference

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| POST   | `/api/v1/upload`      | Upload animal image                |
| POST   | `/api/v1/classify`    | Run full ATC pipeline              |
| GET    | `/api/v1/records`     | List classification records        |
| GET    | `/api/v1/records/:id` | Get single record detail           |
| GET    | `/api/v1/reports`     | Aggregated statistics              |
| GET    | `/api/health`         | System health check                |

Full interactive docs: `http://localhost:8000/api/docs`

---

## 🧪 Test Script (cURL)
```bash
# Health check
curl http://localhost:8000/api/health

# Upload an image
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/cow.jpg" \
  -F "tag_number=TEST-001" \
  -F "breed=Gir"

# Classify (use image_id from upload response)
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"image_id": "<image_id_from_upload>"}'

# Get records
curl http://localhost:8000/api/v1/records?page=1&page_size=10

# Get reports
curl http://localhost:8000/api/v1/reports
```

---

## 📋 Tech Stack Summary

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | React 18, TypeScript, Tailwind CSS, Recharts |
| Backend   | FastAPI, SQLAlchemy (async), Pydantic v2 |
| Database  | MySQL 8.0 (aiomysql driver)        |
| ML        | PyTorch, ResNet50, YOLOv8 (Ultralytics) |
| Vision    | OpenCV (GrabCut, contour, geometry) |
| Container | Docker, Docker Compose, Nginx       |

---

## 📚 References
- ICAR Linear Appraisal Guidelines for Dairy Cattle
- NABARD Bovine Breed Standards (Gir, Sahiwal, Murrah)
- He et al., "Deep Residual Learning for Image Recognition" (ResNet)
- Jocher et al., "YOLOv8" (Ultralytics, 2023)

---

*Developed for Rashtriya Gokul Mission & IEEE paper submission.*
*ATC System v1.0 — Production-ready bovine AI classification.*
