import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings

def ingest_documents():
    # Use absolute path relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # app/rag/ingestion.py -> .../backend
    project_root = os.path.dirname(os.path.dirname(current_dir))
    data_path = os.path.join(project_root, "data")
    
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"Created data directory at {data_path}. Please add files.")
        return

    # Loaders for PDF and Text
    loaders = [
        DirectoryLoader(data_path, glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(data_path, glob="**/*.txt", loader_cls=TextLoader),
        DirectoryLoader(data_path, glob="**/*.md", loader_cls=TextLoader),
    ]

    documents = []
    for loader in loaders:
        try:
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading documents: {e}")

    if not documents:
        print("No documents found in data directory.")
        return

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(splits)} chunks.")

    # Embed and Store
    if splits:
        vectorstore = Chroma(
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)
        )
        vectorstore.add_documents(documents=splits)
        # vectorstore.persist() # Chroma 0.4+ persists automatically or uses different method, usually auto-persist
        print("Documents ingested and stored in ChromaDB.")

if __name__ == "__main__":
    ingest_documents()
