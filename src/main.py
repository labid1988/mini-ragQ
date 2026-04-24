from fastapi import FastAPI
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv



load_dotenv(".env")

from routes.base import base_router  # ✅ importe l'objet router directement
from routes.data import data_router

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    setting = get_settings()

    app.mongo_conn = AsyncIOMotorClient(setting.MONGODB_URL)
    app.db_client= app.mongo_conn[setting.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(base_router)
app.include_router(data_router)