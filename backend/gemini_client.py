import os
from typing import List, Dict, Any

# Define a fallback function for when API is unavailable
def simple_local_response(query: str, passages: List[Dict[str, Any]]) -> str:
    """Generate a simple response locally when the API is unavailable"""
    # Extract relevant passages based on basic keyword matching
    query_terms = set(query.lower().split())
    
    relevant_passages = []
    for p in passages:
        text = p['text'].lower()
        title = p['title'].lower()
        # Check if any query term appears in the text or title
        if any(term in text or term in title for term in query_terms):
            relevant_passages.append(p)
    
    if not relevant_passages:
        relevant_passages = passages[:2]  # Take top 2 if no direct matches
    
    response = f"Based on the available information about '{query}':\n\n"
    
    for p in relevant_passages:
        response += f"From {p['title']}: {p['text'][:150]}...\n\n"
    
    response += "\nNote: This is a simplified response as the AI service is currently unavailable."
    return response

def generate_gemini_response(query: str, passages: List[Dict[str, Any]]) -> str:
    """
    Generate a response using Google's Gemini API based on the query and retrieved passages.
    Falls back to local processing if API is unavailable.
    """
    try:
        # Try to import the Google AI package - if not installed, fall back to local method
        import google.generativeai as genai
        from google.api_core.exceptions import NotFound, ResourceExhausted
    except ImportError:
        # Package not installed
        return simple_local_response(query, passages) + "\n\nError: Google Generative AI package not installed. Run 'pip install google-generativeai'."

    # Set your API key - preferably from environment variable
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "test_key")
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Format context from passages
        context = "\n\n".join([
            f"Title: {p['title']}\nText: {p['text']}\nURL: {p['url']}"
            for p in passages
        ])
        
        # Create prompt with query and context
        prompt = f"""
        User Query: {query}
        
        Context Information:
        {context}
        
        Based on the above information, please provide a comprehensive answer to the user's query.
        If the information isn't sufficient, please indicate what's missing.
        Include relevant facts from the provided context.
        """
        
        # Try to use a model that's more likely to be available with free tier
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')  # Use standard model first
            response = model.generate_content(prompt)
            return response.text
        except (NotFound, ResourceExhausted) as e:
            # If rate limited or model not found, fall back to local method
            return simple_local_response(query, passages) + f"\n\nAPI Error: {str(e)}"
        
    except Exception as e:
        # Catch-all for other errors
        return simple_local_response(query, passages) + f"\n\nError: {str(e)}"