from pydantic import BaseModel
from typing import List, Optional

class TopProduct(BaseModel):
    product: str
    mentions: int

class ChannelActivity(BaseModel):
    date: str
    messages: int
    views: int

class Message(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    views: int

class VisualContentStats(BaseModel):
    channel_name: str
    image_posts: int
    promotional: int
    product_display: int
    lifestyle: int
    other: int
