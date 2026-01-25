from langchain_community.document_loaders import PyPDFLoader
import os

data_path = os.path.join("backend", "data")
files = [f for f in os.listdir(data_path) if f.endswith('.pdf')]

print(f"Found PDF files: {files}")

for f in files:
    path = os.path.join(data_path, f)
    try:
        loader = PyPDFLoader(path)
        pages = loader.load()
        text_len = sum(len(p.page_content) for p in pages)
        print(f"File: {f} | Pages: {len(pages)} | Total Text Length: {text_len}")
        if text_len < 100:
            print("WARNING: Very little text found. Is this a scanned image?")
            print(f"Content preview: {[p.page_content for p in pages]}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
