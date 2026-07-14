#!/usr/bin/env python3
"""
ATC System — End-to-End Test Script
Tests all API endpoints against a running instance.

Usage:
  python test_e2e.py                          # default: http://localhost:8000
  python test_e2e.py --base http://myhost:8000
  python test_e2e.py --image /path/to/cow.jpg
"""

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw
import numpy as np

BASE_URL = "http://localhost:8000"
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"


def log(status: str, test: str, detail: str = ""):
    print(f"  {status}  {test}" + (f" — {detail}" if detail else ""))


def make_synthetic_cow_image(path: str):
    """Create a synthetic cow-like image for testing."""
    img = Image.new("RGB", (500, 350), color=(200, 190, 170))
    draw = ImageDraw.Draw(img)
    # Body
    draw.ellipse([60, 100, 420, 250], fill=(180, 160, 130))
    # Head
    draw.ellipse([360, 70, 470, 180], fill=(175, 155, 125))
    # Legs
    for x in [100, 170, 280, 350]:
        draw.rectangle([x, 245, x+35, 330], fill=(160, 140, 110))
    # Dark spots
    draw.ellipse([150, 115, 210, 155], fill=(80, 55, 35))
    draw.ellipse([250, 130, 300, 165], fill=(80, 55, 35))
    img.save(path, "JPEG", quality=90)


def test_health(base: str) -> bool:
    try:
        r = requests.get(f"{base}/api/health", timeout=10)
        r.raise_for_status()
        data = r.json()
        log(PASS, "GET /api/health", f"status={data.get('status')} db={data.get('database')} ml={data.get('ml_engine')}")
        return True
    except Exception as e:
        log(FAIL, "GET /api/health", str(e))
        return False


def test_upload(base: str, image_path: str) -> dict:
    try:
        with open(image_path, "rb") as f:
            r = requests.post(
                f"{base}/api/v1/upload",
                files={"file": ("test_cow.jpg", f, "image/jpeg")},
                data={"tag_number": "E2E-TEST-001", "animal_name": "TestCow", "breed": "Gir"},
                timeout=30
            )
        r.raise_for_status()
        data = r.json()
        log(PASS, "POST /api/v1/upload", f"image_id={data['image_id'][:8]}… animal_id={data['animal_id'][:8]}…")
        return data
    except Exception as e:
        log(FAIL, "POST /api/v1/upload", str(e))
        return {}


def test_classify(base: str, image_id: str, animal_id: str = None) -> dict:
    try:
        payload = {"image_id": image_id}
        if animal_id:
            payload["animal_id"] = animal_id
        r = requests.post(
            f"{base}/api/v1/classify",
            json=payload,
            timeout=120
        )
        r.raise_for_status()
        data = r.json()
        clf_class = data.get("predicted_class", "?")
        conf = data.get("confidence", 0)
        score = data.get("score", {})
        final = score.get("final_score", "?")
        grade = score.get("grade", "?")
        ms = data.get("processing_time_ms", 0)
        log(PASS, "POST /api/v1/classify",
            f"class={clf_class} conf={conf:.2f} score={final} grade={grade} time={ms:.0f}ms")
        return data
    except Exception as e:
        log(FAIL, "POST /api/v1/classify", str(e))
        return {}


def test_records(base: str) -> bool:
    try:
        r = requests.get(f"{base}/api/v1/records", params={"page": 1, "page_size": 5}, timeout=15)
        r.raise_for_status()
        data = r.json()
        total = data.get("total", 0)
        items = len(data.get("items", []))
        log(PASS, "GET /api/v1/records", f"total={total} returned={items}")
        return True
    except Exception as e:
        log(FAIL, "GET /api/v1/records", str(e))
        return False


def test_records_filter(base: str) -> bool:
    try:
        for cls in ["cow", "buffalo"]:
            r = requests.get(f"{base}/api/v1/records", params={"animal_class": cls}, timeout=10)
            r.raise_for_status()
        log(PASS, "GET /api/v1/records (filtered)", "cow + buffalo filters work")
        return True
    except Exception as e:
        log(FAIL, "GET /api/v1/records (filtered)", str(e))
        return False


def test_record_detail(base: str, clf_id: str) -> bool:
    try:
        r = requests.get(f"{base}/api/v1/records/{clf_id}", timeout=10)
        r.raise_for_status()
        data = r.json()
        has_score = "score" in data and data["score"] is not None
        log(PASS, f"GET /api/v1/records/{clf_id[:8]}…", f"has_score={has_score}")
        return True
    except Exception as e:
        log(FAIL, "GET /api/v1/records/{id}", str(e))
        return False


