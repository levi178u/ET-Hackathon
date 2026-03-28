import os
import httpx
import asyncio
import traceback
from dotenv import load_dotenv

async def test_rapid():
    load_dotenv()
    key = os.getenv("RAPIDAPI_KEY")
    host = "current-affairs-of-india.p.rapidapi.com"
    endpoints = ["recent", "international-today", "history-of-today", "today-quiz"]
    
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": host
    }
    
    async with httpx.AsyncClient() as client:
        for ep in endpoints:
            url = f"https://{host}/{ep}"
            print(f"Testing {ep}...")
            try:
                res = await client.get(url, headers=headers)
                print(f"  Status: {res.status_code}")
                print(f"  Body: {res.text[:200]}")
            except Exception:
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rapid())
