import os
from dotenv import load_dotenv

# Explicitly load .env from the backend root directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(env_path)

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-index")
    MONGO_URI = os.getenv("MONGO_URI")

settings = Settings()

# Debug print to verify loading (do not print actual secrets in production logs ideally, but helpful here)
if not settings.MONGO_URI:
    print(f"WARNING: MONGO_URI not found in .env at {env_path}")
else:
    print(f"SUCCESS: MONGO_URI loaded successfully.")
