"""
ATC System — Backend Test Suite
Tests for pipeline, scoring, and API endpoints.
Run: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch


# ─── Pipeline Tests ───────────────────────────────────────────────────────────

class TestImageProcessingPipeline:
    def setup_method(self):
        from app.ml.pipeline import ImageProcessingPipeline
        self.pipeline = ImageProcessingPipeline()

    def _make_test_image(self, w=400, h=300):
        """Create a synthetic cow-like image for testing."""
        img = np.ones((h, w, 3), dtype=np.uint8) * 200
        # Draw body ellipse
        cv2.ellipse(img, (w//2, h//2), (w//3, h//4), 0, 0, 360, (120, 100, 80), -1)
        return img

    def test_pipeline_returns_result(self):
        img = self._make_test_image()
        result = self.pipeline.process(img, bbox=None)
        assert result is not None
        assert result.body_length_px > 0
        assert result.height_px > 0

    def test_body_length_plausible(self):
        img = self._make_test_image(600, 400)
        result = self.pipeline.process(img)
        assert result.body_length_cm >= 80
        assert result.body_length_cm <= 250

    def test_height_plausible(self):
        img = self._make_test_image(600, 400)
        result = self.pipeline.process(img)
        assert result.height_cm >= 70
        assert result.height_cm <= 200

    def test_chest_girth_plausible(self):
        img = self._make_test_image(600, 400)
        result = self.pipeline.process(img)
        assert result.chest_girth_cm >= 100
        assert result.chest_girth_cm <= 280

    def test_with_bounding_box(self):
        from app.ml.pipeline import BoundingBox
        img = self._make_test_image(600, 400)
        bbox = BoundingBox(50, 50, 550, 350, 0.95)
        result = self.pipeline.process(img, bbox=bbox)
        assert result.body_length_px > 0

    def test_small_image(self):
        img = self._make_test_image(100, 80)
        result = self.pipeline.process(img)
        assert result is not None

    def test_keypoints_populated(self):
        img = self._make_test_image(400, 300)
        result = self.pipeline.process(img)
        assert "head" in result.keypoints
        assert "tail" in result.keypoints
        assert "withers" in result.keypoints
        assert "hoof" in result.keypoints


# ─── Scoring Tests ────────────────────────────────────────────────────────────

class TestATCScoringEngine:
    def setup_method(self):
        from app.ml.scoring import ATCScoringEngine
        from app.ml.pipeline import MorphometricResult
        self.engine = ATCScoringEngine()
        self.MorphometricResult = MorphometricResult

    def _ideal_measurements(self):
        m = self.MorphometricResult()
        m.body_length_cm = 160.0
        m.height_cm       = 135.0
        m.chest_girth_cm  = 175.0
        m.body_depth_cm   = 68.0
        m.rump_width_cm   = 47.0
        m.aspect_ratio    = 1.19
        return m

    def _poor_measurements(self):
        m = self.MorphometricResult()
        m.body_length_cm = 90.0
        m.height_cm       = 78.0
        m.chest_girth_cm  = 105.0
        m.body_depth_cm   = 38.0
        m.rump_width_cm   = 18.0
        m.aspect_ratio    = 1.15
        return m

    def test_ideal_score_high(self):
        result = self.engine.compute(self._ideal_measurements(), "cow", 0.95)
        assert result.final_score >= 70.0, f"Expected ≥70, got {result.final_score}"

    def test_poor_score_low(self):
        result = self.engine.compute(self._poor_measurements(), "cow", 0.6)
        assert result.final_score < 75.0

    def test_grade_excellent(self):
        m = self._ideal_measurements()
        result = self.engine.compute(m, "cow", 0.98)
        # Ideal measurements should produce Good or better
        assert result.grade in ("Excellent", "Good Plus", "Good")

    def test_grade_thresholds(self):
        assert self.engine._grade(90) == "Excellent"
        assert self.engine._grade(75) == "Good Plus"
        assert self.engine._grade(60) == "Good"
        assert self.engine._grade(40) == "Average"

    def test_range_score(self):
        # In ideal range → 100
        assert self.engine._range_score(160, 140, 175, 80, 250) == 100.0
        # At absolute min → 0
        assert self.engine._range_score(80, 140, 175, 80, 250) == 0.0
        # Halfway below ideal → ~50
        score = self.engine._range_score(110, 140, 175, 80, 250)
        assert 40 < score < 60

    def test_gaussian_score(self):
        assert self.engine._gaussian_score(1.2, 1.2, 0.15) == pytest.approx(100.0, abs=0.1)
        assert self.engine._gaussian_score(1.5, 1.2, 0.15) < 50.0

    def test_score_bounded(self):
        for _ in range(20):
            m = self.MorphometricResult()
            m.body_length_cm = np.random.uniform(80, 250)
            m.height_cm       = np.random.uniform(70, 200)
            m.chest_girth_cm  = np.random.uniform(100, 280)
            m.body_depth_cm   = np.random.uniform(30, 120)
            m.rump_width_cm   = np.random.uniform(15, 80)
            result = self.engine.compute(m, "cow", 0.8)
            assert 0 <= result.final_score <= 100

    def test_weights_sum_to_one(self):
        total = sum(self.engine.WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9, f"Weights sum to {total}, expected 1.0"

    def test_buffalo_vs_cow_dairy(self):
        m = self._ideal_measurements()
        cow_result = self.engine.compute(m, "cow", 0.9)
        buf_result = self.engine.compute(m, "buffalo", 0.9)
        # Both should score reasonably; dairy character differs
        assert cow_result.component_scores.dairy_character != buf_result.component_scores.dairy_character


# ─── Schema Tests ─────────────────────────────────────────────────────────────

class TestSchemas:
    def test_component_scores_bounded(self):
        from app.schemas.schemas import ComponentScores
        cs = ComponentScores(
            body_length=85, height=90, chest_girth=75, rump_angle=80,
            rump_width=70, body_depth=65, dairy_character=88, feet_legs=72, udder=68
        )
        assert all(0 <= v <= 100 for v in [
            cs.body_length, cs.height, cs.chest_girth, cs.rump_angle,
            cs.rump_width, cs.body_depth, cs.dairy_character, cs.feet_legs, cs.udder
        ])

    def test_classify_request(self):
        from app.schemas.schemas import ClassifyRequest
        req = ClassifyRequest(image_id="test-uuid-123")
        assert req.image_id == "test-uuid-123"
        assert req.animal_id is None

    def test_animal_create(self):
        from app.schemas.schemas import AnimalCreate
        animal = AnimalCreate(tag_number="GJ-001", breed="Gir", age_years=4.5)
        assert animal.tag_number == "GJ-001"
        assert animal.age_years == 4.5


# ─── API Integration Tests (no DB) ────────────────────────────────────────────

class TestAPIHealth:
    def test_import_main(self):
        """Verify app imports without errors."""
        try:
            from app.main import app
            assert app is not None
        except Exception as e:
            pytest.fail(f"App import failed: {e}")

    def test_config_loaded(self):
        from app.core.config import settings
        assert settings.DB_NAME == "atc_db"
        assert settings.IMAGE_SIZE == 224
        total_weights = (
            settings.SCORE_WEIGHT_BODY_LENGTH + settings.SCORE_WEIGHT_HEIGHT +
            settings.SCORE_WEIGHT_CHEST_GIRTH + settings.SCORE_WEIGHT_RUMP_ANGLE +
            settings.SCORE_WEIGHT_RUMP_WIDTH  + settings.SCORE_WEIGHT_BODY_DEPTH +
            settings.SCORE_WEIGHT_DAIRY_CHARACTER + settings.SCORE_WEIGHT_FEET_LEGS +
            settings.SCORE_WEIGHT_UDDER
        )
        assert abs(total_weights - 1.0) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
