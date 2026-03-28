import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_mongo():
    url = os.environ.get("DATABASE_URL")
    print(f"Testing connection to: {url[:30]}...")
    client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
    try:
        # The ismaster command is cheap and does not require auth.
        await client.admin.command('ismaster')
        print("✅ MongoDB Connection Successful!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongo())
