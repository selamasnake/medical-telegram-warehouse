from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import database, schemas, crud
from .database import get_db


app = FastAPI(title="Medical Telegram Analytics API")

# Dependency
def get_db_session():
    return next(database.get_db())

@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct])
def top_products(limit: int = 10, db: Session = Depends(get_db_session)):
    return crud.get_top_products(db, limit)

@app.get("/api/channels/{channel_name}/activity")
def channel_activity(channel_name: str, db: Session = Depends(get_db_session)):
    return crud.get_channel_activity(db, channel_name)

@app.get("/api/search/messages", response_model=List[schemas.Message])
def message_search(query: str, limit: int = 20, db: Session = Depends(get_db_session)):
    return crud.search_messages(db, query, limit)

@app.get("/api/reports/visual-content", response_model=List[schemas.VisualContentStats])
def visual_content(db: Session = Depends(get_db_session)):
    return crud.visual_content_stats(db)

