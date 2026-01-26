import os
import time
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
        raise ValueError("No text could be extracted from the document. It might be a scanned image.")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(splits)} chunks.")

    # Embed and Store in Pinecone
    if splits:
        print("Initializing Pinecone VectorStore...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)
        
        # We assume the index already exists (User created it in Pinecone Console)
        # Verify index name
        index_name = settings.PINECONE_INDEX_NAME
        if not index_name:
             raise ValueError("PINECONE_INDEX_NAME not set in environment variables.")

        # Ingest
        # This will automatically compute embeddings and upsert
        PineconeVectorStore.from_documents(
            documents=splits,
            embedding=embeddings,
            index_name=index_name
        )
        print("Documents ingested and stored in Pinecone.")

if __name__ == "__main__":
    ingest_documents()
