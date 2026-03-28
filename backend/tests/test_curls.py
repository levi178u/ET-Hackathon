import requests

BASE_URL = "http://127.0.0.1:8001/api"

print("\n--- 1. Testing Chatbot Endpoint ---")
try:
    res = requests.post(f"{BASE_URL}/assistant/chat", json={
        "message": "Explain what inflation is in 2 sentences.",
        "role_context": "Student"
    })
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json().get('response')}")
except Exception as e:
    print(f"Error testing chatbot: {e}")

print("\n--- 2. Testing Quiz Engine ---")
try:
    res = requests.post(f"{BASE_URL}/assistant/generate_quiz", json={
        "article_content": "The Reserve Bank of India (RBI) lowered the repo rate by 50 basis points to stimulate the economy. This marks the first cut in two years, aiming to boost borrowing and investment."
    })
    print(f"Status: {res.status_code}")
    data = res.json()
    quiz = data.get('quiz', [])
    print(f"Total Questions: {len(quiz)}")
    if quiz:
        print(f"Sample Q: {quiz[0].get('question')}")
except Exception as e:
    print(f"Error testing quiz: {e}")

print("\n--- 3. Testing RapidAPI Endpoints (Requires API Key) ---")
print("Note: Unless RAPIDAPI_KEY is configured in .env, these will return 500.")
for ep in ["international-today", "recent", "today-quiz", "history-of-today"]:
    try:
        res = requests.get(f"{BASE_URL}/news/current-affairs/{ep}")
        print(f"Endpoint /{ep} -> Status: {res.status_code}")
    except Exception as e:
        print(f"Error testing {ep}: {e}")

print("\n✅ Verification complete.")
