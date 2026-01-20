{{ config(
    materialized='table'
) }}

WITH channels AS (
    SELECT
        channel_name,
        channel_title,
        -- Simple logic to assign channel_type; adjust as needed
        CASE
            WHEN channel_name ILIKE '%pharma%' THEN 'Pharmaceutical'
            WHEN channel_name ILIKE '%cosmetic%' THEN 'Cosmetics'
            ELSE 'Medical'
        END AS channel_type,
        MIN(message_date) AS first_post_date,
        MAX(message_date) AS last_post_date,
        COUNT(*) AS total_posts,
        AVG(views) AS avg_views
    FROM {{ ref('stg_telegram_messages') }}
    GROUP BY channel_name, channel_title
)

SELECT
    ROW_NUMBER() OVER (ORDER BY channel_name) AS channel_key, -- surrogate key
    channel_name,
    channel_title,
    channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
FROM channels
