# inbox/setup_db.py
"""
Setup script to create MongoDB indexes for better performance
Run this once before starting the application
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

async def setup_indexes():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Creating indexes...")
    
    # Index on user_id for faster conversation queries
    await db.messages.create_index("user_id")
    print("✓ Created index on user_id")
    
    # Index on timestamp for sorting
    await db.messages.create_index("timestamp")
    print("✓ Created index on timestamp")
    
    # Compound index for user conversations sorted by time
    await db.messages.create_index([("user_id", 1), ("timestamp", -1)])
    print("✓ Created compound index on user_id and timestamp")
    
    # Index on message_id for status updates
    await db.messages.create_index("message_id", unique=True, sparse=True)
    print("✓ Created index on message_id")
    
    # Text index for message search
    await db.messages.create_index([("body", "text")])
    print("✓ Created text index on body")
    
    print("\n✅ Database indexes created successfully!")
    print("\nYou can now start the application with:")
    print("cd inbox && python -m uvicorn app.main:app --reload")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_indexes())