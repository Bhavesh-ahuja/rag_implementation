import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-index")
    MONGO_URI = os.getenv("MONGO_URI")

settings = Settings()
