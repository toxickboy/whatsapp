# inbox/app/routes/webhook.py
from fastapi import APIRouter, Request
from datetime import datetime
from services.inbox import save_incoming_message, update_message_status
from config import WEBHOOK_VERIFY_TOKEN
from utils.logger import logger

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook for WhatsApp Business API"""
    params = dict(request.query_params)
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    logger.info(f"Webhook verification attempt - Mode: {mode}, Token matches: {token == WEBHOOK_VERIFY_TOKEN}")
    
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return int(challenge)
    
    logger.warning("Webhook verification failed")
    return {"status": "verification failed"}, 403

@router.post("/webhook")
async def receive_webhook(request: Request):
    """Receive incoming messages and status updates from WhatsApp"""
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")
        
        # Extract entry data
        entry = body.get("entry", [])
        if not entry:
            return {"status": "ok"}
        
        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ok"}
        
        value = changes[0].get("value", {})
        
        # Handle incoming messages
        messages = value.get("messages", [])
        for msg in messages:
            message_type = msg.get("type", "text")
            
            message_data = {
                "user_id": msg["from"],
                "direction": "inbound",
                "body": "",
                "timestamp": datetime.fromtimestamp(int(msg["timestamp"])),
                "status": "received",
                "message_id": msg["id"]
            }
            
            # Extract message body based on type
            if message_type == "text":
                message_data["body"] = msg.get("text", {}).get("body", "")
            elif message_type == "image":
                message_data["body"] = "[Image]"
                message_data["media_url"] = msg.get("image", {}).get("id")
                message_data["media_type"] = "image"
            elif message_type == "video":
                message_data["body"] = "[Video]"
                message_data["media_url"] = msg.get("video", {}).get("id")
                message_data["media_type"] = "video"
            elif message_type == "audio":
                message_data["body"] = "[Audio]"
                message_data["media_url"] = msg.get("audio", {}).get("id")
                message_data["media_type"] = "audio"
            elif message_type == "document":
                message_data["body"] = "[Document]"
                message_data["media_url"] = msg.get("document", {}).get("id")
                message_data["media_type"] = "document"
            else:
                message_data["body"] = f"[{message_type}]"
            
            await save_incoming_message(message_data)
            logger.info(f"Processed incoming message from {msg['from']}")
        
        # Handle status updates (delivered, read, etc.)
        statuses = value.get("statuses", [])
        for status in statuses:
            message_id = status.get("id")
            new_status = status.get("status")
            
            if message_id and new_status:
                await update_message_status(message_id, new_status)
                logger.info(f"Updated message {message_id} status to {new_status}")
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
    
    return {"status": "ok"}