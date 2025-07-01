# app.py
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from parser import extract_text_from_pdf
from summarizer import generate_summary_and_tasks, call_gemini_for_qa
from memory import add_to_memory, search_memory, get_memory_stats, clear_memory

# Load environment variables
load_dotenv()

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []

# --- Streamlit UI Setup ---
st.set_page_config(page_title="📄 Email & Document AI Assistant", layout="wide")

# Remove duplicate title - this was causing issues
st.title("📄 AI Task Extractor + Memory ✨")
st.write("Upload a PDF below to begin.")

# --- Upload PDF ---
pdf_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])

if pdf_file:
    # Save uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(pdf_file.read())

    # Extract text
    with st.spinner("⏳ Extracting text from PDF..."):
        raw_text = extract_text_from_pdf("temp.pdf")
        if raw_text.startswith("❌"):
            st.error(raw_text)
        else:
            st.success("✅ Text Extracted")

    # Show extracted text in expandable section
    if not raw_text.startswith("❌"):
        with st.expander("📖 View Extracted Text"):
            st.text_area("Extracted PDF Content", raw_text, height=300)

        # Summarize & Extract Tasks
        with st.spinner("🧠 Analyzing with Gemini..."):
            summary_and_tasks = generate_summary_and_tasks(raw_text)
        
        st.subheader("📝 AI Summary & Tasks")
        st.markdown(summary_and_tasks)

        # Store in Memory
        try:
            add_to_memory(raw_text + "\n\n" + summary_and_tasks, doc_name=pdf_file.name)
            st.success("✅ Document added to memory!")
            
            # Add to uploaded docs history
            st.session_state.uploaded_docs.append({
                'name': pdf_file.name,
                'timestamp': st.session_state.get('timestamp', 'Unknown'),
                'type': 'PDF'
            })
        except Exception as e:
            st.error(f"❌ Failed to add to memory: {e}")

# --- Memory-Based Question Answering ---
st.markdown("---")
st.subheader("🔎 Ask a Question from Document Memory")
query = st.text_input("E.g., What are my upcoming deadlines?")

if query:
    with st.spinner("🔍 Searching memory..."):
        try:
            context_chunks = search_memory(query)
            if context_chunks:
                context = "\n\n".join(context_chunks)

                # Create a different prompt for Q&A vs document analysis
                qa_prompt = f"""
You are an intelligent AI assistant helping the user find specific information from their uploaded documents.

Based on the following relevant content from the user's documents:

{context}

Please answer this specific question: {query}

Instructions:
- Answer the question directly and specifically
- Use only the information provided in the context above
- If the context doesn't contain enough information to answer the question, say so
- Don't provide a document summary unless specifically asked
- Be concise and focused on the user's question
"""

                response = call_gemini_for_qa(qa_prompt)
                st.subheader("🧠 Memory-Aware Answer:")
                st.markdown(response)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': query,
                    'answer': response,
                    'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                st.warning("No relevant information found in memory. Please upload some documents first.")
        except Exception as e:
            st.error(f"❌ Memory search failed: {e}")

# --- Sidebar: Memory Stats and History ---
st.sidebar.title("🧠 Memory & History")

# Memory Statistics
memory_stats = get_memory_stats()
st.sidebar.subheader("📊 Memory Statistics")
st.sidebar.write(f"**Documents:** {memory_stats['total_documents']}")
st.sidebar.write(f"**Text Chunks:** {memory_stats['total_chunks']}")
st.sidebar.write(f"**Index Size:** {memory_stats['index_size']}")

# Clear Memory Button
if st.sidebar.button("🗑️ Clear All Memory"):
    clear_memory()
    st.session_state.chat_history = []
    st.session_state.uploaded_docs = []
    st.sidebar.success("Memory cleared!")
    st.rerun()

# Uploaded Documents History
st.sidebar.subheader("📄 Uploaded Documents")
if st.session_state.uploaded_docs:
    for i, doc in enumerate(reversed(st.session_state.uploaded_docs)):
        with st.sidebar.expander(f"{doc['name'][:20]}..."):
            st.write(f"**Type:** {doc['type']}")
            st.write(f"**Time:** {doc['timestamp']}")
else:
    st.sidebar.write("No documents uploaded yet")

# Chat History
st.sidebar.subheader("💬 Question History")
if st.session_state.chat_history:
    for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10
        with st.sidebar.expander(f"Q{len(st.session_state.chat_history)-i}: {chat['question'][:30]}..."):
            st.write(f"**Asked:** {chat['timestamp']}")
            st.write(f"**Q:** {chat['question']}")
            st.write(f"**A:** {chat['answer'][:200]}...")
else:
    st.sidebar.write("No questions asked yet")

# Clean up temporary file
try:
    if os.path.exists("temp.pdf"):
        os.remove("temp.pdf")
except:
    pass