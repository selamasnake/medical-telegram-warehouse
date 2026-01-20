# medical-telegram-warehouse

The goal of first task is to collect data from public Telegram channels, including messages and images, and store it in a raw data lake. This raw data will later be transformed and analyzed to generate insights such as top products, pricing trends, and visual content usage.

### Project Structure

- `data/` — raw Telegram messages and images (not tracked in git):
- `raw/telegram_messages/YYYY-MM-DD/` — JSON files for each channel.
- `raw/images/{channel_name}/ `— downloaded images per message.
- `_manifest.json` — summary of messages scraped per channel.
- `src/scraper.py` — Python script to extract messages and media from Telegram channels.
- `logs/` — logs and error reports generated during scraping.
- `.env` — stores Telegram API credentials securely:

### How to Run

Install dependencies:
```pip install -r requirements.txt```

Run the scraper (example: 500 messages per channel):
```python src/scraper.py --path data --limit 500 --message-delay 1 --channel-delay 3```

Check outputs:
- JSON messages → data/raw/telegram_messages/YYYY-MM-DD/
- Images → data/raw/images/{channel_name}/
- Manifest → _manifest.json
- Logs → logs/scrape_YYYY-MM-DD.log

### Notes

- Each run generates a manifest summarizing the number of messages scraped per channel.
- Images are stored in a structured folder for easy integration into future analysis pipelines.
- The scraper handles rate limits and errors, logging issues for later inspection.

### Requirements

`python-dotenv` — load environment variables
`telethon` — Telegram API client