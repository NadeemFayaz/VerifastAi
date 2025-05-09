# 📰 RAG-Powered News Chatbot

A full-stack chatbot that answers questions over news articles using Retrieval-Augmented Generation (RAG) with Qdrant and Gemini.

---

## 🚀 Features

- Ingests ~50 news articles from Reuters sitemap
- Embeds text using SentenceTransformers
- Stores embeddings in Qdrant
- FastAPI backend with Gemini API for generative answers
- React + Tailwind frontend with session chat
- Redis for chat history and session management

---

## 🧰 Tech Stack

| Layer        | Technology                         |
|--------------|------------------------------------|
| Embedding    | SentenceTransformers (MiniLM)      |
| Vector DB    | Qdrant                             |
| LLM          | Google Gemini API                  |
| Backend      | FastAPI (Python)                   |
| Frontend     | React + Tailwind CSS               |
| Sessions     | Redis                              |
| Optional DB  | PostgreSQL / MySQL (not required)  |

---

## 🛠️ Setup Instructions

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd <project-directory>
2. Set up environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
3. Run services (Qdrant + Redis)
bash
Copy
Edit
docker-compose up
4. Fetch and embed articles
bash
Copy
Edit
python data/fetch_from_reuters_sitemap.py
python embeddings/generate_embeddings.py
python vector_db/store_in_qdrant.py
5. Start backend (FastAPI)
bash
Copy
Edit
uvicorn backend.main:app --reload
6. Start frontend
bash
Copy
Edit
cd frontend
npm install
npm start
🔐 .env Configuration (in backend/.env)
env
Copy
Edit
REDIS_URL=redis://localhost:6379
VECTOR_DB_URL=http://localhost:6333
GEMINI_API_KEY=your_google_gemini_key_here