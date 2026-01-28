import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(r"D:\Projects\Rag_Implementation\backend\.env")
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = "models/gemini-embedding-001"
text = "Hello world"

try:
    result = genai.embed_content(
        model=model_name,
        content=text,
        task_type="retrieval_document"
    )
    embedding = result['embedding']
    print(f"Model: {model_name}")
    print(f"Dimension: {len(embedding)}")
except Exception as e:
    print(f"Error: {e}")
