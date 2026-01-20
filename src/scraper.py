
import os
import sys
import json
import csv
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageMediaPhoto


# PROJECT PATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ENVIRONMENT
load_dotenv()

API_ID = os.getenv("Tg_API_ID")
API_HASH = os.getenv("Tg_API_HASH")

if not API_ID or not API_HASH:
    raise RuntimeError("Missing Tg_API_ID or Tg_API_HASH in .env")

API_ID = int(API_ID)


# CONSTANTS

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DEFAULT_MESSAGE_DELAY = 1.0
DEFAULT_CHANNEL_DELAY = 3.0


# LOGGING

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("telegram_scraper")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(
    os.path.join(LOG_DIR, f"scrape_{TODAY}.log"),
    encoding="utf-8"
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


# DATA LAKE HELPERS

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def json_output_path(base_path: str, channel: str) -> str:
    path = os.path.join(base_path, "raw", "telegram_messages", TODAY)
    ensure_dir(path)
    return os.path.join(path, f"{channel}.json")

def image_dir(base_path: str, channel: str) -> str:
    path = os.path.join(base_path, "raw", "images", channel)
    ensure_dir(path)
    return path

def csv_output_path(base_path: str) -> str:
    path = os.path.join(base_path, "raw", "csv", TODAY)
    ensure_dir(path)
    return os.path.join(path, "telegram_data.csv")

def write_manifest(base_path: str, stats: Dict[str, int]) -> None:
    manifest = {
        "date": TODAY,
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "channels": stats,
        "total_messages": sum(stats.values())
    }
    path = os.path.join(
        base_path,
        "raw",
        "telegram_messages",
        TODAY,
        "_manifest.json"
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


# SCRAPING LOGIC

async def scrape_channel(
    client: TelegramClient,
    channel: str,
    base_path: str,
    csv_writer: csv.writer,
    limit: int,
    message_delay: float
) -> int:
    """
    Scrape a single Telegram channel and save messages & images.
    Logs progress every 50 messages.
    """
    channel_name = channel.strip("@")
    image_path_base = image_dir(base_path, channel_name)
    messages: List[Dict] = []

    try:
        entity = await client.get_entity(channel)
        logger.info(f"Scraping {channel} (limit={limit})")

        idx = 0
        async for message in client.iter_messages(entity, limit=limit):
            idx += 1
            has_media = message.media is not None
            image_path: Optional[str] = None

            if has_media and isinstance(message.media, MessageMediaPhoto):
                image_path = os.path.join(image_path_base, f"{message.id}.jpg")
                try:
                    await client.download_media(message.media, image_path)
                except Exception as e:
                    logger.warning(f"Image download failed ({message.id}): {e}")
                    image_path = None

            record = {
                "message_id": message.id,
                "channel_name": channel_name,
                "channel_title": getattr(entity, "title", channel_name),
                "message_date": message.date.isoformat() if message.date else None,
                "message_text": message.message or "",
                "has_media": has_media,
                "image_path": image_path,
                "views": message.views,
                "forwards": message.forwards
            }

            messages.append(record)

            csv_writer.writerow([
                record["message_id"],
                record["channel_name"],
                record["channel_title"],
                record["message_date"],
                record["message_text"],
                record["has_media"],
                record["image_path"],
                record["views"],
                record["forwards"]
            ])

            # --- Progress logging every 50 messages ---
            if idx % 50 == 0 or idx == limit:
                logger.info(f"{channel_name}: {idx}/{limit} messages scraped so far")

            if message_delay > 0:
                await asyncio.sleep(message_delay)

        # Save all messages to JSON
        json_path = json_output_path(base_path, channel_name)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        logger.info(f"{channel_name}: {len(messages)} messages saved")
        return len(messages)

    except FloodWaitError as e:
        wait = max(int(e.seconds), 1)
        logger.warning(f"FloodWaitError on {channel}, sleeping {wait}s")
        await asyncio.sleep(wait)
        return 0

    except Exception as e:
        logger.error(f"Error scraping {channel}: {e}")
        return 0

# MAIN

async def main(
    base_path: str,
    channels: List[str],
    limit: int,
    message_delay: float,
    channel_delay: float
) -> None:
    client = TelegramClient("telegram_scraper_session", API_ID, API_HASH)
    stats: Dict[str, int] = {}

    csv_path = csv_output_path(base_path)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "message_id",
            "channel_name",
            "channel_title",
            "message_date",
            "message_text",
            "has_media",
            "image_path",
            "views",
            "forwards"
        ])

        async with client:
            for channel in channels:
                count = await scrape_channel(
                    client,
                    channel,
                    base_path,
                    writer,
                    limit,
                    message_delay
                )
                stats[channel.strip("@")] = count

                if channel_delay > 0:
                    await asyncio.sleep(channel_delay)

    write_manifest(base_path, stats)
    logger.info("Scraping complete")
    logger.info(f"Summary: {stats}")


# ENTRY POINT

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram medical channel scraper")
    parser.add_argument("--path", default="data", help="Base data directory")
    parser.add_argument("--limit", type=int, default=100, help="Messages per channel")
    parser.add_argument("--message-delay", type=float, default=DEFAULT_MESSAGE_DELAY)
    parser.add_argument("--channel-delay", type=float, default=DEFAULT_CHANNEL_DELAY)
    args = parser.parse_args()

    TARGET_CHANNELS = [
        "@CheMed123",
        "@lobelia4cosmetics",
        "@tikvahpharma",
        "@pharmaceuticals_sales",
        "@Ethiopharmaceuticals",
        "@PharmaceuticalandMedicalgroup" ]

    asyncio.run(
        main(
            base_path=args.path,
            channels=TARGET_CHANNELS,
            limit=args.limit,
            message_delay=args.message_delay,
            channel_delay=args.channel_delay,
        )
    )
