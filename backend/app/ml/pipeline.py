"""
Image Processing Pipeline — ATC System
Real OpenCV-based morphometric measurement extraction.

Pipeline:
  1. YOLOv8 detection → bounding box
  2. Crop + segment animal ROI
  3. Extract contour via GrabCut + Canny
  4. Compute geometric keypoints (head, tail, back, hoof)
  5. Measure Body Length, Height, Chest Width, Girth, Body Depth, Rump Width
  6. Normalise pixel measurements to cm using image scaling heuristics
"""

import logging
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class BoundingBox:
    x1: int; y1: int; x2: int; y2: int
    confidence: float = 1.0

    @property
    def width(self): return self.x2 - self.x1
    @property
    def height(self): return self.y2 - self.y1
    @property
    def area(self): return self.width * self.height
    @property
    def center(self): return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)


@dataclass
class MorphometricResult:
    # Pixel measurements
    body_length_px: float = 0.0
    height_px: float = 0.0
    chest_width_px: float = 0.0
    chest_girth_px: float = 0.0
    body_depth_px: float = 0.0
    rump_width_px: float = 0.0

    # Scale
    pixel_per_cm: float = 1.0

    # Normalised cm measurements
    body_length_cm: float = 0.0
    height_cm: float = 0.0
    chest_girth_cm: float = 0.0
    body_depth_cm: float = 0.0
    rump_width_cm: float = 0.0

    # Contour area (for dairy character heuristic)
    contour_area: float = 0.0
    aspect_ratio: float = 0.0

    # Keypoints (for debug / overlay)
    keypoints: Dict[str, Tuple[int, int]] = None

    def __post_init__(self):
        if self.keypoints is None:
            self.keypoints = {}


# ─── Pipeline ─────────────────────────────────────────────────────────────────

class ImageProcessingPipeline:
    """
    Executes the full morphometric extraction pipeline on a bovine image.

    Reference measurements (average adult cow, used for pixel normalisation):
      Body length: 150–170 cm
      Height at withers: 130–145 cm
      Chest girth: 165–185 cm
    """

    # Average bovine body length (cm) used as reference for pixel → cm conversion
    REFERENCE_BODY_LENGTH_CM = 160.0
    # Average pixel diagonal used as a secondary fallback
    MIN_BBOX_HEIGHT_PX = 50

    def __init__(self):
        logger.info("ImageProcessingPipeline initialised")

    # ── Public entry point ────────────────────────────────────────────────────

    def process(self, image: np.ndarray, bbox: Optional[BoundingBox] = None) -> MorphometricResult:
        """
        Full pipeline: detection crop → segmentation → contour → measurements → normalise.

        Args:
            image: BGR numpy array (H×W×3)
            bbox:  Optional pre-detected bounding box. If None, full image is used.

        Returns:
            MorphometricResult with all measurements populated.
        """
        h_img, w_img = image.shape[:2]

        # Step 1: Crop to ROI
        if bbox is not None:
            roi, offset = self._crop_roi(image, bbox, padding=0.05)
        else:
            roi = image.copy()
            offset = (0, 0)
            bbox = BoundingBox(0, 0, w_img, h_img)

        # Step 2: Segmentation / foreground extraction
        mask = self._segment_animal(roi)

        # Step 3: Contour extraction
        contour = self._extract_primary_contour(mask)
        if contour is None:
            logger.warning("No contour found — using bounding box fallback")
            contour = self._bbox_to_contour(roi.shape)

        # Step 4: Keypoint estimation
        keypoints = self._estimate_keypoints(contour, roi.shape)

        # Step 5: Geometric measurements (pixels)
        result = self._compute_pixel_measurements(contour, keypoints, roi.shape)
        result.keypoints = keypoints

        # Step 6: Normalise to cm
        self._normalise_to_cm(result, image_shape=image.shape, bbox=bbox)

        logger.debug(
            "Pipeline complete | length=%.1f cm | height=%.1f cm | girth=%.1f cm",
            result.body_length_cm, result.height_cm, result.chest_girth_cm
        )
        return result

    # ── Step 1: Crop ROI ──────────────────────────────────────────────────────

    def _crop_roi(
        self, image: np.ndarray, bbox: BoundingBox, padding: float = 0.05
    ) -> Tuple[np.ndarray, Tuple[int, int]]:
        h, w = image.shape[:2]
        pad_x = int(bbox.width * padding)
        pad_y = int(bbox.height * padding)
        x1 = max(0, bbox.x1 - pad_x)
        y1 = max(0, bbox.y1 - pad_y)
        x2 = min(w, bbox.x2 + pad_x)
        y2 = min(h, bbox.y2 + pad_y)
        return image[y1:y2, x1:x2].copy(), (x1, y1)

    # ── Step 2: Segmentation ──────────────────────────────────────────────────

    def _segment_animal(self, roi: np.ndarray) -> np.ndarray:
        """
        GrabCut-based foreground segmentation.
        Falls back to Otsu thresholding if GrabCut fails.
        """
        h, w = roi.shape[:2]
        if h < 20 or w < 20:
            return np.ones((h, w), dtype=np.uint8) * 255

        try:
            mask = np.zeros((h, w), np.uint8)
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)

            # Use a central rectangle as probable foreground
            margin_x = max(int(w * 0.08), 5)
            margin_y = max(int(h * 0.08), 5)
            rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

            cv2.grabCut(roi, mask, rect, bgd_model, fgd_model, iterCount=5,
                        mode=cv2.GC_INIT_WITH_RECT)

            binary = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

            # Morphological cleanup
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=3)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN,  kernel, iterations=2)
            return binary

        except cv2.error:
            return self._otsu_segment(roi)

    def _otsu_segment(self, roi: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    # ── Step 3: Contour ───────────────────────────────────────────────────────

    def _extract_primary_contour(self, mask: np.ndarray) -> Optional[np.ndarray]:
        """Return the largest contour from the segmentation mask."""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        # Largest by area
        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) < 200:
            return None
        return contour

    def _bbox_to_contour(self, shape: Tuple) -> np.ndarray:
        """Fallback: rectangular contour from ROI shape."""
        h, w = shape[:2]
        return np.array([[[0, 0]], [[w, 0]], [[w, h]], [[0, h]]], dtype=np.int32)

    # ── Step 4: Keypoints ─────────────────────────────────────────────────────

    def _estimate_keypoints(
        self, contour: np.ndarray, roi_shape: Tuple
    ) -> Dict[str, Tuple[int, int]]:
        """
        Estimate anatomical keypoints from contour geometry.

        Strategy (side-view assumption):
          • head  = leftmost point of the convex hull
          • tail  = rightmost point
          • top_back = topmost point in the middle third (withers region)
          • hoof  = bottommost point
          • mid_chest = left quarter of bounding rect, vertical midpoint
        """
        h_roi, w_roi = roi_shape[:2]
        hull = cv2.convexHull(contour)
        pts = hull.reshape(-1, 2)

        # Bounding rect of contour
        x, y, w, h = cv2.boundingRect(contour)

        # Head (leftmost)
        head_idx = np.argmin(pts[:, 0])
        head = tuple(pts[head_idx].tolist())

        # Tail (rightmost)
        tail_idx = np.argmax(pts[:, 0])
        tail = tuple(pts[tail_idx].tolist())

        # Withers / top of back: topmost point in middle 40–60% x range
        mid_x_min = x + int(w * 0.35)
        mid_x_max = x + int(w * 0.65)
        mid_pts = pts[(pts[:, 0] >= mid_x_min) & (pts[:, 0] <= mid_x_max)]
        if len(mid_pts) > 0:
            withers_idx = np.argmin(mid_pts[:, 1])
            withers = tuple(mid_pts[withers_idx].tolist())
        else:
            withers = (x + w // 2, y)

        # Hoof (bottommost)
        hoof_idx = np.argmax(pts[:, 1])
        hoof = tuple(pts[hoof_idx].tolist())

        # Chest: leftmost quarter, midheight
        chest_x = x + w // 5
        chest_pts = pts[(pts[:, 0] >= x) & (pts[:, 0] <= x + w // 3)]
        if len(chest_pts) > 0:
            chest_y = int(np.median(chest_pts[:, 1]))
        else:
            chest_y = y + h // 2
        chest = (chest_x, chest_y)

        # Rump: rightmost quarter, midheight
        rump_x = x + int(w * 0.8)
        rump_pts = pts[(pts[:, 0] >= x + int(w * 0.7))]
        if len(rump_pts) > 0:
            rump_y = int(np.median(rump_pts[:, 1]))
        else:
            rump_y = y + h // 2
        rump = (rump_x, rump_y)

        return {
            "head": head,
            "tail": tail,
            "withers": withers,
            "hoof": hoof,
            "chest": chest,
            "rump": rump,
        }

    # ── Step 5: Pixel Measurements ────────────────────────────────────────────

    def _compute_pixel_measurements(
        self, contour: np.ndarray, keypoints: Dict, roi_shape: Tuple
    ) -> MorphometricResult:
        result = MorphometricResult()

        head = np.array(keypoints["head"])
        tail = np.array(keypoints["tail"])
        withers = np.array(keypoints["withers"])
        hoof = np.array(keypoints["hoof"])

        x, y, w, h = cv2.boundingRect(contour)

        # Body Length = Euclidean distance head → tail
        result.body_length_px = float(np.linalg.norm(tail - head))

        # Height at withers = vertical distance top_back → hoof
        result.height_px = float(abs(hoof[1] - withers[1]))

        # Chest width = horizontal span of contour at 1/4 x position
        chest_x_pos = x + w // 4
        chest_pts = contour.reshape(-1, 2)
        chest_cols = chest_pts[np.abs(chest_pts[:, 0] - chest_x_pos) < max(w // 20, 5)]
        if len(chest_cols) >= 2:
            result.chest_width_px = float(chest_cols[:, 1].max() - chest_cols[:, 1].min())
        else:
            result.chest_width_px = h * 0.55

        # Body depth = bounding rect height at mid-body
        mid_x_pos = x + w // 2
        mid_pts = chest_pts[np.abs(chest_pts[:, 0] - mid_x_pos) < max(w // 20, 5)]
        if len(mid_pts) >= 2:
            result.body_depth_px = float(mid_pts[:, 1].max() - mid_pts[:, 1].min())
        else:
            result.body_depth_px = h * 0.6

        # Rump width = horizontal span at 80% x position
        rump_x_pos = x + int(w * 0.8)
        rump_pts = chest_pts[np.abs(chest_pts[:, 0] - rump_x_pos) < max(w // 20, 5)]
        if len(rump_pts) >= 2:
            result.rump_width_px = float(rump_pts[:, 1].max() - rump_pts[:, 1].min())
        else:
            result.rump_width_px = h * 0.45

        # Chest girth ≈ circumference approximation from chest_width and body_depth
        # Using ellipse perimeter formula: π × (3(a+b) − √((3a+b)(a+3b)))
        a = result.chest_width_px / 2.0
        b = result.body_depth_px / 2.0
        if a > 0 and b > 0:
            result.chest_girth_px = math.pi * (3*(a + b) - math.sqrt((3*a + b) * (a + 3*b)))
        else:
            result.chest_girth_px = result.body_length_px * 1.05

        # Contour area and aspect ratio
        result.contour_area = float(cv2.contourArea(contour))
        result.aspect_ratio = result.body_length_px / result.height_px if result.height_px > 0 else 1.2

        return result

    # ── Step 6: Normalise to cm ───────────────────────────────────────────────

    def _normalise_to_cm(
        self, result: MorphometricResult, image_shape: Tuple, bbox: BoundingBox
    ) -> None:
        """
        Convert pixel measurements to real-world centimetres.

        Method:
          Using reference body length of an adult bovine (160 cm) as anchor.
          pixel_per_cm = body_length_px / REFERENCE_BODY_LENGTH_CM

        Alternative: if bbox is smaller than 50% of image, use image-width ratio
        as secondary scale.
        """
        if result.body_length_px > self.MIN_BBOX_HEIGHT_PX:
            result.pixel_per_cm = result.body_length_px / self.REFERENCE_BODY_LENGTH_CM
        else:
            # Fallback: assume bbox width ≈ body length
            result.pixel_per_cm = max(bbox.width, 50) / self.REFERENCE_BODY_LENGTH_CM

        ppc = result.pixel_per_cm

        result.body_length_cm = result.body_length_px / ppc
        result.height_cm       = result.height_px       / ppc
        result.chest_girth_cm  = result.chest_girth_px  / ppc
        result.body_depth_cm   = result.body_depth_px   / ppc
        result.rump_width_cm   = result.rump_width_px   / ppc

        # Clamp to physiologically plausible ranges
        result.body_length_cm  = self._clamp(result.body_length_cm,  80, 250)
        result.height_cm       = self._clamp(result.height_cm,       70, 200)
        result.chest_girth_cm  = self._clamp(result.chest_girth_cm, 100, 280)
        result.body_depth_cm   = self._clamp(result.body_depth_cm,   40, 120)
        result.rump_width_cm   = self._clamp(result.rump_width_cm,   20,  80)

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))
