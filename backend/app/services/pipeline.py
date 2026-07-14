import cv2
import torch
import os
from ultralytics import YOLO
from torchvision import transforms
import torch.nn as nn
from pathlib import Path

# ---------------- YOLO ----------------
yolo = YOLO("yolov8n.pt")


# ---------------- MODEL PATH (FIXED) ----------------
BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "core_ml" / "models" / "model.pth"


# ---------------- CNN MODEL ----------------
class CNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(3,32,3,padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32,64,3,padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64,128,3,padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128*16*16,256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256,2)
        )

    def forward(self,x):
        return self.fc(self.conv(x))


# ---------------- LOAD MODEL ----------------
def load_classifier():
    model = CNN()

    try:
        print(f"🔍 Looking for model at: {MODEL_PATH}")

        if MODEL_PATH.exists():
            model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
            print("✅ CNN Model loaded successfully")
        else:
            print("⚠️ Model not found — using default weights (not trained)")

    except Exception as e:
        print(f"🔥 Error loading model: {e}")

    model.eval()
    return model


classifier = load_classifier()


# ---------------- TRANSFORM ----------------
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((128,128)),   # match training
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])


# ---------------- DETECTION ----------------
def detect(img):
    try:
        result = yolo(img)[0]

        if len(result.boxes) == 0:
            return img

        x1, y1, x2, y2 = map(int, result.boxes[0].xyxy[0])

        if x2 <= x1 or y2 <= y1:
            return img

        return img[y1:y2, x1:x2]

    except Exception as e:
        print("YOLO error:", e)
        return img


# ---------------- CLASSIFICATION ----------------
def classify(img):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        tensor = transform(img).unsqueeze(0)

        out = classifier(tensor)
        probs = torch.softmax(out, dim=1)

        confidence, pred = torch.max(probs, 1)

        return pred.item()

    except Exception as e:
        print("Classification error:", e)
        return 0


# ---------------- MEASUREMENTS ----------------
def measure(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

        cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) == 0:
            h, w = img.shape[:2]
            return {
                "body_length": w,
                "height": h,
                "chest_width": w * 0.4,
                "chest_girth": w * 1.5
            }

        c = max(cnts, key=cv2.contourArea)

        x, y, w, h = cv2.boundingRect(c)

        return {
            "body_length": w,
            "height": h,
            "chest_width": w * 0.4,
            "chest_girth": cv2.arcLength(c, True)
        }

    except Exception as e:
        print("Measurement error:", e)
        h, w = img.shape[:2]
        return {
            "body_length": w,
            "height": h,
            "chest_width": w * 0.4,
            "chest_girth": w * 1.5
        }


# ---------------- ATC SCORE ----------------
def score(m):
    score_val = (
        0.15*m["body_length"] +
        0.15*m["height"] +
        0.15*m["chest_girth"] +
        0.10*(m["height"]*0.1) +
        0.10*(m["body_length"]*0.2) +
        0.10*(m["height"]*0.5) +
        0.10*(m["chest_girth"]*0.05) +
        0.075*(m["height"]*0.08) +
        0.075*(m["chest_width"]*0.07)
    )

    val = min(100, score_val / 10)

    grade = (
        "Excellent" if val >= 85 else
        "Good Plus" if val >= 70 else
        "Good" if val >= 50 else
        "Average"
    )

    return val, grade


# ---------------- FULL PIPELINE ----------------
def full_pipeline(img):
    try:
        crop = detect(img)
        cls = classify(crop)
        m = measure(crop)
        val, grade = score(m)

        classes = ['buffalo', 'cow']

        return {
            "class": classes[cls],
            "score": round(val, 2),
            "grade": grade,
            "measurements": m
        }

    except Exception as e:
        return {"error": str(e)}