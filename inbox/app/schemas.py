# inbox/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageOut(BaseModel):
    user_id: str
    direction: str
    body: str
    timestamp: datetime
    status: Optional[str]
    message_id: Optional[str] = None

    class Config:
        from_attributes = True

class ConversationOut(BaseModel):
    user_id: str
    last_message: str
    last_timestamp: datetime
    unread_count: int = 0
    total_messages: int

class SendMessageResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None