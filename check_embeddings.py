import google.generativeai as genai
import os
from dotenv import load_dotenv

# Try loading env from backend
load_dotenv(r"D:\Projects\Rag_Implementation\backend\.env")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Could not find GOOGLE_API_KEY")
    exit(1)

genai.configure(api_key=api_key)

print(f"Checking models with key: {api_key[:5]}...")

try:
    print("Listing embedding models:")
    found = False
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            found = True
    if not found:
        print("No embedding models found.")
except Exception as e:
    print(f"Error listing models: {e}")
