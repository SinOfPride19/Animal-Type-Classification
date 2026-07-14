"""
Dataset Preparation Script — ATC System
Splits raw images into train/val sets and validates structure.

Expected raw layout:
  <src>/cow/     *.jpg, *.png ...
  <src>/buffalo/ *.jpg, *.png ...

Output layout:
  <dst>/train/cow/
  <dst>/train/buffalo/
  <dst>/val/cow/
  <dst>/val/buffalo/

Usage:
  python prepare_dataset.py --src ./raw_images --dst ./dataset --val_split 0.2
  python prepare_dataset.py --generate_dummy --dst ./dataset   # create synthetic test data
"""

import argparse
import logging
import os
import random
import shutil
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

CLASSES = ["cow", "buffalo"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# ─── Real dataset split ───────────────────────────────────────────────────────

def split_dataset(src: str, dst: str, val_split: float = 0.2, seed: int = 42) -> None:
    random.seed(seed)
    src_path = Path(src)
    dst_path = Path(dst)

    total_copied = 0
    for cls in CLASSES:
        cls_path = src_path / cls
        if not cls_path.exists():
            logger.warning("Class folder not found: %s", cls_path)
            continue

        images: List[Path] = [
            p for p in cls_path.iterdir()
            if p.suffix.lower() in IMAGE_EXTENSIONS
        ]
        if not images:
            logger.warning("No images found in %s", cls_path)
            continue

        random.shuffle(images)
        split_idx = int(len(images) * (1 - val_split))
        train_imgs = images[:split_idx]
        val_imgs   = images[split_idx:]

        for split, imgs in [("train", train_imgs), ("val", val_imgs)]:
            out_dir = dst_path / split / cls
            out_dir.mkdir(parents=True, exist_ok=True)
            for img_path in imgs:
                shutil.copy2(str(img_path), str(out_dir / img_path.name))
                total_copied += 1

        logger.info(
            "Class '%s': total=%d | train=%d | val=%d",
            cls, len(images), len(train_imgs), len(val_imgs)
        )

    logger.info("Dataset prepared at %s | total=%d images", dst_path, total_copied)


# ─── Dummy dataset generator ─────────────────────────────────────────────────

def _draw_cow(size: Tuple[int, int]) -> Image.Image:
    """Synthesise a minimal cow-like shape (light, white/brown)."""
    img = Image.new("RGB", size, color=(220, 200, 170))
    draw = ImageDraw.Draw(img)
    w, h = size
    # Body ellipse
    draw.ellipse([w*0.15, h*0.3, w*0.85, h*0.7], fill=(230, 210, 185))
    # Head
    draw.ellipse([w*0.72, h*0.2, w*0.92, h*0.45], fill=(225, 205, 180))
    # Legs
    for lx in [0.25, 0.4, 0.55, 0.7]:
        draw.rectangle([w*lx, h*0.68, w*(lx+0.05), h*0.9], fill=(200, 180, 160))
    # Dark spots
    for _ in range(3):
        sx = random.randint(int(w*0.2), int(w*0.65))
        sy = random.randint(int(h*0.3), int(h*0.6))
        sr = random.randint(10, 30)
        draw.ellipse([sx, sy, sx+sr, sy+sr//2], fill=(90, 60, 40))
    img = img.filter(ImageFilter.SMOOTH)
    return img


def _draw_buffalo(size: Tuple[int, int]) -> Image.Image:
    """Synthesise a minimal buffalo-like shape (dark grey/black)."""
    img = Image.new("RGB", size, color=(180, 170, 160))
    draw = ImageDraw.Draw(img)
    w, h = size
    # Body (darker, wider)
    draw.ellipse([w*0.12, h*0.28, w*0.88, h*0.72], fill=(55, 50, 48))
    # Head (larger, more forward)
    draw.ellipse([w*0.70, h*0.18, w*0.94, h*0.48], fill=(45, 40, 38))
    # Horns
    draw.arc([w*0.62, h*0.10, w*0.82, h*0.28], start=200, end=340, fill=(30, 25, 20), width=4)
    # Legs
    for lx in [0.22, 0.38, 0.55, 0.70]:
        draw.rectangle([w*lx, h*0.70, w*(lx+0.06), h*0.92], fill=(40, 35, 32))
    img = img.filter(ImageFilter.SMOOTH)
    return img


def generate_dummy_dataset(dst: str, count_per_class: int = 50) -> None:
    """Generate synthetic dummy images for testing when real dataset is unavailable."""
    dst_path = Path(dst)
    sizes = [(400, 300), (500, 350), (450, 320)]
    generators = {"cow": _draw_cow, "buffalo": _draw_buffalo}

    for split in ["train", "val"]:
        n = count_per_class if split == "train" else max(10, count_per_class // 5)
        for cls in CLASSES:
            out_dir = dst_path / split / cls
            out_dir.mkdir(parents=True, exist_ok=True)
            for i in range(n):
                size = random.choice(sizes)
                img = generators[cls](size)
                # Add slight noise
                arr = np.array(img).astype(np.float32)
                noise = np.random.normal(0, 8, arr.shape)
                arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
                img = Image.fromarray(arr)
                img.save(str(out_dir / f"{cls}_{split}_{i:04d}.jpg"), quality=90)
            logger.info("Generated %d dummy %s/%s images", n, split, cls)

    logger.info("Dummy dataset ready at: %s", dst_path)


# ─── Validation ───────────────────────────────────────────────────────────────

def validate_dataset(dst: str) -> bool:
    dst_path = Path(dst)
    ok = True
    for split in ["train", "val"]:
        for cls in CLASSES:
            folder = dst_path / split / cls
            if not folder.exists():
                logger.error("Missing: %s", folder)
                ok = False
                continue
            imgs = [f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]
            logger.info("  %s/%s: %d images", split, cls, len(imgs))
            if len(imgs) == 0:
                logger.warning("  ⚠️  Empty folder: %s", folder)
                ok = False
    return ok


def main():
    parser = argparse.ArgumentParser(description="Prepare ATC dataset")
    parser.add_argument("--src",             type=str,   default=None,    help="Source raw image directory")
    parser.add_argument("--dst",             type=str,   default="./dataset")
    parser.add_argument("--val_split",       type=float, default=0.2)
    parser.add_argument("--seed",            type=int,   default=42)
    parser.add_argument("--generate_dummy",  action="store_true",         help="Generate synthetic dummy images")
    parser.add_argument("--count",           type=int,   default=50,      help="Images per class for dummy generation")
    parser.add_argument("--validate",        action="store_true",         help="Only validate existing dataset")
    args = parser.parse_args()

    if args.validate:
        ok = validate_dataset(args.dst)
        logger.info("Dataset valid: %s", ok)
        return

    if args.generate_dummy:
        generate_dummy_dataset(args.dst, args.count)
    elif args.src:
        split_dataset(args.src, args.dst, args.val_split, args.seed)
    else:
        logger.error("Provide --src <raw_dir> or --generate_dummy")
        return

    validate_dataset(args.dst)


if __name__ == "__main__":
    main()
