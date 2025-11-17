# inbox/app/services/inbox.py
from datetime import datetime
from typing import List, Optional
from db import db 
from utils.logger import logger

async def save_incoming_message(message: dict):
    """Save an incoming message to MongoDB"""
    try:
        await db.messages.insert_one(message)
        logger.info(f"Saved incoming message from {message.get('user_id')}")
    except Exception as e:
        logger.error(f"Error saving message: {str(e)}")

async def save_outgoing_message(to: str, message: str, message_id: str, status: str = "sent"):
    """Save an outgoing message to MongoDB"""
    try:
        doc = {
            "user_id": to,
            "direction": "outbound",
            "body": message,
            "timestamp": datetime.utcnow(),
            "status": status,
            "message_id": message_id
        }
        await db.messages.insert_one(doc)
        logger.info(f"Saved outgoing message to {to}")
    except Exception as e:
        logger.error(f"Error saving outgoing message: {str(e)}")

async def get_messages_by_user(user_id: str, limit: int = 100) -> List[dict]:
    """Get all messages for a specific user"""
    try:
        cursor = db.messages.find({"user_id": user_id}).sort("timestamp", 1).limit(limit)
        messages = await cursor.to_list(length=limit)
        return messages
    except Exception as e:
        logger.error(f"Error fetching messages for {user_id}: {str(e)}")
        return []

async def get_all_conversations(limit: int = 50) -> List[dict]:
    """Get list of all users with their last message"""
    try:
        pipeline = [
            {
                "$sort": {"timestamp": -1}
            },
            {
                "$group": {
                    "_id": "$user_id",
                    "last_message": {"$first": "$body"},
                    "last_timestamp": {"$first": "$timestamp"},
                    "total_messages": {"$sum": 1}
                }
            },
            {
                "$sort": {"last_timestamp": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        cursor = db.messages.aggregate(pipeline)
        conversations = await cursor.to_list(length=limit)
        
        # Format response
        result = []
        for conv in conversations:
            result.append({
                "user_id": conv["_id"],
                "last_message": conv["last_message"],
                "last_timestamp": conv["last_timestamp"],
                "total_messages": conv["total_messages"],
                "unread_count": 0  # You can implement unread logic later
            })
        
        return result
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        return []

async def search_messages(query: str, limit: int = 50) -> List[dict]:
    """Search messages by content"""
    try:
        cursor = db.messages.find(
            {"body": {"$regex": query, "$options": "i"}}
        ).sort("timestamp", -1).limit(limit)
        
        messages = await cursor.to_list(length=limit)
        return messages
    except Exception as e:
        logger.error(f"Error searching messages: {str(e)}")
        return []

async def update_message_status(message_id: str, status: str):
    """Update the status of a message"""
    try:
        result = await db.messages.update_one(
            {"message_id": message_id},
            {"$set": {"status": status}}
        )
        if result.modified_count > 0:
            logger.info(f"Updated message {message_id} status to {status}")
    except Exception as e:
        logger.error(f"Error updating message status: {str(e)}")