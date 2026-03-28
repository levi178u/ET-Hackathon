import os
import asyncio
from groq import AsyncGroq

async def test_key():
    key = "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"
    client = AsyncGroq(api_key=key)
    print(f"Testing key: {key[:10]}...")
    
    models = ["llama-3.1-8b-instant", "llama3-8b-8192", "gemma2-9b-it", "mixtral-8x7b-32768"]
    
    for model in models:
        print(f"\nTrying model: {model}")
        try:
            chat_completion = await client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model=model,
            )
            print(f"✅ Success: {chat_completion.choices[0].message.content[:50]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_key())
