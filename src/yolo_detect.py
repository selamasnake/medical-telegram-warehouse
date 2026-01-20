import os
import pandas as pd
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
image_parent_folder = 'data/raw/images'
output_csv = 'data/processed/yolo_detections.csv'

detection_data = []

product_labels = [
    'bottle',       # Syrups, vials, liquid meds
    'cup',          # Small jars/containers
    'suitcase',     # Medical kits
    'refrigerator', # Cold-stored meds
    'bed',          # Clinic/hospital beds (contextual)
    'tv',           # Patient monitors (contextual)
    'laptop',       # Diagnostic stations (contextual)
    'book'          # Tall boxes/packaging proxies
]
# Iterate through channel folders
for channel_folder in os.listdir(image_parent_folder):
    channel_path = os.path.join(image_parent_folder, channel_folder)
    if not os.path.isdir(channel_path):
        continue

    print(f"Processing images from channel: {channel_folder}")
    results = model.predict(source=channel_path, conf=0.25, imgsz=640)

    for result in results:
        img_name = os.path.basename(result.path)
        labels = [model.names[int(box.cls[0])] for box in result.boxes]
        confidences = [float(box.conf[0]) for box in result.boxes]

        has_person = 'person' in labels
        has_product = any(item in labels for item in product_labels)

        if has_person and has_product:
            category = 'promotional'
        elif has_product:
            category = 'product_display'
        elif has_person:
            category = 'lifestyle'
        else:
            category = 'other'

        detection_data.append({
            'image_name': img_name,
            'channel_name': channel_folder,
            'detected_objects': ", ".join(labels) if labels else '',
            'max_confidence': max(confidences) if confidences else 0,
            'image_category': category
        })

# Save to CSV for dbt
os.makedirs(os.path.dirname(output_csv), exist_ok=True)
pd.DataFrame(detection_data).to_csv(output_csv, index=False)
print(f"Detection CSV saved to {output_csv}")
