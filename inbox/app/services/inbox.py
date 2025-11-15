# app/services/inbox.py
from app.database import db

async def save_incoming_message(message: dict):
    await db.messages.insert_one(message)


# app/services/inbox.py
async def get_messages_by_user(user_id: str):
    cursor = db.messages.find({"user_id": user_id}).sort("timestamp", 1)
    return await cursor.to_list(length=100)