-- Ensure no message_id is NULL in raw table
SELECT *
FROM raw.telegram_messages
WHERE message_id IS NULL
