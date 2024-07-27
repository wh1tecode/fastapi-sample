from fastapi import FastAPI
from auth import router as auth_routers
from user import api
from models import database_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from beanie import init_beanie
from tools import config
from auth import set_default_group
import uvicorn


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # connect to mongo service
    client = AsyncIOMotorClient(config.CONNECTION_URI)
    # initialize
    await init_beanie(
        database=client.project,
        document_models=[
            database_beanie.User,
            database_beanie.Session,
            database_beanie.Route,
            database_beanie.Group,
        ],
    )
    client = MongoClient(config.CONNECTION_URI)
    await set_default_group(app)


app.include_router(auth_routers)

# routes user
app.include_router(api)


if __name__ == "__main__":
    uvicorn.run(app="application:app", host=config.HOST, port=config.PORT, workers=1)
