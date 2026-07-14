import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import json

from train import CNN  # import model

# LOAD MODEL
model = CNN()
model.load_state_dict(torch.load("../models/model.pth", map_location="cpu"))
model.eval()

# LOAD CLASSES
with open("../models/classes.json") as f:
    classes = json.load(f)

transform = transforms.Compose([
    transforms.Resize((128,128)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

def predict_image(image_path):

    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)

        probs = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)

    confidence = confidence.item()
    predicted_class = classes[predicted.item()]

    #  MAIN FIX (REJECTION LOGIC)
    if confidence < 0.75:
        return {
            "error": True,
            "message": "Image mismatch. Upload cow or buffalo"
        }

    return {
        "class": predicted_class,
        "confidence": confidence
    }