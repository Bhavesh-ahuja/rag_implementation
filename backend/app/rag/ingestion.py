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

    # Check for empty content (scanned PDFs)
    total_content_length = sum(len(doc.page_content.strip()) for doc in documents)
    if total_content_length == 0:
        print("Error: Documents found but extracted text length is 0. Possible scanned/image-based PDF.")
        # We should probably raise an exception here so the API knows it failed
        raise ValueError("No text could be extracted from the document. It might be a scanned image.")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(splits)} chunks.")

    # Embed and Store
    if splits:
        # Initialize client to potentially clear existing collection
        # For simplicity in this demo, we will re-create the collection or we can check ids.
        # A simple robust way for "re-ingest all" is to delete the DB dir or use reset.
        # Here we will try to use the vectorstore object to delete collection if possible,
        # or just overwrite by re-initializing fresh if we nuked the dir in main.py (which we didn't).
        
        # Better approach: Initialize Chroma, delete collection, then add.
        vectorstore = Chroma(
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)
        )
        
        try:
            # Attempt to clear existing documents to avoid duplicates on re-ingestion
            # Chroma's delete_collection or getting all IDs and deleting them
            ids = vectorstore.get()["ids"]
            if ids:
                vectorstore.delete(ids)
                print(f"Deleted {len(ids)} existing documents to prevent duplication.")
        except Exception as e:
            print(f"Warning during cleanup: {e}")

        vectorstore.add_documents(documents=splits)
        print("Documents ingested and stored in ChromaDB.")

if __name__ == "__main__":
    ingest_documents()
