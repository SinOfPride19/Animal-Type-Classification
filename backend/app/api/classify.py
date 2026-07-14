import sys
import os
sys.path.append(os.path.abspath(".."))
from fastapi import APIRouter, UploadFile, File
import shutil
import uuid

from core_ml.scripts.predict import predict_image
from app.ml.cv_measurement import extract_measurements
from app.ml.scaling import normalize
from app.ml.scoring import compute_scores

router = APIRouter()

@router.post("/classify")
async def classify(file: UploadFile = File(...)):
    filename = f"uploads/{uuid.uuid4()}.jpg"

    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    #  STEP 1: MODEL PREDICTION
    result = predict_image(filename)

    # STEP 2: REJECT WRONG IMAGE
    if result.get("error"):
        return result

    # STEP 3: CONTINUE NORMAL FLOW
    raw = extract_measurements(filename)
    scaled = normalize(raw)
    scores = compute_scores(scaled)

    return {
        "class": result["class"],  #  dynamic now
        "confidence": result["confidence"],
        "measurements": scaled,
        "score": scores["final_score"],
        "grade": scores["grade"],
        "components": scores["components"]
    }