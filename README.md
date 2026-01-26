# 🧠 End-to-End RAG AI Agent with Memory

![Status](https://img.shields.io/badge/Status-Production_Ready-success) ![Stack](https://img.shields.io/badge/Stack-FastAPI_React_LangChain-blue) ![Model](https://img.shields.io/badge/AI-Gemini_1.5_Flash-orange)

A secure, production-ready AI agent capable of **Retrieval-Augmented Generation (RAG)**. Built for accuracy, security, and scalability.

---

## 🚀 Key Features

*   **Advanced RAG Pipeline**:
    *   **Model**: Powered by `gemini-1.5-flash` for high speed and reasoning.
    *   **MMR Retrieval**: `fetch_k=50` ensures broad diversity in context selection.
    *   **Chain-of-Thought**: System prompt enforces step-by-step reasoning before answering.
*   **Persistent Memory**:
    *   **SQLite Storage**: Chat history is saved locally (`backend/data/chat_history.db`) and survives server restarts.
    *   **Session Isolation**: Supports multiple concurrent users.
*   **Security Hardened**:
    *   **Path Traversal Protection**: Filenames are sanitized to prevent filesystem attacks.
    *   **Strict Validation**: Only accepts `.pdf`, `.txt`, and `.md` files.
    *   **Concurrency Safe**: Thread-safe file uploads using `asyncio.Lock`.
*   **Robust Frontend**:
    *   **Real-time Feedback**: Loading states for uploads/deletes.
    *   **Error Handling**: Graceful degradation when APIs fail.

---

## 🛠️ Tech Stack

### **Backend** (Python)
*   **FastAPI**: Async web framework.
*   **LangChain**: Orchestration & Memory (SQLChatMessageHistory).
*   **ChromaDB**: Local vector storage.
*   **SQLite**: Chat history persistence.

### **Frontend** (JavaScript)
*   **React 19**: Component-based UI.
*   **Vite**: Fast tooling.
*   **Tailwind CSS**: Modern styling.

---

## 💻 Local Setup

### Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)
*   Google API Key

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```
Create `.env`:
```env
GOOGLE_API_KEY=your_key
```
Run:
```bash
python -m uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```
Create `.env.local` (for local development):
```env
VITE_API_URL=http://localhost:8000
```
Run:
```bash
npm run dev
```

---

## 🌐 Deployment (Render + Vercel)

### Backend (Render)
1.  **Build Command**: `pip install -r requirements.txt`
2.  **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
3.  **Env**: `GOOGLE_API_KEY`

### Frontend (Vercel)
1.  **Env**: `VITE_API_URL` (Your Render Backend URL)

---

## 🛡️ License
MIT
