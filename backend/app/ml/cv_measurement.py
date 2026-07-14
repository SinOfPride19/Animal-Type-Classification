import cv2
import numpy as np

def extract_measurements(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Blur + Edge detect
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # 2. Find contour (largest = animal)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv2.contourArea)

    # 3. Bounding box
    x,y,w,h = cv2.boundingRect(c)

    # 4. Approx measurements (pixel-based)
    body_length = w
    height = h

    # chest width (middle horizontal slice)
    mid_y = y + h//2
    row = edges[mid_y]
    xs = np.where(row > 0)[0]
    chest_width = xs[-1] - xs[0] if len(xs) > 0 else 0

    # chest girth approx (ellipse)
    chest_girth = int(np.pi * ((w + h) / 2) / 2)

    return {
        "body_length": body_length,
        "height": height,
        "chest_girth": chest_girth,
        "chest_width": chest_width
    }