import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()


# Load the CSV
df = pd.read_csv('data/processed/yolo_detections.csv')

# Connect to PostgreSQL
POSTGRES_URI = os.getenv('POSTGRES_URI')
if POSTGRES_URI is None:
    raise ValueError("POSTGRES_URI not set in environment variables!")

engine = create_engine(POSTGRES_URI) 

# Load into staging schema
df.to_sql('stg_yolo_detections', engine, schema='medical_warehouse_staging', if_exists='replace', index=False)

print("YOLO CSV loaded into staging.stg_yolo_detections")
