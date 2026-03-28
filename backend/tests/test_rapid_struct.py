import os
import httpx
import asyncio
import json
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
    
    results = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        for ep in endpoints:
            url = f"https://{host}/{ep}"
            print(f"Fetching {ep}...")
            try:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    results[ep] = res.json()
                else:
                    results[ep] = f"Error {res.status_code}: {res.text[:100]}"
            except Exception as e:
                results[ep] = f"Exception: {str(e)}"
    
    with open("rapid_debug.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to rapid_debug.json")

if __name__ == "__main__":
    asyncio.run(test_rapid())
