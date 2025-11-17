from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

class Message(BaseModel):
    user_id: str
    direction: Literal["inbound", "outbound"]
    body: str
    timestamp: datetime
    status: Optional[str]

class SendMessageRequest(BaseModel):
    to: str
    message: str

class MessageResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None

class ConversationResponse(BaseModel):
    user_id: str
    last_message: str
    last_timestamp: datetime
    unread_count: int = 0
    total_messages: int = 0