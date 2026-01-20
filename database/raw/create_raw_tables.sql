CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    message_id        BIGINT,
    channel_name      TEXT,
    channel_title     TEXT,
    message_date      TIMESTAMPTZ,
    message_text      TEXT,
    has_media         BOOLEAN,
    image_path        TEXT,
    views             INTEGER,
    forwards          INTEGER,
    ingestion_date    DATE,
    scrape_run_ts     TIMESTAMPTZ
);
