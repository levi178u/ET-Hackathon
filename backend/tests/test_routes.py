import httpx
import asyncio

BASE_URL = "http://127.0.0.1:8000"

async def test_all():
    async with httpx.AsyncClient() as client:
        print("1. Testing Health")
        res = await client.get(f"{BASE_URL}/api/health")
        print("Health:", res.json())
        
        print("\n2. Testing Auth Registration")
        user_data = {
            "email": "test_auth@example.com",
            "password": "password123",
            "name": "Jane Doe"
        }
        res = await client.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print("Auth Register:", res.json())
        
        print("\n3. Testing News Fetching (Includes FAISS Vector DB Embedding)")
        res = await client.get(f"{BASE_URL}/api/news/fetch")
        print(f"News Fetched: {res.json().get('count', 0)} articles")
        
        print("\n4. Testing Squirrel Chatbot (With FAISS RAG & UPSC Prompt)")
        chat_data = {
            "message": "What is the recent development in India's semiconductor policy?",
            "role_context": "UPSC Aspirant",
            "user_interests": ["Technology", "Economy"],
            "history": "USER: Hello\nSQUIRREL: Hi! How can I help you today?"
        }
        # Give it a longer timeout as Groq + RAG might take 2-3s
        res = await client.post(f"{BASE_URL}/api/assistant/chat", json=chat_data, timeout=15.0)
        print("Chatbot Reply:\n", res.json().get('response', res.text))
        
        print("\n5. Testing TTS Narration Endpoint")
        tts_data = {"text": "Hello, this is a test of the Text to Speech system for the 60 second briefing."}
        res = await client.post(f"{BASE_URL}/api/assistant/tts", json=tts_data, timeout=15.0)
        tts_json = res.json()
        audio_uri = tts_json.get('audioDataUri', '')
        print("TTS generated Base64 Audio URI len:", len(audio_uri), "(If > 100, Success)")
        
        print("\n6. Testing Stripe Checkout Session")
        res = await client.post(f"{BASE_URL}/api/payment/create-checkout-session")
        print("Stripe URL:", res.json().get("url"))

if __name__ == "__main__":
    asyncio.run(test_all())
