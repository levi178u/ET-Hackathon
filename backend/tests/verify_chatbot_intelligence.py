import httpx
import asyncio
import json

BASE_URL = "http://127.0.0.1:8001"

async def test_chatbot_scenarios():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("--- 🧠 squirrel chatbot verification ---")
        
        # Step 1: Ensure news is fetched and indexed
        print("\n[1] refreshing news feed for faiss index...")
        await client.get(f"{BASE_URL}/api/news/fetch")
        
        scenarios = [
            {
                "name": "recent news awareness (rag)",
                "payload": {
                    "message": "What is the most recent update on Indian economy from the feed?",
                    "role_context": "UPSC Aspirant",
                    "user_interests": ["Economy"],
                    "history": ""
                }
            },
            {
                "name": "upsc exam orientation",
                "payload": {
                    "message": "Why should a UPSC aspirant care about the latest semiconductor policy?",
                    "role_context": "UPSC Aspirant",
                    "user_interests": ["Technology"],
                    "history": ""
                }
            },
            {
                "name": "concise revision request",
                "payload": {
                    "message": "Give me a 3-point bulleted revision of current affairs for today.",
                    "role_context": "Student",
                    "user_interests": ["General"],
                    "history": ""
                }
            }
        ]
        
        for scenario in scenarios:
            print(f"\n🚀 testing scenario: {scenario['name']}")
            res = await client.post(f"{BASE_URL}/api/assistant/chat", json=scenario['payload'])
            if res.status_code == 200:
                print(f"✅ reply: {res.json().get('response')}\n")
            else:
                print(f"❌ failed: {res.text}\n")

if __name__ == "__main__":
    asyncio.run(test_chatbot_scenarios())
