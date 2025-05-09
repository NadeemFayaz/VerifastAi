# embeddings/generate_embeddings.py

import json
from sentence_transformers import SentenceTransformer
import os

# Create embeddings directory if it doesn't exist
os.makedirs("../embeddings", exist_ok=True)

# Load articles
with open("../data/data/articles_from_sitemap.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Load the sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Extract texts and titles
texts = [article["text"] for article in articles]
titles = [article["title"] for article in articles]

# Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# Prepare data to save
vector_data = [
    {
        "title": titles[i],
        "embedding": embeddings[i].tolist(),  # Convert NumPy array to list
        "text": texts[i],
        "url": articles[i]["url"]
    }
    for i in range(len(texts))
]

# Save to JSON
output_dir = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(output_dir, "article_embeddings.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(vector_data, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(vector_data)} embeddings to {output_path}")