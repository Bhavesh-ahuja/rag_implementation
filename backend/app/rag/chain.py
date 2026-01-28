from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_mongodb import MongoDBChatMessageHistory
import os
from app.core.config import settings

def get_session_history(session_id: str):
    return MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=settings.MONGO_URI,
        database_name="rag_chat_history",
        collection_name="chat_sessions",
    )

def get_rag_chain():
    # Initialize Pinecone Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=settings.GOOGLE_API_KEY)
    
    vectorstore = PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings
    )
    
    # Use MMR (Maximal Marginal Relevance) to diversify results
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 12, "fetch_k": 50, "lambda_mult": 0.6}
    )

    # LLM - Using gemini-flash-latest (previously working alias)
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=settings.GOOGLE_API_KEY, temperature=0.3)

    # 1. Contextualize question (History Aware Retriever)
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # 2. Answer question (QA Chain)
    system_prompt = (
        "You are an expert AI consultant. Your goal is to provide deep, well-structured, and comprehensive answers based on the context."
        "\n\n"
        "Guidelines:"
        "\n- **Think Step-by-Step**: Before answering, briefly analyze the retrieved context to synthesize the best answer."
        "\n- **Structure**: Use Markdown headers (###), bullet points, and bold text to organize your answer. Do not use generic introductions."
        "\n- **Detail**: Explain concepts thoroughly using the retrieved information. Avoid superficial summaries."
        "\n- **Objectivity**: Stick strictly to the context. If the answer is missing, say 'I cannot find the relevant information in the documents.'"
        "\n- **Citations**: Reference specific sections or source documents from the context where possible."
        "\n\n"
        "Context:\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # 3. Retrieval Chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # 4. Wrap with Message History
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain
