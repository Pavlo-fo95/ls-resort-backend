import os
print("CWD:", os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import contact, services, reviews, search
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

openapi_tags = [
    {"name": "contact", "description": "Контактні повідомлення"},
    {"name": "services", "description": "Послуги"},
    {"name": "reviews", "description": "Відгуки"},
    {"name": "auth", "description": "Авторизація"},
    {"name": "admin", "description": "Адмінка"},
    {"name": "search", "description": "Пошук з підказками та рекомендації"},
]

app = FastAPI(
    title="LS Resort Backend",
    lifespan=lifespan,
    swagger_ui_parameters={
        "operationsSorter": "alpha",  # сортирует операции
        "tagsSorter": "alpha"         # сортирует теги
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contact.router)
app.include_router(services.router)
app.include_router(reviews.router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(search.router)

@app.get("/")
async def root():
    return {"status": "ok", "service": "LS Resort Backend"}

