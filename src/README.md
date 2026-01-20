### Source Modules Overview

This folder contains Python scripts for data extraction, image enrichment, and preprocessing.

####  Modules

- `scraper.py` — Extracts messages and media from public Telegram channels; stores raw JSON and downloads images by channel and message ID.

- `yolo_detect.py` — Runs YOLOv8 object detection on downloaded images, classifies images (promotional, product_display, lifestyle, other), and saves results as a CSV for warehouse ingestion.