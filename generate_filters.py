import os
import cv2
import numpy as np

output_dir = "static/filters"
os.makedirs(output_dir, exist_ok=True)

filters = {
    "sunglasses": (0, 0, 0),
    "hat": (255, 0, 0),
    "mask": (0, 255, 0),
    "crown": (255, 255, 0),
    "spiderman": (255, 0, 255),
    "full_face_mask": (128, 128, 128)
}

for name, color in filters.items():
    img = np.full((150, 300, 3), color, np.uint8)
    cv2.putText(img, name, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.imwrite(os.path.join(output_dir, f"{name}.png"), img)

print("Sample filters generated successfully.")