def test_reports(base: str) -> bool:
    try:
        r = requests.get(f"{base}/api/v1/reports", timeout=15)
        r.raise_for_status()
        data = r.json()
        total = data.get("total_classifications", 0)
        avg_score = data.get("avg_score", 0)
        log(PASS, "GET /api/v1/reports",
            f"total={total} avg_score={avg_score:.1f} trends={len(data.get('score_trends',[]))}")
        return True
    except Exception as e:
        log(FAIL, "GET /api/v1/reports", str(e))
        return False


def test_scoring_values(clf_data: dict) -> bool:
    """Validate ATC score values are within expected ranges."""
    score = clf_data.get("score")
    if not score:
        log(WARN, "Score validation", "No score data returned")
        return False
    try:
        final = score["final_score"]
        grade = score["grade"]
        comp  = score["component_scores"]
        assert 0 <= final <= 100, f"final_score={final} out of range"
        assert grade in ("Excellent", "Good Plus", "Good", "Average"), f"Invalid grade: {grade}"
        for key, val in comp.items():
            assert 0 <= val <= 100, f"{key}={val} out of range"
        # Validate grade matches score
        if   final >= 85: assert grade == "Excellent"
        elif final >= 70: assert grade == "Good Plus"
        elif final >= 50: assert grade == "Good"
        else:             assert grade == "Average"
        log(PASS, "Score validation", f"final={final:.2f} grade={grade} all components in [0,100]")
        return True
    except AssertionError as e:
        log(FAIL, "Score validation", str(e))
        return False


def test_measurements(clf_data: dict) -> bool:
    """Validate morphometric measurements are physiologically plausible."""
    m = clf_data.get("measurements")
    if not m:
        log(WARN, "Measurements validation", "No measurements returned")
        return False
    try:
        checks = [
            ("body_length_cm", 80, 250),
            ("height_cm",      70, 200),
            ("chest_girth_cm", 100, 280),
            ("body_depth_cm",  30, 120),
            ("rump_width_cm",  15, 80),
        ]
        for key, lo, hi in checks:
            val = m.get(key)
            if val is not None:
                assert lo <= val <= hi, f"{key}={val:.1f} outside [{lo},{hi}]"
        log(PASS, "Measurements validation",
            f"length={m.get('body_length_cm',0):.1f}cm height={m.get('height_cm',0):.1f}cm girth={m.get('chest_girth_cm',0):.1f}cm")
        return True
    except AssertionError as e:
        log(FAIL, "Measurements validation", str(e))
        return False


def run_all(base: str, image_path: str = None):
    print("\n" + "="*65)
    print("  ATC System — End-to-End Test Suite")
    print("="*65)
    print(f"  Target: {base}\n")

    results = []

    # Health
    results.append(test_health(base))

    # Create test image if not provided
    if not image_path or not Path(image_path).exists():
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        make_synthetic_cow_image(tmp.name)
        image_path = tmp.name
        print(f"  ℹ️  Using synthetic test image: {image_path}\n")

    # Upload
    upload_data = test_upload(base, image_path)
    results.append(bool(upload_data))
    image_id = upload_data.get("image_id")
    animal_id = upload_data.get("animal_id")

    if image_id:
        # Classify
        clf_data = test_classify(base, image_id, animal_id)
        results.append(bool(clf_data))

        if clf_data:
            clf_id = clf_data.get("id")
            results.append(test_scoring_values(clf_data))
            results.append(test_measurements(clf_data))
            if clf_id:
                results.append(test_record_detail(base, clf_id))

    # Records
    results.append(test_records(base))
    results.append(test_records_filter(base))

    # Reports
    results.append(test_reports(base))

    # Summary
    passed = sum(results)
    total  = len(results)
    print("\n" + "─"*65)
    print(f"  Results: {passed}/{total} tests passed")
    if passed == total:
        print("  🎉 All tests passed!")
    else:
        print(f"  ⚠️  {total - passed} test(s) failed")
    print("="*65 + "\n")
    return passed == total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATC System E2E Tests")
    parser.add_argument("--base",  default="http://localhost:8000")
    parser.add_argument("--image", default=None, help="Path to test image (optional)")
    args = parser.parse_args()
    success = run_all(args.base, args.image)
    sys.exit(0 if success else 1)
