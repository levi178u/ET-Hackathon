from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from typing import List, Dict, Any
import feedparser
from groq import AsyncGroq
import os
import asyncio
import anyio
from newsapi import NewsApiClient
from api import vector_db

router = APIRouter(prefix="/api/news", tags=["News"])

RSS_FEEDS = {
    "Economic Times": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "Times of India": "https://timesofindia.indiatimes.com/rssfeedmostrecent.cms",
    "The Hindu": "https://www.thehindu.com/news/national/feeder/default.rss",
    "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
}

try:
    groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    groq_client = None

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
newsapi = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY and len(NEWS_API_KEY) > 10 else None

async def summarize_article(content: str) -> str:
    if not groq_client: return "Summarization unavailable (API Key missing)."
    try:
        response = await groq_client.chat.completions.create(
            messages=[{
                "role": "system", "content": "You are an expert news summarizer. Summarize the following text in 3-4 concise, objective sentences suitable for a 60-second briefing."
            }, {
                "role": "user", "content": content
            }],
            model="llama-3.1-8b-instant",
            max_tokens=250,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing: {str(e)}"

async def generate_insights(content: str, role: str) -> str:
    # ... (rest of the generate_insights function)
    role_instructions = {
        "Student": "Explain why this news is critical for a Student (e.g., UPSC/competitive exam preparation, syllabus relevance like GS-II/III, or academic knowledge). Specifically answer: 'Why is this important for your exams or studies?'",
        "Investor": "Explain why this news is critical for an Investor (e.g., impact on specific market sectors, macroeconomic trends, or stock volatility). Specifically answer: 'How does this affect your portfolio or market strategy?'",
        "Developer": "Explain why this news is critical for a Tech Developer (e.g., new frameworks, industry shifts towards AI, or job market impacts). Specifically answer: 'How does this change the tech landscape you build in?'",
        "Founder": "Explain why this news is critical for a Startup Founder (e.g., competitive intelligence, new regulatory hurdles, or funding opportunities). Specifically answer: 'What is the strategic takeaway for your business?'"
    }
    instruction = role_instructions.get(role, "Explain why this news is important and provide a key takeaway.")
    try:
        response = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an elite analyst providing role-specific 'Smart Insights'. You must refer to the article's core points and explicitly answer 'Why this matters' for the user's specific role. Keep it to 3-4 impactful sentences."},
                {"role": "user", "content": f"Article Content: {content}\n\nTask: {instruction}"}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=200,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Insight error: {e}")
        return "Insight generation failed. Please try again later."

async def get_latest_articles(background_tasks: BackgroundTasks = None) -> List[Dict[str, Any]]:
    """Core logic to fetch latest news from multiple sources."""
    articles = []
    
    def index_article(item):
        try:
            vector_db.add_to_index(f"{item['title']}. {item['summary_raw']}", item)
        except Exception as e:
            print(f"Background indexing error: {e}")

    # 1. Fetch from NewsAPI First (Live headlines)
    if NEWS_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={"language": "en", "country": "in", "apiKey": NEWS_API_KEY},
                    timeout=5.0
                )
                resp.raise_for_status()
                top_headlines = resp.json()
                
            for article in top_headlines.get('articles', [])[:10]:
                content = article.get('description', '') or article.get('content', '')
                if not content: continue
                item = {
                    "title": article.get('title'),
                    "link": article.get('url'),
                    "summary_raw": content,
                    "source": article.get('source', {}).get('name', 'NewsAPI'),
                    "publishedAt": article.get('publishedAt', '')
                }
                articles.append(item)
                if background_tasks:
                    background_tasks.add_task(index_article, item)
        except Exception as e:
            print(f"NewsAPI error: {e}")

    # 2. Add Standard RSS in Parallel
    import httpx
    async def fetch_rss_source(source, url):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                response.raise_for_status()
                feed = feedparser.parse(response.text)

            source_articles = []
            for entry in feed.entries[:8]: 
                content = (entry.get('summary', '') or entry.get('description', '')).strip()
                if not content or len(content) < 10:
                    continue
                item = {
                    "title": entry.get('title', 'No Title'),
                    "link": entry.get('link', '#'),
                    "summary_raw": content,
                    "source": source,
                    "publishedAt": entry.get('published', entry.get('updated', ''))
                }
                source_articles.append(item)
                if background_tasks:
                    background_tasks.add_task(index_article, item)
            return source_articles
        except Exception as e:
            print(f"RSS error for {source}: {e}")
            return []

    rss_tasks = [fetch_rss_source(source, url) for source, url in RSS_FEEDS.items()]
    rss_results = await asyncio.gather(*rss_tasks)
    for result in rss_results:
        articles.extend(result)
    
    return articles

