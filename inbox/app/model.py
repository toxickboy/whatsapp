from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

class Message(BaseModel):
    user_id: str
    direction: Literal["inbound", "outbound"]
    body: str
    timestamp: datetime
    status: Optional[str]