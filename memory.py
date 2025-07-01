# memory.py

import faiss
import numpy as np
import pickle
import os
import hashlib
from sentence_transformers import SentenceTransformer
from parser import chunk_text
import streamlit as st

# Initialize the embedding model
@st.cache_resource
def load_embedding_model():
    """Load and cache the sentence transformer model"""
    return SentenceTransformer("all-MiniLM-L6-v2")

def get_user_session_id():
    """Generate a unique session ID for each user"""
    if 'user_session_id' not in st.session_state:
        # Create unique session ID based on session state
        session_info = str(st.session_state) + str(id(st.session_state))
        st.session_state.user_session_id = hashlib.md5(session_info.encode()).hexdigest()[:12]
    return st.session_state.user_session_id

def get_memory_file():
    """Get user-specific memory file"""
    session_id = get_user_session_id()
    return f"memory_store_{session_id}.pkl"

def initialize_user_memory():
    """Initialize memory for current user session"""
    if 'user_memory_initialized' not in st.session_state:
        st.session_state.dimension = 384
        st.session_state.index = faiss.IndexFlatL2(st.session_state.dimension)
        st.session_state.stored_chunks = []
        st.session_state.metadata = []
        st.session_state.user_memory_initialized = True
        load_memory()  # Load existing user data if any

def save_memory():
    """Save memory to disk for current user"""
    try:
        initialize_user_memory()
        if len(st.session_state.stored_chunks) == 0:
            return  # Nothing to save
            
        memory_file = get_memory_file()
        with open(memory_file, 'wb') as f:
            pickle.dump({
                'chunks': st.session_state.stored_chunks,
                'metadata': st.session_state.metadata,
                'index': faiss.serialize_index(st.session_state.index)
            }, f)
    except Exception as e:
        st.error(f"Failed to save memory: {e}")

def load_memory():
    """Load memory from disk for current user"""
    try:
        initialize_user_memory()
        memory_file = get_memory_file()
        if os.path.exists(memory_file):
            with open(memory_file, 'rb') as f:
                data = pickle.load(f)
                st.session_state.stored_chunks.clear()
                st.session_state.metadata.clear()
                st.session_state.stored_chunks.extend(data['chunks'])
                st.session_state.metadata.extend(data['metadata'])
                st.session_state.index = faiss.deserialize_index(data['index'])
    except Exception as e:
        st.error(f"Failed to load memory: {e}")
        # Initialize fresh memory on error
        st.session_state.index = faiss.IndexFlatL2(st.session_state.dimension)
        st.session_state.stored_chunks.clear()
        st.session_state.metadata.clear()

def store_document(filename, text, doc_type="Unknown"):
    """Store document in memory with user isolation"""
    try:
        initialize_user_memory()
        model = load_embedding_model()
        
        # Chunk the text
        chunks = chunk_text(text)
        
        for chunk in chunks:
            if len(chunk.strip()) < 10:  # Skip very short chunks
                continue
                
            # Create embedding
            embedding = model.encode([chunk])[0]
            
            # Add to index
            st.session_state.index.add(np.array([embedding]))
            
            # Store chunk and metadata
            st.session_state.stored_chunks.append(chunk)
            st.session_state.metadata.append({
                'filename': filename,
                'doc_type': doc_type,
                'chunk_id': len(st.session_state.stored_chunks) - 1,
                'text_preview': chunk[:100] + "..." if len(chunk) > 100 else chunk
            })
        
        # Save to disk
        save_memory()
        return True
        
    except Exception as e:
        st.error(f"Failed to store document: {e}")
        return False

