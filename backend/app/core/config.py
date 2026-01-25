import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

settings = Settings()
