# app.py
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from parser import extract_text_from_pdf, extract_metadata, get_text_statistics
from summarizer import (generate_summary_and_tasks, call_gemini_for_qa, 
                       generate_questions, extract_entities, detect_document_type, analyze_ats_score)
from memory import (store_document, search_documents, get_memory_stats, 
                   clear_all_memory, get_all_documents, remove_document, get_context_for_query, get_document_text)

# Load environment variables
load_dotenv()

# Check for required API key
if not os.getenv("GEMINI_API_KEY"):
    st.error("⚠️ GEMINI_API_KEY not configured. Please add it to your environment variables.")
    st.info("Add your Gemini API key to a .env file: `GEMINI_API_KEY=your_key_here`")
    st.stop()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []

# --- Streamlit UI Setup ---
st.set_page_config(
    page_title="📄 AI Document Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 AI Document Assistant with Memory ✨")
st.markdown("Upload PDFs, get AI summaries, and ask intelligent questions with persistent memory!")

# Force deployment refresh - Version 2.0

# --- Feature Selection ---
st.markdown("### Choose a Feature:")
col_features = st.columns(2)

with col_features[0]:
    if st.button("📄 Document Analysis", type="primary", use_container_width=True):
        st.session_state.current_feature = "document_analysis"

with col_features[1]:
    if st.button("🎯 ATS Resume Scorer", type="secondary", use_container_width=True):
        st.session_state.current_feature = "ats_scorer"

# Initialize current feature
if 'current_feature' not in st.session_state:
    st.session_state.current_feature = "document_analysis"

st.markdown("---")

