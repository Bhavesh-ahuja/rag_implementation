from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from app.core.config import settings

# In-memory storage for session history
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def get_rag_chain():
    # Initialize Vector Store Retriever
    vectorstore = Chroma(
        persist_directory=settings.CHROMA_DB_DIR,
        embedding_function=GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)
    )
    # Use MMR (Maximal Marginal Relevance) to diversify results
    # fetch_k=20 means fetch 20 candidates, then select top 10 most diverse.
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 20, "lambda_mult": 0.7}
    )

    # LLM
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
        "\n- **Structure**: Use Markdown headers (###), bullet points, and bold text to organize your answer."
        "\n- **Detail**: Explain concepts thoroughly using the retrieved information."
        "\n- **Objectivity**: Stick strictly to the context. If the answer is missing, say 'I cannot find the relevant information in the documents.'"
        "\n- **Citations**: If possible, reference specific sections from the context."
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
