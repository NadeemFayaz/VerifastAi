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
```

### 2. Prerequisites
- Docker installed and running (required for Qdrant vector database)
- Python 3.9+ with pip
- Node.js and npm

### 3. Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies (consider using a virtual environment)
pip install -r requirements.txt

# Start the backend server
# Note: This will run start.py which deploys Docker containers for Qdrant and Redis
uvicorn main:app --reload
```

### 4. Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 5. Accessing the Application
- Frontend: http://localhost:5173 (default Vite port)
- Backend API: http://localhost:8000 (default FastAPI port)
- API Documentation: http://localhost:8000/docs

---

## 📊 Project Structure

```
/
├── backend/                 # Python FastAPI backend
│   ├── data/                # News article data and scraping utilities
│   ├── embeddings/          # Text embedding generation
│   ├── vector_db/           # Qdrant vector database interface
│   ├── gemini_client.py     # Google Gemini API client
│   ├── main.py              # FastAPI application entry point
│   ├── session_manager.py   # Redis session management
│   └── start.py             # Docker container setup script
│
└── frontend/                # React frontend application
    ├── public/              # Static assets
    ├── src/                 # React source code
    ├── package.json         # Frontend dependencies
    └── vite.config.js       # Vite configuration
```

---

## 🗂️ Data Flow

1. **Data Collection**: News articles are scraped from Reuters sitemap
2. **Embedding Generation**: Text chunks are embedded using SentenceTransformers
3. **Vector Storage**: Embeddings are stored in Qdrant vector database
4. **User Interaction**: User queries are processed through the React frontend
5. **Query Processing**: Backend retrieves relevant context from Qdrant
6. **Response Generation**: Google Gemini API generates responses using retrieved context
7. **Session Management**: Redis maintains chat history and session state