# inbox/app/services/whatsapp.py
import requests
from typing import Optional, Dict
from config import WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
from utils.logger import logger

class WhatsAppService:
    def __init__(self):
        self.access_token = WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = WHATSAPP_PHONE_NUMBER_ID
        self.api_url = f"https://graph.facebook.com/v22.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def send_text_message(self, to: str, message: str) -> Dict:
        """
        Send a text message via WhatsApp Business API
        
        Args:
            to: Recipient phone number (with country code, no +)
            message: Message text to send
            
        Returns:
            Dict with success status and message_id or error
        """
        # Clean phone number
        to = to.replace("+", "").replace(" ", "").replace("-", "")
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                message_id = response_data.get("messages", [{}])[0].get("id")
                logger.info(f"Message sent successfully to {to}, ID: {message_id}")
                return {
                    "success": True,
                    "message_id": message_id,
                    "error": None
                }
            else:
                error_msg = response_data.get("error", {}).get("message", "Unknown error")
                logger.error(f"Failed to send message to {to}: {error_msg}")
                return {
                    "success": False,
                    "message_id": None,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Exception while sending message to {to}: {str(e)}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to mark message as read: {str(e)}")
            return False

# Create singleton instance
whatsapp_service = WhatsAppService()