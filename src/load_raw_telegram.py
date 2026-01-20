import os
import json
from pathlib import Path
from datetime import datetime, timezone
import psycopg2
from dotenv import load_dotenv

# Load environment variables

load_dotenv()

DATA_DIR = Path("data/raw/telegram_messages")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# SQL Template

INSERT_SQL = """
INSERT INTO raw.telegram_messages (
    message_id,
    channel_name,
    channel_title,
    message_date,
    message_text,
    has_media,
    image_path,
    views,
    forwards,
    ingestion_date,
    scrape_run_ts
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (message_id) DO NOTHING;
"""

# Load a single JSON file into Postgres

def load_file(cursor, filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        records = json.load(f)

    for r in records:
        cursor.execute(
            INSERT_SQL,
            (
                r["message_id"],
                r["channel_name"],
                r.get("channel_title"),
                r["message_date"],
                r["message_text"],
                r["has_media"],
                r["image_path"],
                r["views"],
                r["forwards"],
                datetime.now(timezone.utc).date(),      # ingestion_date
                datetime.now(timezone.utc),              # scrape_run_ts
            )
        )


# Main loader

def main():
    # Connect to Postgres
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Iterate over all date folders
    for date_dir in DATA_DIR.iterdir():
        if not date_dir.is_dir():
            continue

        for json_file in date_dir.glob("*.json"):
            if json_file.name.startswith("_"):
                continue

            print(f"Loading {json_file} ...")
            load_file(cur, json_file)
            conn.commit()  # commit per file to reduce rollback risk

    cur.close()
    conn.close()
    print("All data loaded successfully!")


# Entry point

if __name__ == "__main__":
    main()
