-- Ensure all messages reference a valid channel
SELECT f.*
FROM medical_warehouse.fct_messages f
LEFT JOIN medical_warehouse.dim_channels d
ON f.channel_key = d.channel_key
WHERE d.channel_key IS NULL
