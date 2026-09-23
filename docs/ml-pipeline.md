# Drusti ML Pipeline

## Overview

The ML pipeline processes a retinal fundus image through multiple stages to produce a screening recommendation.

## Pipeline Stages

### 1. Image Validation
- Format check (JPEG, PNG)
- Dimension validation
- Corruption detection

### 2. Quality Gate
- **Blur detection** — Laplacian variance
- **Brightness** — Mean pixel intensity
- **Contrast** — Standard deviation
- **Retinal field visibility** — Binary thresholding + area ratio
- Output: `good` or `poor`

### 3. DR Classification
- **Model:** ResNet-50
- **Input:** 224×224 RGB, ImageNet-normalised
- **Output:** 5-class probabilities
- **Classes:** No DR, Mild NPDR, Moderate NPDR, Severe NPDR, PDR

### 4. Probability Calibration
- **Method:** Temperature scaling
- **Config:** `models/calibration/temperature.json`
- If unavailable, raw softmax is used (labelled as uncalibrated)

### 5. Grad-CAM
- Hooks into ResNet-50 `layer4`
- Captures forward activations and backward gradients
- Produces attention heatmap overlaid on original image

### 6. Lesion Detection
- **Model:** U-Net (when available)
- **Fallback:** Classical morphological candidate detection
- **Targets:** Microaneurysms, Hemorrhages, Hard Exudates, Soft Exudates

### 7. Decision Engine
- Combines quality, classification, confidence, and evidence
- Outputs: `CLEAR`, `REFER`, or `ESCALATE`

## Important Notes

- Model outputs are screening indicators, not clinical diagnoses
- Demo mode uses deterministic fixture data, not model inference
- Live mode fails safely if model weights are absent
