### Source Modules Overview

This folder contains Python scripts for data extraction, image enrichment, and preprocessing.

####  Modules

- `scraper.py` — Extracts messages and media from public Telegram channels.

    - Stores raw JSON per channel and per date.
    - Downloads images organized by channel and message ID.

- `load_raw_telegram.py` — Loads raw Telegram JSON messages into the warehouse staging schema.

    - Prepares data for dbt transformations.

- `yolo_detect.py` — Runs YOLOv8 object detection on downloaded images.

    - Classifies images into categories: promotional, product_display, lifestyle, other.
    - Records detected objects and confidence scores.
    - Saves results to a CSV (yolo_detections.csv) for loading into the data warehouse.

- `load_yolo.py` — Loads YOLO detection CSV into the warehouse staging schema.

    - Inserts data into staging.stg_yolo_detections ready for dbt models.