from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

# 1. Replace with your actual DB credentials
DATABASE_URL='postgresql+psycopg2://medical_user:medical_password@localhost:5432/medical_dw'

# 2. Set up SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

channel_name = "tikvahpharma"

# 3. Open a session and run the query
with SessionLocal() as db:
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
    rows = db.execute(query, {"channel_name": channel_name}).fetchall()
    
    # 4. Print results
    for row in rows:
        print(dict(row._mapping))