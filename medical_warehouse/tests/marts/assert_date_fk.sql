-- Ensure all messages reference a valid date
SELECT f.*
FROM medical_warehouse.fct_messages f
LEFT JOIN medical_warehouse.dim_dates d
ON f.date_key = d.date_key
WHERE d.date_key IS NULL
