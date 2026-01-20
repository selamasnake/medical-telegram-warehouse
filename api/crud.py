from sqlalchemy.orm import Session
from sqlalchemy import text


def get_top_products(db: Session, limit: int = 10):
    query = text("""
    SELECT product, COUNT(*) AS mentions
    FROM medical_warehouse_marts.fct_messages
    CROSS JOIN LATERAL unnest(string_to_array(lower(message_text), ' ')) AS product
    GROUP BY product
    ORDER BY mentions DESC
    LIMIT :limit;
    """)
    return db.execute(query, {"limit": limit}).fetchall()

def get_channel_activity(db: Session, channel_name: str):
    query = text("""
        SELECT f.date_key AS date,
               COUNT(*) AS messages,
               SUM(f.view_count) AS views
        FROM medical_warehouse_marts.fct_messages f
        JOIN medical_warehouse_marts.dim_channels c
          ON f.channel_key = c.channel_key
        WHERE c.channel_name = :channel_name
        GROUP BY f.date_key
        ORDER BY f.date_key;
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    # Convert to list of dicts for FastAPI JSON response
    return [{"date": row.date, "messages": row.messages, "views": row.views} for row in result]

def search_messages(db: Session, keyword: str, limit: int = 20):
    query = text("""
    SELECT message_id, channel_name, message_text, views
    FROM medical_warehouse.fct_messages
    WHERE message_text ILIKE :keyword
    ORDER BY message_date DESC
    LIMIT :limit;
    """)
    return db.execute(query, {"keyword": f"%{keyword}%", "limit": limit}).fetchall()

def visual_content_stats(db: Session):
    query = text("""
    SELECT c.channel_name,
           COUNT(*) AS image_posts,
           SUM(CASE WHEN image_category = 'promotional' THEN 1 ELSE 0 END) AS promotional,
           SUM(CASE WHEN image_category = 'product_display' THEN 1 ELSE 0 END) AS product_display,
           SUM(CASE WHEN image_category = 'lifestyle' THEN 1 ELSE 0 END) AS lifestyle,
           SUM(CASE WHEN image_category = 'other' THEN 1 ELSE 0 END) AS other
    FROM medical_warehouse_marts.fct_image_detections d
    JOIN medical_warehouse_marts.dim_channels c
      ON d.channel_key = c.channel_key
    GROUP BY c.channel_name
    ORDER BY image_posts DESC;
    """)
    return db.execute(query).fetchall()
