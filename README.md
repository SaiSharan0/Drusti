# Drusti

**Explainable AI-Based Diabetic Retinopathy Screening System**

Drusti is a local-first AI-assisted retinal screening application designed to help healthcare workers and clinicians perform structured diabetic retinopathy screening using retinal fundus images.

> **Medical Disclaimer:** Drusti is a screening support system. It does NOT replace clinical examination by a qualified healthcare professional. Results are not a definitive medical diagnosis.

## Features

- Patient management with generated patient codes
- Retinal fundus image upload with quality assessment
- 5-class DR classification (ResNet-50 architecture)
- Calibrated probability display
- Grad-CAM visual explanation
- Lesion evidence analysis
- Evidence-aware screening decisions (Clear / Refer / Escalate)
- Clinician review workflow
- Printable screening reports
- Nearby eye-care and diabetes facility locator
- Analytics dashboard
- Demo mode for demonstration without model weights

## Architecture

```
Browser → Next.js (React/TypeScript) → FastAPI (Python) → MySQL
                                         ↓
                                    ML Pipeline:
                              Quality Gate → ResNet-50
                              → Calibration → Grad-CAM
                              → Lesion Detector → Decision Engine
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Database | MySQL 8 |
| ML | PyTorch, torchvision, OpenCV |
| Maps | Leaflet, OpenStreetMap |

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **MySQL** 8.x

## MySQL Setup

```sql
CREATE DATABASE drusti CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Environment Variables

Copy the example:

```bash
cp .env.example backend/.env
```

Edit `backend/.env` with your MySQL credentials.

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MYSQL_HOST` | localhost | MySQL host |
| `MYSQL_PORT` | 3306 | MySQL port |
| `MYSQL_DATABASE` | drusti | Database name |
| `MYSQL_USER` | root | Database user |
| `MYSQL_PASSWORD` | (empty) | Database password |
| `DRUSTI_MODE` | demo | `demo` or `live` |
| `SECRET_KEY` | (change) | JWT signing key |

## Installation

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running the Application

### Quick Start (Windows)

```powershell
.\start-dev.ps1
```

### Quick Start (Linux/macOS)

```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Manual Start

Backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm run dev
```

Access:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Demo Mode

Set `DRUSTI_MODE=demo` in `.env`. The application provides deterministic demo screening cases labelled **DEMO MODE**.

Demo credentials:
- `doctor@drusti.local` / `drusti123` (Clinician)
- `worker@drusti.local` / `drusti123` (Health Worker)
- `admin@drusti.local` / `drusti123` (Admin)

## Live Mode

1. Place trained ResNet-50 weights at `models/classifier/resnet50_dr.pt`
2. Optionally place U-Net weights at `models/segmentation/unet_lesions.pt`
3. Optionally create `models/calibration/temperature.json`
4. Set `DRUSTI_MODE=live` in `.env`

See `models/README.md` for model specifications.

## Folder Structure

```
drusti/
├── frontend/          Next.js application
├── backend/           FastAPI application
│   ├── app/
│   │   ├── api/       Route handlers
│   │   ├── core/      Config, security, logging
│   │   ├── database/  SQLAlchemy session, seed
│   │   ├── models/    ORM models
│   │   ├── schemas/   Pydantic schemas
│   │   ├── services/  Business logic
│   │   └── ml/        ML pipeline
│   └── alembic/       Database migrations
├── models/            Model weight files
├── data/              Uploads and demo data
├── scripts/           Utility scripts
├── tests/             Test files
└── docs/              Documentation
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| MySQL connection refused | Ensure MySQL is running and credentials are correct |
| Port 8000 in use | Change port: `uvicorn app.main:app --port 8001` |
| Model not configured error | Expected in demo mode; place weights for live mode |
| npm install fails | Delete `node_modules` and `package-lock.json`, retry |

## Medical Disclaimer

Drusti provides AI-assisted screening support and does not replace clinical examination by a qualified healthcare professional. Screening results should be interpreted by trained medical personnel. The system is a research prototype and has not been clinically validated for diagnostic use.
