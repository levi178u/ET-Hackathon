from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()
from api.db import prisma, connect_db, disconnect_db
from api.user import router as user_router
from api.news import router as news_router
from api.assistant import router as assistant_router
from api.payment import router as payment_router
from api.auth import router as auth_router

app = FastAPI(title="Squirrel API")

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(news_router)
app.include_router(assistant_router)
app.include_router(payment_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Squirrel API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

