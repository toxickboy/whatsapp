# inbox/app/routes/messages.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.model import Message
from app.schemas import MessageOut, ConversationOut, SendMessageResponse
from app.services.inbox import get_messages_by_user
from app.services.whatsapp import whatsapp_service
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["messages"])

@router.get("/conversations", response_model=List[ConversationOut])
async def list_conversations(limit: int = Query(50, ge=1, le=100)):
    """Get all conversations with last message"""
    try:
        conversations = await get_all_conversations(limit)
        return conversations
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@router.get("/conversations/{user_id}", response_model=List[MessageOut])
async def get_conversation(user_id: str, limit: int = Query(100, ge=1, le=500)):
    """Get all messages for a specific user"""
    try:
        messages = await get_messages_by_user(user_id, limit)
        
        # Convert MongoDB documents to response format
        result = []
        for msg in messages:
            result.append({
                "user_id": msg.get("user_id"),
                "direction": msg.get("direction"),
                "body": msg.get("body"),
                "timestamp": msg.get("timestamp"),
                "status": msg.get("status"),
                "message_id": msg.get("message_id")
            })
        
        return result
    except Exception as e:
        logger.error(f"Error fetching conversation for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversation")

@router.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    """Send a message to a user"""
    try:
        # Send via WhatsApp API
        result = whatsapp_service.send_text_message(request.to, request.message)
        
        # Save to database if successful
        if result["success"]:
            await save_outgoing_message(
                to=request.to,
                message=request.message,
                message_id=result["message_id"],
                status="sent"
            )
        
        return {
            "success": result["success"],
            "message_id": result["message_id"],
            "error": result["error"]
        }
    
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[MessageOut])
async def search_conversation(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100)
):
    """Search messages by content"""
    try:
        messages = await search_messages(q, limit)
        
        result = []
        for msg in messages:
            result.append({
                "user_id": msg.get("user_id"),
                "direction": msg.get("direction"),
                "body": msg.get("body"),
                "timestamp": msg.get("timestamp"),
                "status": msg.get("status"),
                "message_id": msg.get("message_id")
            })
        
        return result
    except Exception as e:
        logger.error(f"Error searching messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search messages")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "whatsapp-inbox"}