# --- Main Content Area ---
if st.session_state.current_feature == "document_analysis":
    # Original Document Analysis Feature
    col1, col2 = st.columns([2, 1])

    with col1:
        # --- Upload PDF ---
        pdf_file = st.file_uploader("📤 Upload a PDF Document", type=["pdf"])

        if pdf_file:
            # Validate file size (max 10MB)
            if pdf_file.size > 10 * 1024 * 1024:
                st.error("📁 File too large. Please upload a PDF smaller than 10MB.")
                st.stop()
            
            # Validate file type more strictly
            if not pdf_file.name.lower().endswith('.pdf'):
                st.error("📄 Please upload a valid PDF file.")
                st.stop()

            # Save uploaded file temporarily
            with open("temp.pdf", "wb") as f:
                f.write(pdf_file.read())

            # Extract text
            with st.spinner("⏳ Extracting text from PDF..."):
                raw_text = extract_text_from_pdf("temp.pdf")
                if raw_text.startswith("❌"):
                    st.error(raw_text)
                else:
                    st.success("✅ Text extracted successfully!")

            # Show extracted text in expandable section
            if not raw_text.startswith("❌"):
                with st.expander("📖 View Extracted Text", expanded=False):
                    st.text_area("Extracted PDF Content", raw_text, height=300, disabled=True)

                # --- Enhanced PDF Analysis Section ---
                # Create tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["📄 Summary", "📊 Statistics", "🔍 Entities", "❓ Suggested Questions"])
                
                with tab1:
                    # AI Analysis
                    with st.spinner("🧠 Analyzing with AI..."):
                        summary_and_tasks = generate_summary_and_tasks(raw_text)
                    
                    st.subheader("📝 AI Analysis")
                    st.markdown(summary_and_tasks)

                    # Store in Memory
                    col_save, col_info = st.columns([1, 2])
                    with col_save:
                        if st.button("💾 Save to Memory", type="primary"):
                            try:
                                success = store_document(
                                    pdf_file.name,
                                    raw_text + "\n\n" + summary_and_tasks, 
                                    doc_type="PDF"
                                )
                                if success:
                                    st.success("✅ Document saved to memory!")
                                    
                                    # Add to uploaded docs history for session tracking
                                    st.session_state.uploaded_docs.append({
                                        'name': pdf_file.name,
                                        'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'type': 'PDF',
                                        'size': f"{pdf_file.size / 1024:.1f} KB"
                                    })
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to save to memory")
                            except Exception as e:
                                st.error(f"❌ Error saving to memory: {e}")
                    
                    with col_info:
                        st.info("💡 Save this document to memory to ask questions about it later!")
                
                with tab2:
                    # Document statistics
                    col_stats, col_meta = st.columns(2)
                    
                    with col_stats:
                        st.subheader("📊 Text Statistics")
                        text_stats = get_text_statistics(raw_text)
                        if text_stats:
                            st.metric("Words", text_stats['total_words'])
                            st.metric("Sentences", text_stats['total_sentences'])
                            st.metric("Paragraphs", text_stats['total_paragraphs'])
                            st.metric("Reading Time", f"{text_stats['estimated_reading_time_minutes']:.1f} min")
                    
                    with col_meta:
                        st.subheader("📋 PDF Metadata")
                        pdf_metadata = extract_metadata("temp.pdf")
                        if 'error' not in pdf_metadata:
                            st.write(f"**Pages:** {pdf_metadata['page_count']}")
                            st.write(f"**File Size:** {pdf_metadata['file_size_mb']} MB")
                            st.write(f"**Title:** {pdf_metadata['title']}")
                            st.write(f"**Author:** {pdf_metadata['author']}")
                            st.write(f"**Created:** {pdf_metadata['creation_date']}")
                
                with tab3:
                    # Entity extraction
                    st.subheader("🔍 Key Entities")
                    with st.spinner("Extracting entities..."):
                        entities = extract_entities(raw_text)
                    
                    if entities and 'entities' in entities:
                        st.markdown(entities['entities'])
                    else:
                        st.info("No entities extracted")
                
                with tab4:
                    # Suggested questions
                    st.subheader("❓ Suggested Questions")
                    with st.spinner("Generating questions..."):
                        questions = generate_questions(raw_text)
                    
                    if questions:
                        st.write("Here are some questions you might want to ask about this document:")
                        for i, question in enumerate(questions, 1):
                            if st.button(f"{i}. {question}", key=f"q_{i}"):
                                # Set the question in session state and trigger processing
                                st.session_state.selected_question = question
                                st.rerun()
                    else:
                        st.info("No questions generated")

        # --- Memory-Based Question Answering ---
        st.markdown("---")
        st.subheader("🔎 Ask Questions from Memory")
        
        # Show memory status
        memory_stats = get_memory_stats()
        if memory_stats['total_documents'] > 0:
            st.success(f"💾 Memory contains {memory_stats['total_documents']} documents with {memory_stats['total_chunks']} chunks")
        else:
            st.warning("📝 No documents in memory. Upload and save some documents first!")

        # Handle selected question from suggested questions
        if 'selected_question' in st.session_state:
            query = st.session_state.selected_question
            # Clear the selected question
            del st.session_state.selected_question
            # Process the question automatically
            process_question = True
            question_source = "suggested questions"
        else:
            # Q&A with manual input
            query = st.text_input(
                "Ask a question about your documents:",
                placeholder="e.g., What are my upcoming deadlines? Summarize the main points..."
            )
            process_question = bool(query)
            question_source = "text input"

        # Clear the auto question after it's been used in the text input
        # Only clear if the query is not empty (meaning user has seen the question)
        if 'auto_question' in st.session_state and query:
            del st.session_state.auto_question

        if process_question and query and memory_stats['total_documents'] > 0:
            # Show the question being processed
            st.write(f"**Question:** {query}")
            st.write(f"**Source:** {question_source}")
        
        with st.spinner("🔍 Searching memory and generating answer..."):
            try:
                # Get enhanced search results with scores
                context_results = search_documents(query, k=5)
                
                if context_results:
                    # Prepare context for AI
                    context = "\n\n".join([result['text'] for result in context_results])

                    # Create ultra-explicit Q&A prompt to prevent question generation
                    qa_prompt = f"""
TASK: Answer the user's question based on the document content. DO NOT GENERATE QUESTIONS.

DOCUMENT CONTEXT:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Read the document context above
2. Answer the user's question using only information from the document
3. Provide a direct answer - do not generate any questions
4. If you cannot answer, say "I cannot answer this based on the document content"

Your response should be a direct answer, not questions. Start your response with "Based on the document content:"

ANSWER:"""

                    response = call_gemini_for_qa(qa_prompt)
                    
                    # Display the answer
                    st.subheader("🧠 AI Answer:")
                    st.markdown(response)
                    
                    # Show source information
                    with st.expander("📚 Source Information", expanded=False):
                        st.write("**Most relevant document chunks:**")
                        for i, result in enumerate(context_results[:3], 1):
                            similarity_pct = result['similarity'] * 100
                            doc_name = result['metadata'].get('filename', 'Unknown')
                            st.write(f"**{i}. {doc_name}** (Similarity: {similarity_pct:.1f}%)")
                            st.write(f"_{result['text'][:200]}..._")
                            st.write("---")
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        'question': query,
                        'answer': response,
                        'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'sources': len(context_results)
                    })
                else:
                    st.warning("🔍 No relevant information found in memory for your question.")
            except Exception as e:
                st.error(f"❌ Error processing question: {e}")

    with col2:
        # --- Memory Stats and History ---
        st.subheader("🧠 Memory & Statistics")

        # Memory Statistics
        memory_stats = get_memory_stats()
        
        # Create metrics display
        col_docs, col_chunks = st.columns(2)
        with col_docs:
            st.metric("📁 Documents", memory_stats['total_documents'])
        with col_chunks:
            st.metric("🧩 Chunks", memory_stats['total_chunks'])

    # Memory status indicator
    if memory_stats['memory_file_exists']:
        st.success("💾 Persistent memory active")
    else:
        st.info("🆕 Starting fresh memory")

    # Memory management buttons
    col_clear, col_export = st.columns(2)
    with col_clear:
        if st.button("🗑️ Clear Memory", help="Clear all stored documents"):
            clear_all_memory()
            st.session_state.chat_history = []
            st.session_state.uploaded_docs = []
            st.success("Memory cleared!")
            st.rerun()
    
    with col_export:
        if memory_stats['total_documents'] > 0:
            if st.button("📤 Export Data", help="Export chat history"):
                # Create export data
                export_data = {
                    'chat_history': st.session_state.chat_history,
                    'uploaded_docs': st.session_state.uploaded_docs,
                    'memory_stats': memory_stats
                }
                st.download_button(
                    "⬇️ Download JSON",
                    data=pd.DataFrame(st.session_state.chat_history).to_json(),
                    file_name=f"ai_assistant_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

    # Uploaded Documents History
    st.markdown("---")
    st.subheader("📄 Document Library")
    
    # Get documents from memory (persistent) instead of just session state
    memory_documents = get_all_documents()
    
    if memory_documents:
        for i, doc in enumerate(memory_documents):
            with st.expander(f"📄 {doc['filename'][:25]}{'...' if len(doc['filename']) > 25 else ''}"):
                st.write(f"**Type:** {doc['doc_type']}")
                st.write(f"**Chunks:** {doc['chunks']}")
                
                # Show preview of document content
                if doc['preview']:
                    st.write("**Preview:**")
                    st.write(f"_{doc['preview']}_")
                
                # Option to view all document chunks
                if st.button(f"👁️ View All Chunks", key=f"view_memory_{i}"):
                    chunks = get_document_text(doc['filename'])
                    if chunks:
                        st.text_area("All Document Chunks", chunks, height=300, key=f"chunks_{i}")
                    else:
                        st.write("No chunks found for this document.")
                
                # Option to remove document from memory
                if st.button(f"🗑️ Remove Document", key=f"remove_{i}", help="Remove this document from memory"):
                    try:
                        success = remove_document(doc['filename'])
                        if success:
                            st.success(f"✅ Document '{doc['filename']}' removed from memory!")
                            st.rerun()
                        else:
                            st.error(f"❌ Document '{doc['filename']}' not found in memory")
                    except Exception as e:
                        st.error(f"❌ Error removing document: {e}")
    else:
        st.write("📝 No documents in memory yet")

    # Chat History
    st.markdown("---")
    st.subheader("💬 Recent Questions")
    if st.session_state.chat_history:
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.expander(f"❓ {chat['question'][:30]}{'...' if len(chat['question']) > 30 else ''}"):
                st.write(f"**Asked:** {chat['timestamp']}")
                st.write(f"**Sources:** {chat.get('sources', 'Unknown')} chunks")
                st.write(f"**Q:** {chat['question']}")
                st.write(f"**A:** {chat['answer'][:300]}{'...' if len(chat['answer']) > 300 else ''}")
    else:
        st.write("🤔 No questions asked yet")

elif st.session_state.current_feature == "ats_scorer":
    # ATS Resume Scoring Feature
    st.subheader("🎯 ATS Resume Scorer")
    st.markdown("Upload your resume to get an ATS compatibility score and detailed feedback!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Resume Upload
        resume_file = st.file_uploader("📤 Upload Resume (PDF)", type=["pdf"], key="ats_resume")
        
        # Optional Job Description
        job_description = st.text_area(
            "📋 Job Description (Optional)", 
            placeholder="Paste the job description here to get more targeted ATS analysis...",
            height=150
        )
        
        if resume_file:
            # Validate file
            if resume_file.size > 5 * 1024 * 1024:  # 5MB limit for resumes
                st.error("📁 Resume file too large. Please upload a file smaller than 5MB.")
                st.stop()
            
            # Save and extract text
            with open("temp_resume.pdf", "wb") as f:
                f.write(resume_file.read())
            
            with st.spinner("⏳ Extracting resume text..."):
                resume_text = extract_text_from_pdf("temp_resume.pdf")
                
                if resume_text.startswith("❌"):
                    st.error(resume_text)
                else:
                    st.success("✅ Resume text extracted successfully!")
                    
                    # Show extracted text preview
                    with st.expander("📖 Resume Text Preview", expanded=False):
                        st.text_area("Resume Content", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=200, disabled=True)
                    
                    # Analyze ATS Score
                    if st.button("🎯 Analyze ATS Score", type="primary"):
                        with st.spinner("🔍 Analyzing ATS compatibility..."):
                            ats_result = analyze_ats_score(resume_text, job_description)
                            
                            if ats_result["success"]:
                                # Display ATS Score
                                if ats_result["score"]:
                                    score = ats_result["score"]
                                    if score >= 80:
                                        st.success(f"🎉 Excellent ATS Score: {score}/100")
                                    elif score >= 60:
                                        st.warning(f"⚠️ Good ATS Score: {score}/100")
                                    else:
                                        st.error(f"❌ Needs Improvement: {score}/100")
                                
                                # Display detailed analysis
                                st.markdown("### 📊 ATS Analysis Report")
                                st.markdown(ats_result["analysis"])
                                
                                # Option to save to memory
                                if st.button("💾 Save Resume to Memory"):
                                    try:
                                        success = store_document(
                                            f"ATS_Analysis_{resume_file.name}",
                                            resume_text + "\n\n" + ats_result["analysis"], 
                                            doc_type="Resume"
                                        )
                                        if success:
                                            st.success("✅ Resume analysis saved to memory!")
                                        else:
                                            st.error("❌ Failed to save to memory")
                                    except Exception as e:
                                        st.error(f"❌ Error saving to memory: {e}")
                            else:
                                st.error("❌ Failed to analyze resume for ATS compatibility")
    
    with col2:
        # ATS Tips and Info
        st.subheader("💡 ATS Tips")
        
        st.markdown("""
        **What is ATS?**
        - Applicant Tracking System
        - Filters resumes before human review
        - Looks for keywords and formatting
        
        **Key Factors:**
        - ✅ Relevant keywords
        - ✅ Clear formatting
        - ✅ Standard section headers
        - ✅ Quantified achievements
        - ✅ Contact information
        
        **Score Ranges:**
        - 🎉 80-100: Excellent
        - ⚠️ 60-79: Good  
        - ❌ 0-59: Needs Work
        """)
        
        # Recent ATS Analyses
        st.markdown("---")
        st.subheader("📈 Recent Analyses")
        
        # Get memory documents filtered for resumes
        memory_docs = get_all_documents()
        resume_docs = [doc for doc in memory_docs if doc['doc_type'] == 'Resume']
        
        if resume_docs:
            for doc in resume_docs[-3:]:  # Show last 3 resume analyses
                with st.expander(f"📄 {doc['filename'][:20]}..."):
                    st.write(f"**Chunks:** {doc['chunks']}")
                    st.write(f"**Preview:** {doc['preview'][:100]}...")
        else:
            st.write("No resume analyses yet")

# Clean up temporary files
try:
    if os.path.exists("temp.pdf"):
        os.remove("temp.pdf")
except Exception:
    pass

# Footer
st.markdown("---")
st.markdown("🚀 **AI Document Assistant** - Powered by Gemini AI & Semantic Search")