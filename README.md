# QGen-AI : An AI-based Q/A generator using RAG, Pinecone, and Tavily web search to create MCQs and short-answer questions from any document.
**QGenAI** is an intelligent quiz generator that instantly creates MCQs and short-answer questions from any document you upload (PDF, DOCX, etc.). It's built on a modern RAG (Retrieval-Augmented Generation) pipeline:

1. Documents are vectorized and stored in Pinecone.
2. When you write a query, LangChain retrieves the most relevant context from your files.
3. If that context is insufficient, Tavily automatically performs a real-time web search to find the missing information.
4. The final, enriched context is sent to Groq's high-speed LLMs to generate your questions, all presented in a sleek, responsive UI.