@router.get("/fetch")
async def fetch_news(background_tasks: BackgroundTasks):
    """Fetches latest news and indexes in background to prevent request timeouts."""
    articles = await get_latest_articles(background_tasks)
    return {"status": "success", "count": len(articles), "articles": articles}

async def generate_upsc_enrichment(content: str) -> Dict[str, str]:
    if not groq_client: return {"upscSyllabus": "", "upscFacts": "", "upscMainsPrompt": ""}
    try:
        response = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a UPSC expert. Analyze the news for an aspirant. Provide: 1. Syllabus Map (e.g., GS-II: Governance), 2. 3 Key Prelims Facts, 3. A Mains-style thought prompt. Format as JSON: {\"syllabus\": \"...\", \"facts\": \"...\", \"mains\": \"...\"}"},
                {"role": "user", "content": content}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0.4
        )
        import json
        data = json.loads(response.choices[0].message.content)
        return {
            "upscSyllabus": data.get("syllabus", ""),
            "upscFacts": data.get("facts", ""),
            "upscMainsPrompt": data.get("mains", "")
        }
    except Exception:
        return {"upscSyllabus": "General Studies", "upscFacts": "Check source for details", "upscMainsPrompt": "How does this affect India?"}

@router.post("/process")
async def process_single_article(article_data: Dict[str, Any] = Body(None), role: str = "Student"):
    """Takes raw article content, summarizes it, and generates insights + UPSC enrichment if needed."""
    if not article_data:
        # Auto-select the top story if no article is provided
        articles = await get_latest_articles()
        if not articles:
            return {"error": "No articles found in news feed to auto-process."}
        article_data = articles[0]
        article_data["is_auto_selected"] = True

    content = str(article_data.get("content", article_data.get("summary_raw", "")))
    
    tasks = [summarize_article(content), generate_insights(content, role)]
    if role == "Student":
        tasks.append(generate_upsc_enrichment(content))
    
    results = await asyncio.gather(*tasks)
    summary = str(results[0])
    insight = str(results[1])
    upsc = results[2] if len(results) > 2 else None
    
    response = {
        "title": article_data.get("title"),
        "source": article_data.get("source"),
        "ai_summary": summary,
        "why_it_matters": insight,
        "role_context": role
    }
    
    if upsc and isinstance(upsc, dict):
        response.update(upsc)
        
    return response



# --- RapidAPI Current Affairs Endpoints ---
import httpx

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
RAPIDAPI_HOST = 'current-affairs-of-india.p.rapidapi.com'

async def fetch_rapidapi(endpoint: str):
    if not RAPIDAPI_KEY:
        raise HTTPException(status_code=500, detail="RAPIDAPI_KEY not configured in .env")
    url = f"https://{RAPIDAPI_HOST}/{endpoint}"
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            if endpoint == 'history-of-today' and isinstance(data, list):
                for item in data:
                    if 'date' in item: item['date'] = item['date'].strip()
                    if 'description' in item: item['description'] = item['description'].strip()
            return data
        except httpx.HTTPStatusError as e:
             raise HTTPException(status_code=e.response.status_code, detail=f"RapidAPI Error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RapidAPI Connection Error: {str(e)}")

@router.get("/current-affairs/international-today")
async def get_international_today():
    return await fetch_rapidapi('international-today')

@router.get("/current-affairs/recent")
async def get_recent():
    return await fetch_rapidapi('recent')

@router.get("/current-affairs/today-quiz")
async def get_today_quiz():
    return await fetch_rapidapi('today-quiz')

@router.get("/current-affairs/history-of-today")
async def get_history_of_today():
    return await fetch_rapidapi('history-of-today')
