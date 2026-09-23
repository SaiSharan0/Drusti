# Drusti Architecture

## System Overview

```
┌──────────────────┐
│   Browser/UI     │
│   (Next.js)      │
│   Port 3000      │
└────────┬─────────┘
         │ HTTP/REST
┌────────▼─────────┐
│   FastAPI         │
│   Port 8000       │
├───────────────────┤
│   API Routes      │
│   Services        │
│   ML Pipeline     │
└────────┬─────────┘
         │ SQLAlchemy
┌────────▼─────────┐
│   MySQL 8         │
│   Port 3306       │
└──────────────────┘
```

## ML Pipeline

```
Fundus Image
     │
     ▼
 Preprocessing (resize, normalise)
     │
     ▼
 Quality Gate (blur, brightness, contrast, field)
     │
     ├── POOR → Escalate
     │
     ▼
 ResNet-50 Classifier → 5-class probabilities
     │
     ▼
 Temperature Scaling (optional calibration)
     │
     ▼
 Grad-CAM (layer4 activations + gradients)
     │
     ▼
 Lesion Detector (U-Net / morphological)
     │
     ▼
 Decision Engine → CLEAR / REFER / ESCALATE
```

## Mode Architecture

| Mode | Behaviour |
|------|-----------|
| `demo` | Deterministic fixture cases, clearly labelled |
| `live` | Real model inference, fails safely if weights absent |
