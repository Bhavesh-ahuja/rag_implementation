# 🧠 End-to-End RAG AI Agent with Memory

![Status](https://img.shields.io/badge/Status-Production_Ready-success) ![Stack](https://img.shields.io/badge/Stack-FastAPI_React_LangChain-blue) ![Model](https://img.shields.io/badge/AI-Gemini_Flash-orange)

A conversational AI agent capable of **Retrieval-Augmented Generation (RAG)** using your own documents. Built with a focus on accuracy, architecture, and user experience.

---

## 🚀 Key Features

*   **Advanced RAG Pipeline**:
    *   **MMR (Maximal Marginal Relevance)** Retrieval: Ensures diverse context chunks to prevent repetitive answers.
    *   **History Awareness**: Understands follow-up questions (e.g., *"Summarize it"*) by contextualizing them with previous chat history.
    *   **Source Citation**: Every answer cites the specific document sources used.
*   **Memory Management**:
    *   Maintains conversation context across multiple turns using `RunnableWithMessageHistory`.
    *   Session-based isolation (supports multiple users).
*   **Vector Database**:
    *   **ChromaDB**: Local, persistent vector storage.
    *   **Automated Ingestion**: Auto-activates when new files are uploaded.
*   **Robust Frontend**:
    *   **Modern UI**: Built with React & Tailwind CSS.
    *   **Real-time Updates**: "Active Documents" list updates instantly upon upload/delete.
    *   **Markdown Rendering**: Renders AI responses with bolding, lists, and code blocks.
*   **Smart Validation**:
    *   Auto-detects and rejects scanned (image-only) PDFs to prevent silent failures.
    *   Handles rate limits gracefully.

---

## 🛠️ Tech Stack

### **Backend** (Python)
*   **FastAPI**: High-performance async web framework.
*   **LangChain**: Orchestration framework for RAG chains.
*   **Google Gemini**: `gemini-flash-latest` (Optimized for speed/cost).
*   **ChromaDB**: For vector embeddings storage.
*   **Pydantic**: Data validation.

### **Frontend** (JavaScript)
*   **React 19**: Component-based UI.
*   **Vite**: Next-generation frontend tooling.
*   **Tailwind CSS**: Utility-first styling.
*   **React Markdown**: Rich text display.

---

## 🏗️ Architecture

```mermaid
graph LR
    User[User Question] --> Frontend
    Frontend -->|POST /chat| Backend
    Backend -->|Rewrite Query| HistoryAware{Contextualizer}
    HistoryAware -->|Search| ChromaDB[(Vector Store)]
    ChromaDB -->|Retrieve Top K (MMR)| RAG_Chain
    RAG_Chain -->|Context + Query| LLM[Gemini Flash]
    LLM -->|Answer w/ Sources| Backend
    Backend -->|JSON Response| Frontend
```

---

## 💻 Local Setup & Installation

### Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)
*   Google API Key

### 1. Clone the Repository
```bash
git clone https://github.com/Bhavesh-ahuja/rag_implementation.git
cd rag_implementation
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```
**Configure Environment**:
Create a `.env` file in `backend/`:
```env
GOOGLE_API_KEY=your_google_api_key_here
```
Run the server:
```bash
python -m uvicorn app.main:app --reload
```

### 3. Frontend Setup
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Access the app at `http://localhost:5173`.

---

## 🌐 Deployment (Live)

### Backend (Render / Railway)
1.  Push code to GitHub.
2.  Connect repository to Render.
3.  Set Build Command: `pip install -r requirements.txt`
4.  Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5.  Add Environment Variable: `GOOGLE_API_KEY`.

### Frontend (Vercel)
1.  Import repository to Vercel.
2.  Set Root Directory: `frontend`.
3.  Add Environment Variable:
    *   `VITE_API_URL`: URL of your deployed backend (e.g., `https://my-rag-backend.onrender.com`).
4.  Deploy!

---

## 🔬 Optimization Highlights

1.  **Why MMR?**
    Standard similarity search often returns 4 nearly identical chunks. By enabling **Maximal Marginal Relevance** (`lambda_mult=0.7`), we force the retriever to select diverse information, providing a much richer answer.

2.  **Context Window Upgrade**:
    We increased `k` (retrieved docs) from 4 to **10**, leveraging Gemini's large context window to reduce hallucinations and "I don't know" responses.

3.  **Structured Output**:
    The system prompt strictly enforces Markdown formatting (Headers, Bullets) to ensure the AI acts as a professional consultant rather than a generic chatbot.

---

## 🛡️ License
MIT
