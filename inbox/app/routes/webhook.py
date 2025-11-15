# app/routes/webhook.py
from fastapi import APIRouter, Request
from app.services.inbox import save_incoming_message

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == "your_verify_token":
        return params.get("hub.challenge")
    return {"status": "verification failed"}

@router.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.json()
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])

        for msg in messages:
            await save_incoming_message({
                "user_id": msg["from"],
                "direction": "inbound",
                "body": msg.get("text", {}).get("body", ""),
                "timestamp": msg["timestamp"],
                "status": "received"
            })

    except Exception as e:
        print("Webhook error:", e)

    return {"status": "ok"}