# inbox/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import webhook, messages
from app.utils.logger import logger
from app.config import API_HOST, API_PORT

app = FastAPI(
    title="WhatsApp Inbox API",
    description="API for managing WhatsApp conversations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, tags=["webhook"])
app.include_router(messages.router, tags=["messages"])

@app.on_event("startup")
async def startup_event():
    logger.info("WhatsApp Inbox API starting up...")
    logger.info(f"API running on http://{API_HOST}:{API_PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("WhatsApp Inbox API shutting down...")

@app.get("/")
async def root():
    return {
        "message": "WhatsApp Inbox API",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/webhook",
            "conversations": "/api/conversations",
            "send": "/api/send",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )