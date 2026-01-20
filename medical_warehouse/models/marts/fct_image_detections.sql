{{ config(
    materialized='table'
) }}

with detections as (

    select
        replace(image_name, '.jpg', '')::bigint as message_id,
        detected_objects as detected_class,
        max_confidence as confidence_score,
        image_category
    from medical_warehouse_staging.stg_yolo_detections

),

messages as (

    select
        message_id,
        channel_key,
        date_key,
        view_count
    from medical_warehouse_marts.fct_messages
    where has_image = true

)

select
    m.message_id,
    m.channel_key,
    m.date_key,
    d.detected_class,
    d.confidence_score,
    d.image_category
from messages m
left join detections d
    on m.message_id = d.message_id
