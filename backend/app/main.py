from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import cv2, numpy as np

from app.services.pipeline import full_pipeline
from app.data.storage import save_record

#  FIRST create app
app = FastAPI()

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

#  THEN add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/classify")
async def classify(file: UploadFile):
    data = await file.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image"}

    result = full_pipeline(img)

    #  SAVE RESULT
    save_record(result)

    return result

from app.data.storage import get_dashboard

@app.get("/dashboard")
def dashboard():
    return get_dashboard()

from app.data.storage import get_records

@app.get("/records")
def records_api():
    return get_records()