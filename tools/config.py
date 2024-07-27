from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote
import os


dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)


CONNECTION_URI = os.getenv("MONGO_CONNECTION")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_REFRESH = os.getenv("SECRET_REFRESH")
ALGORITHM = os.getenv("ALGORITHM")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = quote(os.getenv("REDIS_PASSWORD"))
NEXUS_USERNAME = os.getenv("NEXUS_USERNAME")
NEXUS_PASSWORD = os.getenv("NEXUS_PASSWORD")
NEXUS_URL = os.getenv("NEXUS_URL")
AES_KEY = os.getenv("AES_KEY")
