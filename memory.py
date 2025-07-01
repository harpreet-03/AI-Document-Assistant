# memory.py

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from parser import chunk_text
import streamlit as st

# Initialize the embedding model
@st.cache_resource
def load_embedding_model():
    """Load and cache the sentence transformer model"""
    return SentenceTransformer("all-MiniLM-L6-v2")

# Initialize global variables
dimension = 384
index = faiss.IndexFlatL2(dimension)
stored_chunks = []
metadata = []

def add_to_memory(text: str, doc_name: str = "Unknown", doc_type: str = "General"):
    """
    Add text to memory by chunking it and storing embeddings.
    
    Args:
        text: The text content to store
        doc_name: Name of the document
        doc_type: Type of document
    """
    try:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Load the embedding model
        embedding_model = load_embedding_model()
        
        # Chunk the text
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No chunks generated from text")
        
        # Generate embeddings
        vectors = embedding_model.encode(chunks)
        
        # Ensure vectors have the correct shape
        if len(vectors.shape) == 1:
            vectors = vectors.reshape(1, -1)
        
        # Add to FAISS index
        index.add(np.array(vectors, dtype=np.float32))
        
        # Store chunks and metadata
        stored_chunks.extend(chunks)
        metadata.extend([{"name": doc_name, "type": doc_type}] * len(chunks))
        
        return True
        
    except Exception as e:
        st.error(f"Error adding to memory: {e}")
        return False

def search_memory(query: str, top_k: int = 3):
    """
    Search for relevant chunks in memory based on the query.
    
    Args:
        query: Search query
        top_k: Number of top results to return
    
    Returns:
        List of relevant text chunks
    """
    try:
        if not query or not query.strip():
            return []
        
        if len(stored_chunks) == 0:
            return []
        
        # Load the embedding model
        embedding_model = load_embedding_model()
        
        # Generate query embedding
        query_vector = embedding_model.encode([query])
        
        # Ensure query vector has correct shape
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search in FAISS index
        distances, indices = index.search(np.array(query_vector, dtype=np.float32), min(top_k, len(stored_chunks)))
        
        # Get results
        results = []
        for i in indices[0]:
            if i < len(stored_chunks) and i >= 0:  # Valid index check
                results.append(stored_chunks[i])
        
        return results
        
    except Exception as e:
        st.error(f"Error searching memory: {e}")
        return []

def get_memory_stats():
    """
    Get statistics about the current memory state.
    
    Returns:
        Dictionary with memory statistics
    """
    return {
        "total_chunks": len(stored_chunks),
        "total_documents": len(set(meta["name"] for meta in metadata)),
        "index_size": index.ntotal if hasattr(index, 'ntotal') else 0
    }

def clear_memory():
    """
    Clear all stored memory.
    """
    global index, stored_chunks, metadata
    index = faiss.IndexFlatL2(dimension)
    stored_chunks.clear()
    metadata.clear()