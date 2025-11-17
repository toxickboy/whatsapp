import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Import config
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI ="mongodb+srv://ocavior:Qwerty123@backupcluster.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
DB_NAME = os.getenv("DB_NAME", "whatsapp_inbox")

async def setup_indexes():
    print(f"Connecting to MongoDB: {MONGO_URI}")
    print(f"Database: {DB_NAME}")
    
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        print("✓ MongoDB connection successful!\n")
        
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
        try:
            await db.messages.create_index([("body", "text")])
            print("✓ Created text index on body")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ Text index already exists")
            else:
                print(f"⚠ Could not create text index: {e}")
        
        print("\n✅ Database indexes created successfully!")
        print("\nYou can now start the application with:")
        print("cd inbox && uvicorn app.main:app --reload")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your MONGO_URI in .env file")
        print("2. Verify your MongoDB Atlas connection string is correct")
        print("3. Make sure your IP is whitelisted in MongoDB Atlas")
        print("4. Check if your MongoDB Atlas user has proper permissions")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(setup_indexes())