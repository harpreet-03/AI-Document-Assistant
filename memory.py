# memory.py

import faiss
import numpy as np
import pickle
import os
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

# Memory persistence
MEMORY_FILE = "memory_store.pkl"

def save_memory():
    """Save memory to disk"""
    try:
        if len(stored_chunks) == 0:
            return  # Nothing to save
            
        with open(MEMORY_FILE, 'wb') as f:
            pickle.dump({
                'chunks': stored_chunks,
                'metadata': metadata,
                'index': faiss.serialize_index(index)
            }, f)
    except Exception as e:
        st.error(f"Failed to save memory: {e}")

def load_memory():
    """Load memory from disk"""
    global index, stored_chunks, metadata
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'rb') as f:
                data = pickle.load(f)
                stored_chunks.clear()
                metadata.clear()
                stored_chunks.extend(data['chunks'])
                metadata.extend(data['metadata'])
                index = faiss.deserialize_index(data['index'])
                return True
        return False
    except Exception as e:
        st.error(f"Failed to load memory: {e}")
        return False

# Load memory on module import
load_memory()

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
        
        # Save to disk
        save_memory()
        
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
        
        # Get results with relevance scores
        results = []
        for i, distance in zip(indices[0], distances[0]):
            if i < len(stored_chunks) and i >= 0:  # Valid index check
                results.append({
                    'text': stored_chunks[i],
                    'score': float(distance),
                    'metadata': metadata[i] if i < len(metadata) else {}
                })
        
        # Return just the text for backward compatibility
        return [result['text'] for result in results]
        
    except Exception as e:
        st.error(f"Error searching memory: {e}")
        return []

def search_memory_with_scores(query: str, top_k: int = 3):
    """
    Search for relevant chunks with similarity scores and metadata.
    
    Args:
        query: Search query
        top_k: Number of top results to return
    
    Returns:
        List of dictionaries with text, score, and metadata
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
        
        # Get results with relevance scores
        results = []
        for i, distance in zip(indices[0], distances[0]):
            if i < len(stored_chunks) and i >= 0:  # Valid index check
                results.append({
                    'text': stored_chunks[i],
                    'score': float(distance),
                    'metadata': metadata[i] if i < len(metadata) else {},
                    'relevance': max(0, 1 - distance / 2)  # Convert distance to relevance score
                })
        
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
    unique_docs = set(meta.get("name", "Unknown") for meta in metadata)
    return {
        "total_chunks": len(stored_chunks),
        "total_documents": len(unique_docs),
        "index_size": index.ntotal if hasattr(index, 'ntotal') else 0,
        "document_names": list(unique_docs),
        "memory_file_exists": os.path.exists(MEMORY_FILE)
    }

def clear_memory():
    """
    Clear all stored memory and remove the persistence file.
    """
    global index, stored_chunks, metadata
    index = faiss.IndexFlatL2(dimension)
    stored_chunks.clear()
    metadata.clear()
    
    # Remove the persistence file
    try:
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
    except Exception as e:
        st.error(f"Failed to remove memory file: {e}")

def get_document_chunks(doc_name: str):
    """
    Get all chunks for a specific document.
    
    Args:
        doc_name: Name of the document
    
    Returns:
        List of chunks from the specified document
    """
    doc_chunks = []
    for i, meta in enumerate(metadata):
        if meta.get("name") == doc_name and i < len(stored_chunks):
            doc_chunks.append(stored_chunks[i])
    return doc_chunks

def remove_document(doc_name: str):
    """
    Remove all chunks from a specific document.
    
    Args:
        doc_name: Name of the document to remove
    
    Returns:
        Boolean indicating success
    """
    try:
        global index, stored_chunks, metadata
        
        # Find indices to remove
        indices_to_remove = []
        for i, meta in enumerate(metadata):
            if meta.get("name") == doc_name:
                indices_to_remove.append(i)
        
        if not indices_to_remove:
            return False  # Document not found
        
        # Remove in reverse order to maintain indices
        for i in reversed(indices_to_remove):
            if i < len(stored_chunks):
                stored_chunks.pop(i)
            if i < len(metadata):
                metadata.pop(i)
        
        # Rebuild FAISS index (this is expensive but necessary)
        if stored_chunks:
            embedding_model = load_embedding_model()
            vectors = embedding_model.encode(stored_chunks)
            if len(vectors.shape) == 1:
                vectors = vectors.reshape(1, -1)
            
            # Create new index
            index = faiss.IndexFlatL2(dimension)
            index.add(np.array(vectors, dtype=np.float32))
        else:
            # Empty index
            index = faiss.IndexFlatL2(dimension)
        
        # Save updated memory
        save_memory()
        return True
        
    except Exception as e:
        st.error(f"Error removing document: {e}")
        return False

def get_all_documents():
    """
    Get all documents stored in memory with their metadata.
    
    Returns:
        List of dictionaries containing document information
    """
    documents = {}
    
    # Group chunks by document name
    for i, meta in enumerate(metadata):
        doc_name = meta.get("name", "Unknown")
        doc_type = meta.get("type", "General")
        
        if doc_name not in documents:
            documents[doc_name] = {
                'name': doc_name,
                'type': doc_type,
                'chunk_count': 0,
                'total_text_length': 0,
                'first_chunk_preview': ""
            }
        
        documents[doc_name]['chunk_count'] += 1
        
        # Add text length if we have the chunk
        if i < len(stored_chunks):
            chunk_text = stored_chunks[i]
            documents[doc_name]['total_text_length'] += len(chunk_text)
            
            # Store preview of first chunk
            if documents[doc_name]['chunk_count'] == 1:
                documents[doc_name]['first_chunk_preview'] = chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
    
    return list(documents.values())