from fastapi import APIRouter
from pydantic import BaseModel
from groq import AsyncGroq
import os
import base64
from io import BytesIO
import gtts
from gtts import gTTS
print("Loaded gTTS successfully")
from api import vector_db

# TTS integration for Squirrel IAS
router = APIRouter(prefix="/api/assistant", tags=["Assistant"])

try:
    groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    groq_client = None

class ChatRequest(BaseModel):
    message: str
    role_context: str = "Student"
    user_interests: list[str] = ["general current affairs"]
    history: str = ""

@router.post("/chat")
async def chat_with_squirrel(request: ChatRequest):
    if not groq_client: 
        return {"response": "Squirrel is resting right now (Missing API Key)."}
    
    system_prompt = (
        "You are Squirrel, a current-affairs mentor for Indian learners and UPSC aspirants. "
        "Keep answers concise, factual, and exam-oriented when relevant. "
        "If asked for revision, provide bullets with key facts, background, and likely exam angle. "
        "Do not fabricate specific numbers when uncertain."
    )
    
    # RAG lookup using FAISS vector DB
    rag_results = vector_db.search_index(request.message, k=3)
    news_context = ""
    for idx, res in enumerate(rag_results):
        news_context += f"📰 [{res['metadata']['source']}] {res['metadata']['title']}\n"
    
    user_prompt = (
        f"User role: {request.role_context}\n"
        f"User interests: {', '.join(request.user_interests) if request.user_interests else 'general current affairs'}\n\n"
        f"Context from recent news (if relevant):\n{news_context}\n\n"
        f"Conversation:\n{request.history}\n"
        f"USER: {request.message}"
    )
    
    try:
        response = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=400,
            temperature=0.5
        )
        reply = response.choices[0].message.content
        if reply:
            return {"response": reply}
            
        return {"response": "I am ready to help with current affairs. Ask about economy, polity, IR, or quiz prep!"}
    except Exception as e:
        return {"response": f"Oops! I had a little hiccup 🐿️ — {str(e)}"}

class QuizRequest(BaseModel):
    article_content: str

@router.post("/generate_quiz")
async def generate_quiz(request: QuizRequest):
    if not groq_client: return {"error": "Quiz generation unavailable."}
    
    system_prompt = """You are a quiz master. Create 3 multiple choice questions based on the provided text.
Format EXACTLY as valid JSON with the following structure:
[
  {
    "question": "What is the capital of France?",
    "options": ["London", "Berlin", "Paris", "Madrid"],
    "answer": 2, // zero-indexed correct option
    "explanation": "Paris is the capital."
  }
]
Reply with ONLY the raw JSON array. Do not wrap in markdown tags."""

    try:
        response = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.article_content}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=600,
            temperature=0.4
        )
        
        import json
        answer = response.choices[0].message.content.strip()
        if answer.startswith("```json"): answer = answer.replace("```json", "", 1)
        if answer.startswith("```"): answer = answer.replace("```", "", 1)
        if answer.endswith("```"): answer = answer[:-3]
        
        quiz_data = json.loads(answer.strip())
        return {"quiz": quiz_data}
    except Exception as e:
        print(f"Quiz error: {e}")
        return {"error": "Failed to generate quiz."}

class TTSRequest(BaseModel):
    text: str

@router.post("/tts")
async def generate_tts(request: TTSRequest):
    if not gTTS:
        return {"error": "TTS engine not installed."}
    try:
        tts = gTTS(text=request.text, lang='en', tld='co.in')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
        data_uri = f"data:audio/mp3;base64,{audio_base64}"
        return {"audio_base64": data_uri, "fallbackText": request.text}

    except Exception as e:
        return {"error": f"TTS generation failed: {e}"}
