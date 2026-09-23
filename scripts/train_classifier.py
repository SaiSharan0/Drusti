"""
scripts/train_classifier.py

DRUSTI — Real ResNet-50 Training on APTOS 2019 Blindness Detection Dataset.

Usage:
    python scripts/train_classifier.py --data-dir PATH_TO_APTOS_DIR --epochs 30

APTOS 2019 directory structure expected:
    PATH_TO_APTOS_DIR/
        train_images/         (folder with .png fundus images)
        train.csv             (columns: id_code, diagnosis)

Output:
    models/classifier/resnet50_dr.pt
"""

import argparse
import os
import sys
import time
import json
import random
from pathlib import Path

# Ensure project root is in path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms, models
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────────
NUM_CLASSES = 5
DR_LABELS = ["No DR", "Mild NPDR", "Moderate NPDR", "Severe NPDR", "Proliferative DR"]

IMAGE_SIZE = 224
BATCH_SIZE = 16
NUM_WORKERS = 0  # Safe default for Windows
SEED = 42

# ImageNet normalization (used because ResNet-50 was pretrained on ImageNet)
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD  = [0.229, 0.224, 0.225]

# ── Determinism ───────────────────────────────────────────────────────────────
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ── Dataset ───────────────────────────────────────────────────────────────────
class APTOSDataset(Dataset):
    """APTOS 2019 Blindness Detection dataset."""

    def __init__(self, df, images_dir: Path, transform=None):
        self.df = df.reset_index(drop=True)
        self.images_dir = Path(images_dir)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_id = row["id_code"]
        label = int(row["diagnosis"])

        img_path = self.images_dir / f"{img_id}.png"
        if not img_path.exists():
            img_path = self.images_dir / f"{img_id}.jpg"

        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label


# ── Transforms ────────────────────────────────────────────────────────────────
train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),
    transforms.RandomCrop(IMAGE_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
    transforms.ToTensor(),
    transforms.Normalize(NORM_MEAN, NORM_STD),
])

val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(NORM_MEAN, NORM_STD),
])


# ── Model ─────────────────────────────────────────────────────────────────────
def build_model(num_classes: int = NUM_CLASSES) -> nn.Module:
    """Build ResNet-50 with custom 5-class head."""
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, num_classes),
    )
    return model


# ── Training ─────────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Train ResNet-50 DR Classifier on APTOS 2019")
    parser.add_argument("--data-dir", required=True, help="Path to APTOS 2019 directory")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--output", default="models/classifier/resnet50_dr.pt")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        sys.exit(1)

    csv_path = data_dir / "train.csv"
    images_dir = data_dir / "train_images"
    if not csv_path.exists():
        print(f"ERROR: train.csv not found at {csv_path}")
        sys.exit(1)
    if not images_dir.exists():
        print(f"ERROR: train_images/ not found at {images_dir}")
        sys.exit(1)

    import pandas as pd
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} samples")
    print(f"Class distribution:\n{df['diagnosis'].value_counts().sort_index()}")

    # Train/val split (80/20)
    from sklearn.model_selection import train_test_split
    train_df, val_df = train_test_split(df, test_size=0.2, stratify=df["diagnosis"], random_state=SEED)
    print(f"Train: {len(train_df)} | Val: {len(val_df)}")

    # Weighted sampler to handle class imbalance
    class_counts = train_df["diagnosis"].value_counts().sort_index().values
    class_weights = 1.0 / class_counts
    sample_weights = class_weights[train_df["diagnosis"].values]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    train_dataset = APTOSDataset(train_df, images_dir, train_transform)
    val_dataset = APTOSDataset(val_df, images_dir, val_transform)

    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size,
        sampler=sampler, num_workers=NUM_WORKERS, pin_memory=False
    )
    val_loader = DataLoader(
        val_dataset, batch_size=args.batch_size,
        shuffle=False, num_workers=NUM_WORKERS, pin_memory=False
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice: {device}")

    model = build_model(NUM_CLASSES).to(device)

    # Weighted CE loss for imbalanced classes
    class_weights_tensor = torch.tensor(class_weights / class_weights.sum() * NUM_CLASSES, dtype=torch.float).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    best_val_acc = 0.0
    print("\n" + "="*60)
    print("DRUSTI — ResNet-50 Training on APTOS 2019")
    print("="*60)

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step()
        elapsed = time.time() - t0

        print(
            f"Epoch {epoch:02d}/{args.epochs} | "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
            f"Time: {elapsed:.1f}s"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            checkpoint = {
                "epoch": epoch,
                "val_acc": val_acc,
                "model_state_dict": model.state_dict(),
                "class_names": DR_LABELS,
                "num_classes": NUM_CLASSES,
                "image_size": IMAGE_SIZE,
                "norm_mean": NORM_MEAN,
                "norm_std": NORM_STD,
                "architecture": "resnet50",
            }
            torch.save(checkpoint, output_path)
            print(f"  ✓ New best! Saved to {output_path}")

    print(f"\nTraining complete. Best Val Accuracy: {best_val_acc:.4f}")
    print(f"Weights saved to: {output_path}")


if __name__ == "__main__":
    main()
