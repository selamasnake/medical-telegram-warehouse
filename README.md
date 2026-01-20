# medical-telegram-warehouse

This project collects data from public Telegram channels, including messages and images, and transforms it into a clean, structured data warehouse for analysis. Insights generated can include top products, pricing trends, and visual content usage.
### Project Structure

- `data/` — raw Telegram messages and images (not tracked in git):
- `raw/telegram_messages/YYYY-MM-DD/` — JSON files for each channel.
- `raw/images/{channel_name}/ `— downloaded images per message.
- `_manifest.json` — summary of messages scraped per channel.
- `src/scraper.py` — Python script to extract messages and media from Telegram channels.
- `logs/` — logs and error reports generated during scraping.
- `.env` — stores Telegram API credentials securely
- `medical_warehouse/` — dbt project for transforming raw data into a structured warehouse
  - `dbt_project.yml` — dbt project configuration
  - `profiles.yml` — database connection settings
  - `models/`  
    - `staging/` — staging models (clean and standardize raw data)
      - `stg_telegram_messages.sql`
      - `schema.yml`
    - `marts/` — dimensional models (star schema)
      - `dim_channels.sql`
      - `dim_dates.sql`
      - `fct_messages.sql`
      - `schema.yml`
  - `tests/` — custom data tests for business rules
    - `assert_no_future_messages.sql`
    - `assert_positive_views.sql`
    - `assert_channel_fk.sql`
    - `assert_date_fk.sql`

### How to Run

Install dependencies:
```bash 
pip install -r requirements.txt
```

### 1. Data Extraction

Run the scraper (example: 500 messages per channel):
```bash 
python src/scraper.py --path data --limit 500 --message-delay 1 --channel-delay 3
```
Check outputs:
- JSON messages → `data/raw/telegram_messages/YYYY-MM-DD/`
- Images → `data/raw/images/{channel_name}/`
- Manifest → `_manifest.json`
- Logs → `logs/scrape_YYYY-MM-DD.log`

#### Notes
- Each run generates a manifest summarizing the number of messages scraped per channel.
- Images are stored in a structured folder for easy integration into future analysis pipelines.
- The scraper handles rate limits and errors, logging issues for later inspection.

### 2. Data Transformation & Warehouse
Initialize project & set up profile : 

```bash 
dbt init medical_warehouse
```

Configure `profiles.yml` to connect to PostgreSQL database.

Run dbt models and test the data

```bash
cd medical_warehouse
dbt run
dbt test
```
Generate documentation
```bash 
dbt docs generate
dbt docs serve
```
- View table/column descriptions and lineage in the dbt docs site.

#### Notes

- Staging models clean and standardize raw data before loading into the warehouse.
- Mart models implement a star schema:
- Dimensions: dim_channels, dim_dates
- Fact: fct_messages
- All critical columns are validated with not_null and unique tests.
- Custom tests enforce business rules (no future messages, non-empty texts, positive view counts).

### Requirements

- `python-dotenv` — load environment variables
- `telethon` — Telegram API client
- `dbt-postgres` — dbt adapter for PostgreSQL
- `psycopg2` — PostgreSQL database driver