def search_documents(query, k=5):
    """Search for relevant documents for current user"""
    try:
        initialize_user_memory()
        
        if len(st.session_state.stored_chunks) == 0:
            return []
        
        model = load_embedding_model()
        query_embedding = model.encode([query])[0]
        
        # Search in user's index
        distances, indices = st.session_state.index.search(np.array([query_embedding]), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(st.session_state.stored_chunks):
                results.append({
                    'text': st.session_state.stored_chunks[idx],
                    'metadata': st.session_state.metadata[idx],
                    'similarity': float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                })
        
        return results
        
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []

def get_all_documents():
    """Get all documents for current user"""
    try:
        initialize_user_memory()
        
        # Group by filename
        documents = {}
        for meta in st.session_state.metadata:
            filename = meta['filename']
            if filename not in documents:
                documents[filename] = {
                    'filename': filename,
                    'doc_type': meta['doc_type'],
                    'chunks': 0,
                    'preview': meta['text_preview']
                }
            documents[filename]['chunks'] += 1
        
        return list(documents.values())
        
    except Exception as e:
        st.error(f"Failed to get documents: {e}")
        return []

def remove_document(filename):
    """Remove document from current user's memory"""
    try:
        initialize_user_memory()
        
        # Find indices to remove
        indices_to_remove = []
        for i, meta in enumerate(st.session_state.metadata):
            if meta['filename'] == filename:
                indices_to_remove.append(i)
        
        if not indices_to_remove:
            return False
        
        # Remove in reverse order to avoid index shifting
        for idx in reversed(indices_to_remove):
            st.session_state.stored_chunks.pop(idx)
            st.session_state.metadata.pop(idx)
        
        # Rebuild index
        st.session_state.index = faiss.IndexFlatL2(st.session_state.dimension)
        if st.session_state.stored_chunks:
            model = load_embedding_model()
            embeddings = model.encode(st.session_state.stored_chunks)
            st.session_state.index.add(np.array(embeddings))
        
        # Update chunk_ids in metadata
        for i, meta in enumerate(st.session_state.metadata):
            meta['chunk_id'] = i
        
        save_memory()
        return True
        
    except Exception as e:
        st.error(f"Failed to remove document: {e}")
        return False

def get_context_for_query(query, max_chunks=3):
    """Get relevant context for a query from current user's documents"""
    try:
        initialize_user_memory()
        
        if len(st.session_state.stored_chunks) == 0:
            return "No documents found in memory."
        
        results = search_documents(query, k=max_chunks)
        
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for result in results:
            context_parts.append(f"From {result['metadata']['filename']}:\n{result['text']}")
        
        return "\n\n---\n\n".join(context_parts)
        
    except Exception as e:
        st.error(f"Failed to get context: {e}")
        return "Error retrieving context."

def clear_all_memory():
    """Clear all memory for current user"""
    try:
        initialize_user_memory()
        
        st.session_state.stored_chunks.clear()
        st.session_state.metadata.clear()
        st.session_state.index = faiss.IndexFlatL2(st.session_state.dimension)
        
        # Remove user's memory file
        memory_file = get_memory_file()
        if os.path.exists(memory_file):
            os.remove(memory_file)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to clear memory: {e}")
        return False

def get_memory_stats():
    """Get memory statistics for current user"""
    try:
        initialize_user_memory()
        
        total_chunks = len(st.session_state.stored_chunks)
        unique_docs = len(set(meta['filename'] for meta in st.session_state.metadata))
        
        return {
            "total_chunks": total_chunks,
            "unique_documents": unique_docs,
            "memory_file_exists": os.path.exists(get_memory_file()),
            "session_id": get_user_session_id()
        }
        
    except Exception as e:
        st.error(f"Failed to get memory stats: {e}")
        return {"error": str(e)}

def get_document_text(filename):
    """Get full text of a document for current user"""
    try:
        initialize_user_memory()
        
        chunks = []
        for i, meta in enumerate(st.session_state.metadata):
            if meta['filename'] == filename:
                chunks.append(st.session_state.stored_chunks[i])
        
        return "\n\n".join(chunks) if chunks else None
        
    except Exception as e:
        st.error(f"Failed to get document text: {e}")
        return None

# Initialize memory on import
if 'memory_initialized' not in st.session_state:
    initialize_user_memory()
    st.session_state.memory_initialized = True
