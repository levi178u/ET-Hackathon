# import asyncio
# from prisma import Prisma

# async def main():
#     db = Prisma()
#     await db.connect()

#     print("Seeding database...")

#     # Clear old data
#     await db.user.delete_many()
#     await db.article.delete_many()
#     await db.quiz.delete_many()

#     # Create dummy user
#     default_user = await db.user.create(
#         data={
#             "email": "test@example.com",
#             "name": "Demo User",
#             "interests": ["Technology", "Markets"],
#             "role": "Student",
#             "isPremium": False
#         }
#     )
#     print(f"Created user: {default_user.name}")

#     # Create an Article
#     article = await db.article.create(
#         data={
#             "title": "The government approved three new semiconductor fabrication units across Gujarat and Assam",
#             "source": "Economic Times",
#             "url": "https://economictimes.indiatimes.com",
#             "contentRaw": "The government approved three new semiconductor fabrication units across Gujarat and Assam, marking India's largest push toward chip self-reliance and reducing dependence on imports. This move is expected to generate thousands of jobs and boost local tech manufacturing ecosystems.",
#             "contentSummary": "Govt approves 3 new semiconductor foundries in Gujarat and Assam to boost local chip manufacturing.",
#             "category": "Technology",
#             "publishedAt": "2026-03-27T00:00:00Z"
#         }
#     )
#     print("Created article.")

#     # Create a Quiz for that article
#     await db.quiz.create(
#         data={
#             "articleId": article.id,
#             "questions": [
#                 {
#                     "question": "Which states will host the new semiconductor fabrication units?",
#                     "options": ["Maharashtra and Delhi", "Gujarat and Assam", "Karnataka and Tamil Nadu", "Punjab and Haryana"],
#                     "answer": 1,
#                     "explanation": "The units were approved for Gujarat and Assam."
#                 }
#             ]
#         }
#     )
#     print("Created quiz.")

#     await db.disconnect()
#     print("Database seeding completed successfully.")

# if __name__ == "__main__":
#     asyncio.run(main())
import asyncio
import json
from prisma import Prisma

async def main():
    db = Prisma()
    await db.connect()

    print("Seeding database...")

    # Clear old data (respect relations order)
    await db.quizscore.delete_many()
    await db.quiz.delete_many()
    await db.readinghistory.delete_many()
    await db.article.delete_many()
    await db.user.delete_many()

    # Create users
    users = []

    users.append(await db.user.create(
        data={
            "email": "test@example.com",
            "name": "Demo User",
            "interests": "technology,markets",
            "role": "Student",
            "isPremium": False
        }
    ))

    users.append(await db.user.create(
        data={
            "email": "investor@example.com",
            "name": "Investor User",
            "interests": "stocks,economy,markets",
            "role": "Investor",
            "isPremium": True
        }
    ))

    users.append(await db.user.create(
        data={
            "email": "dev@example.com",
            "name": "Developer User",
            "interests": "ai,backend,opensource",
            "role": "Developer",
            "isPremium": False
        }
    ))

    print(f"Created {len(users)} users")

    # Create articles
    articles = []

    articles.append(await db.article.create(
        data={
            "title": "Government approves semiconductor units in Gujarat and Assam",
            "content": "India approved three semiconductor fabrication units to boost self-reliance and reduce imports.",
            "summary": "India pushes semiconductor manufacturing with new fabs.",
            "source": "Economic Times",
            "url": "https://economictimes.indiatimes.com/semiconductor",
            "categories": "technology,economy",
            "publishedAt": "2026-03-27T00:00:00Z",
            "studentInsight": "Important for exam topics on industrial policy.",
            "investorInsight": "Semiconductor sector may see long-term growth.",
            "developerInsight": "New opportunities in chip and embedded systems.",
            "founderInsight": "Opens hardware startup ecosystem in India."
        }
    ))

    articles.append(await db.article.create(
        data={
            "title": "AI startups see record funding surge",
            "content": "AI startups are attracting record venture capital funding globally.",
            "summary": "AI funding boom continues.",
            "source": "YourStory",
            "url": "https://yourstory.com/ai-funding",
            "categories": "ai,startups",
            "publishedAt": "2026-03-26T00:00:00Z"
        }
    ))

    articles.append(await db.article.create(
        data={
            "title": "Stock markets hit record highs",
            "content": "Sensex and Nifty reached all-time highs driven by strong earnings.",
            "summary": "Markets surge to new highs.",
            "source": "MoneyControl",
            "url": "https://moneycontrol.com/markets",
            "categories": "markets,economy",
            "publishedAt": "2026-03-25T00:00:00Z"
        }
    ))

    print(f"Created {len(articles)} articles")

    # Create reading history
    for user in users:
        for article in articles:
            await db.readinghistory.create(
                data={
                    "userId": user.id,
                    "articleId": article.id,
                    "timeSpent": 120
                }
            )

    print("Reading history created")

    # Create quiz
    quiz_questions = [
        {
            "question": "Which states will host the semiconductor units?",
            "options": [
                "Maharashtra and Delhi",
                "Gujarat and Assam",
                "Karnataka and Tamil Nadu",
                "Punjab and Haryana"
            ],
            "answer": 1,
            "explanation": "The approved units are in Gujarat and Assam."
        }
    ]

    quiz = await db.quiz.create(
        data={
            "articleId": articles[0].id,
            "questions": json.dumps(quiz_questions)
        }
    )

    print("Quiz created")

    # Create quiz scores
    for user in users:
        await db.quizscore.create(
            data={
                "userId": user.id,
                "quizId": quiz.id,
                "score": 1,
                "total": 1
            }
        )

    print("Quiz scores created")

    await db.disconnect()
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())