from torchvision import datasets, transforms, models
import torch, torch.nn as nn

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

# Load validation data
val = datasets.ImageFolder("../dataset/val", transform)
val_loader = torch.utils.data.DataLoader(val, batch_size=16)

# Load model
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load("../models/model.pth", map_location="cpu"))
model.eval()

# Accuracy
correct = 0
total = 0

with torch.no_grad():
    for x, y in val_loader:
        outputs = model(x)
        _, predicted = torch.max(outputs, 1)

        total += y.size(0)
        correct += (predicted == y).sum().item()

print(f"\n✅ Accuracy: {100 * correct / total:.2f}%")