import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from dotenv import load_dotenv

async def seed():
    load_dotenv()
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return
        
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(db_url)
    db = client.get_database("newsnavigator")
    
    print(f"Connected to database: {db.name}")
    
    # Insert User
    await db.User.delete_many({})
    user = {
        "email": "test@example.com",
        "name": "ET Hackathon Judge",
        "interests": ["Technology", "Markets", "Startups"],
        "role": "Founder",
        "isPremium": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    await db.User.insert_one(user)
    print("User seeded.")
    
    # Insert Article
    await db.Article.delete_many({})
    article = {
        "title": "Three Indian Unicorns File for IPO in Same Week",
        "source": "Economic Times",
        "url": "https://economictimes.indiatimes.com",
        "contentRaw": "Zepto, PhysicsWallah, and Ather Energy simultaneously filed draft papers with SEBI, signaling a renewed confidence in public markets after a cautious 2025.",
        "contentSummary": "Three major tech unicorns file for IPO.",
        "category": "Startups",
        "publishedAt": datetime.utcnow()
    }
    result = await db.Article.insert_one(article)
    
    # Insert Quiz
    await db.Quiz.delete_many({})
    quiz = {
        "articleId": str(result.inserted_id),
        "questions": [
            {
                "question": "Which of these companies filed for IPO recently?",
                "options": ["Swiggy", "Zepto", "Zomato", "Flipkart"],
                "answer": 1,
                "explanation": "Zepto filed draft papers with SEBI along with PhysicsWallah and Ather Energy."
            }
        ],
        "createdAt": datetime.utcnow()
    }
    await db.Quiz.insert_one(quiz)
    print("Article and Quiz seeded.")
    print("Data is now ready! You can view it by running `npx prisma studio` in the backend folder.")

if __name__ == "__main__":
    asyncio.run(seed())
