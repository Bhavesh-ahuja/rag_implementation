# Free Tier Deployment Guide

This guide will help you deploy the RAG application for **FREE** using **Render** (Backend) and **Vercel** (Frontend).
By following this guide, you will have a live application with persistent memory (Chat History & PDF Vectors) that doesn't get deleted when the app sleeps.

## Prerequisites

1.  **GitHub Account**: You need to push this code to a GitHub repository.
2.  **Google Gemini API Key**: [Get it here](https://aistudio.google.com/app/apikey)
3.  **Pinecone Account** (for Vector DB): [Sign up here](https://app.pinecone.io/)
4.  **MongoDB Atlas Account** (for Chat History): [Sign up here](https://www.mongodb.com/cloud/atlas/register)
5.  **Render Account**: [Sign up here](https://render.com/)
6.  **Vercel Account**: [Sign up here](https://vercel.com/)

---

## Step 1: Get Your API Keys

### 1. Pinecone (Vector Database)
1.  Log in to Pinecone.
2.  Create an **Index**:
    *   **Name**: `rag-index`
    *   **Dimensions**: `768` (Important! This matches `models/text-embedding-004`)
    *   **Metric**: `cosine`
3.  Go to **API Keys** and copy your Key.

### 2. MongoDB Atlas (Chat History)
1.  Log in to MongoDB Atlas.
2.  Create a **Cluster** (Free Tier M0).
3.  Go to **Database Access** -> Create a User (e.g., `admin`) + Password.
4.  Go to **Network Access** -> Add IP Address -> `Allow Access from Anywhere (0.0.0.0/0)`.
5.  Click **Connect** -> **Drivers**.
    *   **Driver**: Select `Python`.
    *   **Version**: Select `3.6 or later`.
6.  Copy the connection string.
    *   **Action**: Paste it into a temporary notepad.
    *   **Replace**: Find the text `<password>` inside the string. Delete it (including the `<` and `>`) and type your actual password.
    *   *Example*: Change `mongodb+srv://admin:<password>@...` to `mongodb+srv://admin:MySecurePass123@...`

---

## Step 2: Push Code to GitHub
1.  Create a new Repository on GitHub.
2.  Run these commands in your project folder:
    ```bash
    git init
    git add .
    git commit -m "Initial commit for RAG App"
    git branch -M main
    git remote add origin <YOUR_REPO_URL>
    git push -u origin main
    ```

---

## Step 3: Deploy Backend (Render)
1.  Go to [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub Repository.
4.  **Settings**:
    *   **Name**: `rag-backend`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r backend/requirements.txt`
    *   **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables** (Click "Add Environment Variable"):
    *   `GOOGLE_API_KEY`: Paste your Gemini Key.
    *   `PINECONE_API_KEY`: Paste your Pinecone Key.
    *   `PINECONE_INDEX_NAME`: `rag-index`
    *   `MONGO_URI`: Paste your MongoDB Connection String.
6.  Click **Deploy Web Service**.
7.  Wait for it to confirm "Live". **Copy the Backend URL** (e.g., `https://rag-backend.onrender.com`).

---

## Step 4: Deploy Frontend (Vercel)
1.  Go to [Vercel Dashboard](https://vercel.com/dashboard).
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub Repository.
4.  **Configure Project**:
    *   **Framework Preset**: Vite
    *   **Root Directory**: Click "Edit" and select `frontend`.
5.  **Environment Variables**:
    *   Click to expand.
    *   Key: `VITE_API_URL`
    *   Value: Your Render Backend URL (e.g., `https://rag-backend.onrender.com`) - **No trailing slash**.
6.  Click **Deploy**.

---

## Done!
Your app is now live.
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.onrender.com/docs` (Swagger UI)

**Note**: Since Render Free Tier spins down after inactivity, the first request might take ~50 seconds to verify/wake up. Subsequent requests will be fast.
