# inbox/app/models.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Message(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str  # Phone number of the user
    direction: Literal["inbound", "outbound"]
    body: str
    timestamp: datetime
    status: Optional[str] = "received"  # received, sent, delivered, read, failed
    message_id: Optional[str] = None  # WhatsApp message ID
    media_url: Optional[str] = None
    media_type: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SendMessageRequest(BaseModel):
    to: str
    message: str

class MessageResponse(BaseModel):
    user_id: str
    direction: str
    body: str
    timestamp: datetime
    status: Optional[str]
    message_id: Optional[str] = None

class ConversationResponse(BaseModel):
    user_id: str
    messages: List[MessageResponse]
    total_messages: int

class UserListResponse(BaseModel):
    users: List[dict]
    total: int