"""
Inference Engine — ATC System
Orchestrates: YOLOv8 detection → Classifier → OpenCV pipeline → ATC Scoring

Model loading strategy:
  1. Load saved classifier (.pt) if exists
  2. Load YOLOv8 nano (auto-download or local)
  3. If no classifier found, use heuristic fallback
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional, Tuple
import io

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image as PILImage

from app.core.config import settings
from app.ml.pipeline import ImageProcessingPipeline, BoundingBox, MorphometricResult
from app.ml.scoring import ATCScoringEngine, ATCScoringResult

logger = logging.getLogger(__name__)


# ─── Classifier Model ─────────────────────────────────────────────────────────

class BovineClassifier(nn.Module):
    """
    Transfer learning classifier: ResNet50 backbone.
    Binary output: [cow, buffalo]
    """
    CLASS_NAMES = ["cow", "buffalo"]

    def __init__(self, num_classes: int = 2, pretrained: bool = False):
        super().__init__()
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        backbone = models.resnet50(weights=weights)
        # Replace final FC layer
        in_features = backbone.fc.in_features
        backbone.fc = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )
        self.model = backbone

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)


# ─── Inference Engine ─────────────────────────────────────────────────────────

class InferenceEngine:
    """
    Full inference pipeline:
      1. YOLOv8 animal detection
      2. ResNet50 species classification
      3. OpenCV morphometric measurement
      4. ATC scoring
    """

    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD  = [0.229, 0.224, 0.225]

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("InferenceEngine using device: %s", self.device)

        self.classifier = self._load_classifier()
        self.yolo_model  = self._load_yolo()
        self.pipeline    = ImageProcessingPipeline()
        self.scorer      = ATCScoringEngine()

        self.transform = transforms.Compose([
            transforms.Resize((settings.IMAGE_SIZE, settings.IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.IMAGENET_MEAN, std=self.IMAGENET_STD),
        ])

    # ── Model Loading ─────────────────────────────────────────────────────────

    def _load_classifier(self) -> Optional[BovineClassifier]:
        try:
            BASE_DIR = Path(__file__).resolve().parents[3]
            model_path = BASE_DIR / "core_ml" / "models" / "model.pth"

            logger.info(f"Looking for model at: {model_path}")

            if model_path.exists():
                model = BovineClassifier(num_classes=settings.NUM_CLASSES, pretrained=False)

                checkpoint = torch.load(str(model_path), map_location=self.device)
                state = checkpoint.get("model_state_dict", checkpoint)

                model.load_state_dict(state)
                model.eval()
                model.to(self.device)

                logger.info("✅ Classifier loaded successfully")
                return model
            else:
                logger.warning(f"❌ Model not found at {model_path}")

        except Exception as e:
            logger.error(f"🔥 Error loading classifier: {e}")

        logger.warning("⚠️ Using heuristic fallback")
        return None

    def _load_yolo(self):
        try:
            from ultralytics import YOLO
            yolo_path = Path(settings.YOLO_MODEL_PATH)
            if yolo_path.exists():
                model = YOLO(str(yolo_path))
            else:
                # Auto-download YOLOv8 nano
                model = YOLO("yolov8n.pt")
            logger.info("✅ YOLOv8 model loaded")
            return model
        except Exception as e:
            logger.warning("⚠️ YOLOv8 not available: %s", e)
            return None

    # ── Main Inference ────────────────────────────────────────────────────────

    def run(self, image_path: str) -> dict:
        """
        Run full inference pipeline on an image file.

        Returns:
            dict with keys: predicted_class, confidence, bbox, measurements, score, processing_time_ms
        """
        t0 = time.time()

        # Load image
        bgr_image = cv2.imread(image_path)
        if bgr_image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        # Step 1: Detection
        bbox, det_conf = self._detect_animal(bgr_image)

        # Step 2: Classification
        predicted_class, confidence = self._classify(bgr_image, bbox)

        # Step 3: Morphometric pipeline
        measurements: MorphometricResult = self.pipeline.process(bgr_image, bbox)

        # Step 4: ATC Scoring
        scoring_result: ATCScoringResult = self.scorer.compute(
            measurements, predicted_class, confidence
        )

        elapsed_ms = (time.time() - t0) * 1000

        return {
            "predicted_class": predicted_class,
            "confidence": float(confidence),
            "detection_confidence": float(det_conf) if det_conf else None,
            "bbox": {
                "x1": float(bbox.x1), "y1": float(bbox.y1),
                "x2": float(bbox.x2), "y2": float(bbox.y2),
                "confidence": float(bbox.confidence),
            } if bbox else None,
            "measurements": {
                "body_length_px": measurements.body_length_px,
                "height_px": measurements.height_px,
                "chest_width_px": measurements.chest_width_px,
                "chest_girth_px": measurements.chest_girth_px,
                "body_depth_px": measurements.body_depth_px,
                "rump_width_px": measurements.rump_width_px,
                "pixel_per_cm": measurements.pixel_per_cm,
                "body_length_cm": measurements.body_length_cm,
                "height_cm": measurements.height_cm,
                "chest_girth_cm": measurements.chest_girth_cm,
                "body_depth_cm": measurements.body_depth_cm,
                "rump_width_cm": measurements.rump_width_cm,
            },
            "score": {
                "final_score": scoring_result.final_score,
                "grade": scoring_result.grade,
                "component_scores": {
                    "body_length":     scoring_result.component_scores.body_length,
                    "height":          scoring_result.component_scores.height,
                    "chest_girth":     scoring_result.component_scores.chest_girth,
                    "rump_angle":      scoring_result.component_scores.rump_angle,
                    "rump_width":      scoring_result.component_scores.rump_width,
                    "body_depth":      scoring_result.component_scores.body_depth,
                    "dairy_character": scoring_result.component_scores.dairy_character,
                    "feet_legs":       scoring_result.component_scores.feet_legs,
                    "udder":           scoring_result.component_scores.udder,
                },
            },
            "processing_time_ms": elapsed_ms,
        }

    # ── Detection ─────────────────────────────────────────────────────────────

    def _detect_animal(self, image: np.ndarray) -> Tuple[Optional[BoundingBox], Optional[float]]:
        """Run YOLOv8 to detect cattle in image."""
        if self.yolo_model is None:
            h, w = image.shape[:2]
            return BoundingBox(0, 0, w, h), 1.0

        try:
            results = self.yolo_model(image, verbose=False, conf=0.25)
            best_box = None
            best_conf = 0.0
            best_area = 0

            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    # COCO classes: cow=19, horse=17, sheep=18 — accept any large animal
                    if cls_id in (19, 17, 18, 20, 21) or conf > 0.5:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        area = (x2 - x1) * (y2 - y1)
                        if area > best_area:
                            best_area = area
                            best_conf = conf
                            best_box = BoundingBox(x1, y1, x2, y2, conf)

            if best_box is None:
                h, w = image.shape[:2]
                return BoundingBox(0, 0, w, h), 0.5

            return best_box, best_conf

        except Exception as e:
            logger.warning("YOLO detection error: %s", e)
            h, w = image.shape[:2]
            return BoundingBox(0, 0, w, h), None

    # ── Classification ────────────────────────────────────────────────────────

    def _classify(self, image: np.ndarray, bbox: Optional[BoundingBox]) -> Tuple[str, float]:
        """Classify cow vs buffalo using ResNet50 classifier."""
        # Crop to detection region
        if bbox:
            crop = image[bbox.y1:bbox.y2, bbox.x1:bbox.x2]
        else:
            crop = image

        if crop.size == 0:
            crop = image

        pil_img = PILImage.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

        if self.classifier is not None:
            return self._nn_classify(pil_img)
        else:
            return self._heuristic_classify(image)

    def _nn_classify(self, pil_img: PILImage.Image) -> Tuple[str, float]:
        """Neural network classification."""
        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.classifier(tensor)
            probs = torch.softmax(logits, dim=1).squeeze()
        class_idx = int(probs.argmax())
        confidence = float(probs[class_idx])
        return BovineClassifier.CLASS_NAMES[class_idx], confidence

    def _heuristic_classify(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Colour-based heuristic fallback.
        Buffalo: darker coat (mean value in HSV < 60)
        Cow: lighter or mixed coat
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mean_value = float(hsv[:, :, 2].mean())
        mean_saturation = float(hsv[:, :, 1].mean())

        if mean_value < 85 and mean_saturation < 50:
            return "buffalo", 0.65
        else:
            return "cow", 0.65
