from torchvision import datasets, transforms
import torch
import torch.nn as nn
import torch.optim as optim

# ---------------- CONFIG ----------------
EPOCHS = 15

transform = transforms.Compose([
    transforms.Resize((128,128)),   # smaller for CNN
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.5, 0.5, 0.5],
        std=[0.5, 0.5, 0.5]
    )
])

train = datasets.ImageFolder("../dataset/train", transform)
val = datasets.ImageFolder("../dataset/val", transform)

train_loader = torch.utils.data.DataLoader(train, batch_size=32, shuffle=True)
val_loader = torch.utils.data.DataLoader(val, batch_size=32)

print("Classes:", train.classes)


# ---------------- CNN MODEL ----------------
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 16 * 16, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 2)
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.fc(x)
        return x


model = CNN()

# ---------------- TRAINING ----------------
optimizer = optim.Adam(model.parameters(), lr=0.0005)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch+1}/{EPOCHS}")
    model.train()

    for i, (x,y) in enumerate(train_loader):
        pred = model(x)
        loss = loss_fn(pred,y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if i % 20 == 0:
            print(f"Batch {i}, Loss: {loss.item():.4f}")


# ---------------- VALIDATION ----------------
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for x,y in val_loader:
        out = model(x)
        _, pred = torch.max(out,1)
        total += y.size(0)
        correct += (pred==y).sum().item()

print(f"\n Accuracy: {100*correct/total:.2f}%")

# ---------------- SAVE ----------------
torch.save(model.state_dict(), "../models/model.pth")

print(" Training complete!")

# ---------------- PREDICTION + VALIDATION (NEW FEATURE) ----------------
import torch.nn.functional as F
from PIL import Image

def predict_image(image_path):
    model.eval()

    transform_infer = transforms.Compose([
        transforms.Resize((128,128)),
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])

    img = Image.open(image_path).convert("RGB")
    img = transform_infer(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)

        probs = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)

    confidence_val = confidence.item()
    predicted_idx = predicted.item()

    classes = train.classes  # ['cow','buffalo']

    predicted_class = classes[predicted_idx]

    #  MAIN FEATURE (IMAGE VALIDATION)
    if confidence_val < 0.90:
        return {
            "error": True,
            "message": " Image mismatch. Upload cow or buffalo image"
        }

    return {
        "class": predicted_class,
        "confidence": confidence_val
    }