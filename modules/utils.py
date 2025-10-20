import os
import numpy as np
from tavily import TavilyClient

def calculate_context_similarity(query: str, context: str, embeddings) -> float:
    """Calculate similarity between query and retrieved context."""
    if not context or not query:
        return 0.0
    
    try:
        query_embedding = embeddings.embed_query(query)
        context_embedding = embeddings.embed_query(context)
        
        query_vec = np.array(query_embedding)
        context_vec = np.array(context_embedding)
        
        similarity = np.dot(query_vec, context_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(context_vec))
        
        return float(similarity)
    except Exception as e:
        print(f"[!] Error calculating similarity: {e}")
        return 0.0

def search_with_tavily(query: str, max_results: int = 3) -> str:
    """Search using Tavily API and return aggregated content."""
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        client = TavilyClient(api_key=tavily_api_key)
        
        print(f"[*] Searching with Tavily for: '{query}'...")
        response = client.search(query=query, max_results=max_results)
        
        content_parts = []
        for idx, result in enumerate(response.get('results', []), 1):
            content_parts.append(f"Source {idx}: {result.get('title', '')}\n{result.get('content', '')}\nURL: {result.get('url', '')}\n")
        
        aggregated_content = "\n\n".join(content_parts)
        print(f"[+] Retrieved {len(response.get('results', []))} results from Tavily")
        return aggregated_content
    
    except Exception as e:
        print(f"[!] Error searching with Tavily: {e}")
        return ""