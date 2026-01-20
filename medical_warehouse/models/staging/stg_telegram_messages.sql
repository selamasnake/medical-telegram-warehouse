-- models/staging/stg_telegram_messages.sql
{{ config(
    materialized='view'
) }}

WITH raw AS (

    SELECT *
    FROM raw.telegram_messages

)

SELECT
    message_id,
    channel_name,
    channel_title,
    message_date::timestamp AS message_date,
    message_text,
    has_media::boolean AS has_media,
    image_path,
    views::int AS views,
    forwards::int AS forwards,
    -- calculated fields
    LENGTH(message_text) AS message_length,
    CASE WHEN has_media THEN TRUE ELSE FALSE END AS has_image
FROM raw
WHERE message_text IS NOT NULL
  AND message_text <> ''
