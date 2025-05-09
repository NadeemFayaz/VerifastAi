# vector_db/store_in_qdrant.py

import json
import sys
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import ResponseHandlingException

try:
    # Connect to Qdrant (local)
    client = QdrantClient(host="localhost", port=6333)

    collection_name = "news_articles"

    # Check if collection exists and create it if it doesn't
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    
    # Create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)  # 384 for MiniLM
    )

    # Load embeddings
    with open("../embeddings/article_embeddings.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    # Prepare points
    points = [
        PointStruct(
            id=i,
            vector=article["embedding"],
            payload={
                "title": article["title"],
                "text": article["text"],
                "url": article["url"]
            }
        )
        for i, article in enumerate(articles)
    ]

    # Upload points
    client.upsert(collection_name=collection_name, points=points)

    print(f"✅ Uploaded {len(points)} articles to Qdrant collection '{collection_name}'")
    
except ResponseHandlingException as e:
    print("Error: Could not connect to Qdrant server.")
    print("Please ensure Qdrant server is running at localhost:6333")
    print("If using Docker, start Qdrant with:")
    print("    docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
    print(f"Original error: {str(e)}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1)