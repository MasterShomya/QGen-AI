import os
import mimetypes
from typing import List
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader, TextLoader
)
from PIL import Image
import pytesseract
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

# --- Constants ---
EMBEDDING_MODEL_NAME = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536 # Dimension for text-embedding-3-small
MMR_K = 1
MMR_LAMBDA = 1

# --- Pinecone Constants ---
PINECONE_INDEX_NAME = "nlp-project" 


# --- Initialization ---
def get_embeddings() -> OpenAIEmbeddings:
    """Initialize and return the OpenAI embeddings."""
    return OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

def get_pinecone_client():
    """Initializes and returns a Pinecone client."""
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    return Pinecone(api_key=api_key)

def get_vectordb() -> PineconeVectorStore:
    """Initialize and return the Pinecone vector store."""
    pc = get_pinecone_client()
    embeddings = get_embeddings()

    if PINECONE_INDEX_NAME not in [index.name for index in pc.list_indexes()]:
        print(f"[!] Index '{PINECONE_INDEX_NAME}' not found. Creating it...")
        try:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"[+] Index '{PINECONE_INDEX_NAME}' created successfully.")
        except Exception as e:
            print(f"[!] Failed to create Pinecone index: {e}")
            raise
    else:
        print(f"[*] Found existing index '{PINECONE_INDEX_NAME}'.")

    return PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings
    )

def get_mmr_retriever(vectordb: PineconeVectorStore):
    """Create MMR retriever from vector database."""
    return vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={"k": MMR_K, "lambda_mult": MMR_LAMBDA}
    )

# --- Document Loading (UNCHANGED) ---
def load_document(file_path: str) -> List[Document]:
    # This function is unchanged
    mime_type, _ = mimetypes.guess_type(file_path)
    print(f"[*] Loading document: {file_path} (MIME type: {mime_type})")
    
    if mime_type == "application/pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
    elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        loader = UnstructuredPowerPointLoader(file_path)
        docs = loader.load()
    elif mime_type == "text/plain":
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
    elif mime_type in ["image/jpeg", "image/png"]:
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
            docs = [Document(page_content=text, metadata={"source": file_path})]
        except pytesseract.TesseractNotFoundError:
            print("[!] Tesseract Error: Tesseract OCR is not installed or not in PATH.")
            raise
        except Exception as e:
            print(f"[!] Image loading error: {e}")
            docs = []
    else:
        print(f"[!] Unsupported file type: {mime_type}. Skipping.")
        docs = []
    
    print(f"[+] Loaded {len(docs)} document chunks.")
    return docs

# --- Database Operations (UNCHANGED) ---
def upsert_documents(docs: List[Document]):
    """Upsert documents into the Pinecone database."""
    if not docs:
        print("[!] No documents to upsert.")
        return
        
    embeddings = get_embeddings()
    print(f"[*] Upserting {len(docs)} docs into Pinecone index '{PINECONE_INDEX_NAME}'...")
    
    PineconeVectorStore.from_documents(
        docs,
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME
    )
    print(f"[+] Upsert complete.")

# --- MODIFIED: clear_vectordb() ---
def clear_vectordb():
    """
    Clear the Pinecone vector database by deleting all vectors.
    Returns a tuple: (success, message, message_type)
    """
    try:
        pc = get_pinecone_client()
        
        if PINECONE_INDEX_NAME not in [index.name for index in pc.list_indexes()]:
            print(f"[!] Index '{PINECONE_INDEX_NAME}' does not exist. Nothing to clear.")
            return True, "Database index not found. Already clear.", "info"
            
        # --- MODIFICATION HERE ---
        # We no longer pass the host. The client finds it.
        index = pc.Index(PINECONE_INDEX_NAME)
        # --- END MODIFICATION ---

        stats = index.describe_index_stats()
        if stats.get('total_vector_count', 0) == 0:
            print("[!] No vectors found. Database is already empty.")
            return True, "Database is already empty.", "info"
        
        print(f"[*] Deleting all vectors from index '{PINECONE_INDEX_NAME}'...")
        index.delete(delete_all=True)
        print(f"[+] All vectors deleted.")
        return True, "Vector database cleared successfully.", "success"
            
    except Exception as e:
        print(f"[!] Error clearing Pinecone DB: {e}")
        return False, str(e), "error"