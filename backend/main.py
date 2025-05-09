# backend/main.py

from fastapi import FastAPI, Query, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
# Import directly from the local module
from gemini_client import generate_gemini_response
import uuid
from session_manager import add_message, get_history, clear_session
from typing import Optional
from start import init_server

app = FastAPI()

init_server()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact origins instead of "*"
    allow_credentials=True,
    allow_methods=["*"],  # Or specify: ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],  # Or specify exact headers allowed
)

# Initialize clients with error handling
try:
    client = QdrantClient(host="localhost", port=6333)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    COLLECTION_NAME = "news_articles"
except Exception as e:
    print(f"Error initializing services: {e}")
    # Application will still start but endpoints will handle errors

@app.get("/search")
def search_articles(query: str = Query(..., min_length=3)):
    try:
        vector = model.encode(query).tolist()
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=5
        )

        passages = [
            {
                "title": hit.payload.get("title", "Untitled"),
                "url": hit.payload.get("url", ""),
                "text": hit.payload.get("text", "No content available"),
                "score": hit.score
            }
            for hit in search_result
        ]

        # Call Gemini with retrieved passages
        gemini_reply = generate_gemini_response(query, passages)

        return {
            "answer": gemini_reply,
            "sources": passages
        }
    except UnexpectedResponse as e:
        raise HTTPException(status_code=500, detail=f"Qdrant search failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/chat")
async def chat(
    query: str = Form(..., min_length=1), 
    session_id: Optional[str] = Form(None)
):
    try:
        if not session_id:
            session_id = str(uuid.uuid4())

        vector = model.encode(query).tolist()
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=5
        )
        
        passages = [
            {
                "title": hit.payload.get("title", "Untitled"),
                "url": hit.payload.get("url", ""),
                "text": hit.payload.get("text", "No content available"),
                "score": hit.score
            }
            for hit in search_result
        ]

        answer = generate_gemini_response(query, passages)

        # Store messages in Redis with error handling
        try:
            add_message(session_id, "user", query)
            add_message(session_id, "bot", answer)
        except Exception as e:
            print(f"Warning: Failed to save session data: {e}")
            # Continue even if Redis fails

        return {
            "session_id": session_id,
            "answer": answer,
            "sources": passages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/history/{session_id}")
def get_session_history(session_id: str):
    try:
        return get_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    try:
        clear_session(session_id)
        return {"message": f"Session {session_id} cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")