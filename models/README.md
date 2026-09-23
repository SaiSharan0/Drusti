# Drusti — Model Files

This directory stores trained model weights. Do NOT commit large binary files to Git.

## Expected Structure

```
models/
├── classifier/
│   └── resnet50_dr.pt       # ResNet-50 5-class DR classifier
├── segmentation/
│   └── unet_lesions.pt      # U-Net lesion segmentation model
├── calibration/
│   └── temperature.json     # Temperature scaling parameters
└── README.md
```

## Classifier

- **Architecture:** ResNet-50, 5-class output
- **Classes:** 0=No DR, 1=Mild NPDR, 2=Moderate NPDR, 3=Severe NPDR, 4=PDR
- **Input:** 224×224 RGB, ImageNet-normalised
- **Training dataset:** APTOS 2019 (intended)
- **File:** `resnet50_dr.pt` — a PyTorch state_dict or checkpoint

## Segmentation (Optional)

- **Architecture:** U-Net
- **Target lesions:** Microaneurysms, Hemorrhages, Hard Exudates, Soft Exudates
- **Dataset:** IDRiD (intended)

## Calibration

- **Method:** Temperature scaling
- **File format:** JSON with `{"temperature": 1.5}`

## Usage

Place model files in the correct directories and set `DRUSTI_MODE=live` in `.env`.

If model files are absent the application will run in DEMO mode with clearly labelled demonstration data.
