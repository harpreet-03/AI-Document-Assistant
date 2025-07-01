# summarizer.py

import os
import requests
import streamlit as st
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash"

# Try to get API key from Streamlit secrets first, then from environment
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Rate limiting and retry configuration
MAX_RETRIES = 3
TIMEOUT = 45
MAX_INPUT_LENGTH = 30000  # Conservative limit for Gemini

def call_gemini(prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
    """
    Makes API call to Gemini with enhanced error handling and retry logic.
    
    Args:
        prompt: The prompt to send to Gemini
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum tokens in response
    
    Returns:
        Generated text response
    """
    if not GEMINI_API_KEY:
        st.error("⚠️ **GEMINI_API_KEY not configured!**")
        st.info("""
        **For Local Development:**
        Add your API key to `.env` file: `GEMINI_API_KEY=your_key_here`
        
        **For Streamlit Cloud:**
        1. Go to your app settings
        2. Click 'Secrets' tab
        3. Add: `GEMINI_API_KEY = "your_key_here"`
        """)
        return "❌ GEMINI_API_KEY not found in environment variables or Streamlit secrets."
    
    # Truncate prompt if too long
    if len(prompt) > MAX_INPUT_LENGTH:
        st.warning(f"⚠️ Input truncated to {MAX_INPUT_LENGTH} characters for API limits")
        prompt = prompt[:MAX_INPUT_LENGTH] + "\n\n[Text truncated due to length limits]"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "topP": 0.8,
            "topK": 40
        }
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, json=payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has the expected structure
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0]["text"]
                    else:
                        return "❌ Unexpected response format from Gemini API"
                else:
                    return "❌ No valid response from Gemini API"
                    
            elif response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                st.warning(f"⏳ Rate limited. Retrying in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
                continue
                
            elif response.status_code == 400:
                error_msg = f"Bad Request: {response.text}"
                st.error(error_msg)
                return f"❌ {error_msg}"
                
            else:
                error_msg = f"Gemini API Error: {response.status_code} - {response.text}"
                st.error(error_msg)
                return f"❌ {error_msg}"
                
        except requests.exceptions.Timeout:
            st.warning(f"⏳ Request timeout. Attempt {attempt + 1}/{MAX_RETRIES}")
            if attempt == MAX_RETRIES - 1:
                return "❌ Request timed out after multiple attempts"
                
        except requests.exceptions.ConnectionError:
            st.warning(f"🌐 Connection error. Attempt {attempt + 1}/{MAX_RETRIES}")
            if attempt == MAX_RETRIES - 1:
                return "❌ Unable to connect to Gemini API"
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            st.error(error_msg)
            return f"❌ {error_msg}"
    
    return "❌ Failed after multiple attempts"

def call_gemini_for_qa(prompt: str) -> str:
    """
    Makes API call to Gemini specifically optimized for Q&A tasks.
    """
    return call_gemini(prompt, temperature=0.3, max_tokens=1500)

def detect_document_type(text: str) -> str:
    """
    Analyze text to detect document type using AI.
    
    Args:
        text: Document text to analyze
    
    Returns:
        Detected document type
    """
    detection_prompt = f"""
Analyze the following text and determine what type of document this is. 

Choose from these categories:
- Resume/CV
- Meeting Notes
- Email
- Legal Document
- Research Paper
- Business Report
- Technical Documentation
- Project Plan
- Financial Report
- Academic Paper
- News Article
- General Document

Text sample (first 1000 characters):
{text[:1000]}

Respond with just the document type category, nothing else.
"""
    
    try:
        doc_type = call_gemini(detection_prompt, temperature=0.1, max_tokens=50)
        # Clean up the response
        doc_type = doc_type.strip().replace("❌", "").strip()
        if doc_type and not doc_type.startswith("❌"):
            return doc_type
        else:
            return "General Document"
    except:
        return "General Document"

def generate_summary_and_tasks(text: str) -> str:
    """
    Generates an intelligent summary and extracts tasks based on document type.
    
    Args:
        text: Document text to analyze
    
    Returns:
        Formatted summary with document-specific insights
    """
    # First detect document type
    doc_type = detect_document_type(text)
    
    # Create document-type specific prompts
    if "resume" in doc_type.lower() or "cv" in doc_type.lower():
        analysis_prompt = f"""
You are analyzing a RESUME/CV. Provide:

1. **Document Type**: Resume/CV Analysis
2. **Summary**: 3-4 lines covering key qualifications, experience level, and main skills
3. **Key Information**:
   - Years of experience
   - Primary skills/technologies
   - Education level
   - Notable achievements
4. **Actionable Items**:
   - [ ] Update contact information if needed
   - [ ] Review for formatting consistency
   - [ ] Add quantifiable achievements
   - [ ] Tailor for specific job applications

Document text:
{text[:2500]}
"""
    
    elif "meeting" in doc_type.lower():
        analysis_prompt = f"""
You are analyzing MEETING NOTES. Provide:

1. **Document Type**: Meeting Notes Analysis
2. **Summary**: 3-4 lines covering meeting purpose, key decisions, and outcomes
3. **Key Information**:
   - Meeting date and attendees (if mentioned)
   - Main topics discussed
   - Decisions made
   - Next steps identified
4. **Action Items**:
   - Extract all tasks mentioned with due dates and assignees
   - Format as: [ ] Task Description (Due: Date) - Assigned to: Person

Document text:
{text[:2500]}
"""
    
    elif any(keyword in doc_type.lower() for keyword in ["legal", "contract", "agreement"]):
        analysis_prompt = f"""
You are analyzing a LEGAL DOCUMENT. Provide:

1. **Document Type**: Legal Document Analysis
2. **Summary**: 3-4 lines covering document purpose, key terms, and parties involved
3. **Key Information**:
   - Document type and purpose
   - Parties involved
   - Key terms and conditions
   - Important dates and deadlines
4. **Important Items**:
   - [ ] Review all terms and conditions
   - [ ] Note important dates and deadlines
   - [ ] Identify obligations and responsibilities
   - [ ] Consider legal review if needed

Document text:
{text[:3500]}
"""
    
    elif any(keyword in doc_type.lower() for keyword in ["research", "academic", "paper"]):
        analysis_prompt = f"""
You are analyzing a RESEARCH/ACADEMIC PAPER. Provide:

1. **Document Type**: Research Paper Analysis
2. **Summary**: 3-4 lines covering research topic, methodology, and key findings
3. **Key Information**:
   - Research topic and objectives
   - Methodology used
   - Key findings and conclusions
   - Authors and publication info
4. **Follow-up Items**:
   - [ ] Review methodology and data
   - [ ] Analyze conclusions and implications
   - [ ] Check citations and references
   - [ ] Consider practical applications

Document text:
{text[:3000]}
"""
    
    else:
        # Generic analysis for other document types
        analysis_prompt = f"""
You are analyzing a {doc_type.upper()}. Provide:

1. **Document Type**: {doc_type}
2. **Summary**: 4-5 lines capturing the main points and purpose of this document
3. **Key Information**:
   - Main topics covered
   - Important dates, numbers, or deadlines
   - Key people or entities mentioned
   - Critical decisions or conclusions
4. **Actionable Items**:
   - Extract any tasks, deadlines, or action items mentioned
   - Format as: [ ] Task Description (Due Date if known) – Assigned to (if known)
   - If no specific tasks found, suggest relevant follow-up actions

Document text:
{text[:3000]}

If the document contains no obvious actionable tasks, provide useful follow-up suggestions based on the document type and content.
"""
    
    try:
        with st.spinner(f"🔍 Analyzing {doc_type}..."):
            response = call_gemini(analysis_prompt, temperature=0.4, max_tokens=2000)
        
        if response.startswith("❌"):
            return response
        
        # Add document insights footer
        insights_footer = f"""

---
### 🎯 Document Insights
- **Detected Type**: {doc_type}
- **Word Count**: ~{len(text.split())} words
- **Analysis Confidence**: High
- **Recommended Actions**: See action items above

💡 *Tip: You can ask specific questions about this document using the Q&A section below.*
"""
        
        return response + insights_footer
        
    except Exception as e:
        return f"❌ Error generating analysis: {str(e)}"

def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract key entities from text (names, dates, organizations, etc.)
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary of extracted entities
    """
    entity_prompt = f"""
Extract key entities from this text and return them in a structured format:

Text:
{text[:2000]}

Please identify and list:
1. People (names)
2. Organizations/Companies
3. Dates (important dates mentioned)
4. Locations
5. Key Numbers/Amounts
6. Technologies/Tools mentioned

Format your response as a simple list under each category. If a category has no items, write "None found".
"""
    
    try:
        response = call_gemini(entity_prompt, temperature=0.2, max_tokens=800)
        if not response.startswith("❌"):
            return {"entities": response}
        return {"entities": "Entity extraction failed"}
    except:
        return {"entities": "Entity extraction unavailable"}

def generate_questions(text: str) -> list:
    """
    Generate intelligent questions that can be asked about the document.
    
    Args:
        text: Document text
    
    Returns:
        List of suggested questions
    """
    questions_prompt = f"""
Based on this document, generate 5-7 intelligent questions that someone might want to ask about it. 
Make the questions specific and useful for understanding or working with this content.

Document sample:
{text[:1500]}

Format your response as a numbered list of questions only.
"""
    
    try:
        response = call_gemini(questions_prompt, temperature=0.6, max_tokens=500)
        if not response.startswith("❌"):
            # Parse the response into a list
            questions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    question = line.split('.', 1)[-1].strip()
                    if question and question.endswith('?'):
                        questions.append(question)
            return questions[:7]  # Limit to 7 questions
        return []
    except:
        return []

def analyze_ats_score(resume_text: str, job_description: str = "") -> dict:
    """
    Analyze resume for ATS compatibility and provide scoring.
    
    Args:
        resume_text: Resume content to analyze
        job_description: Optional job description for targeted analysis
    
    Returns:
        Dictionary with success status, score, and detailed analysis
    """
    try:
        if not resume_text or not resume_text.strip():
            return {"success": False, "error": "Resume text is empty"}
        
        # Create ATS analysis prompt
        analysis_prompt = f"""
You are an expert ATS (Applicant Tracking System) analyzer. Analyze this resume for ATS compatibility and provide a comprehensive score and feedback.

RESUME TEXT:
{resume_text}

JOB DESCRIPTION (if provided):
{job_description if job_description else "No specific job description provided - provide general ATS analysis"}

Please analyze the resume and provide:

1. ATS COMPATIBILITY SCORE (0-100):
   - Consider keyword optimization, formatting, section headers, contact info, etc.

2. DETAILED ANALYSIS covering:
   - Contact Information (completeness and format)
   - Section Headers (standard ATS-friendly headers)
   - Keywords and Skills (relevance and frequency)
   - Formatting Issues (bullets, fonts, graphics)
   - Content Structure (clear hierarchy, logical flow)
   - Quantified Achievements (metrics and numbers)
   - Job Description Match (if provided)

3. SPECIFIC RECOMMENDATIONS:
   - What to improve for better ATS compatibility
   - Missing keywords or skills
   - Formatting corrections needed

4. STRENGTHS:
   - What the resume does well for ATS systems

Format your response as:

SCORE: [number]/100

ANALYSIS:
[Detailed analysis with clear sections and bullet points]

RECOMMENDATIONS:
[Specific actionable improvements]

STRENGTHS:
[What works well]
"""

        response = call_gemini(analysis_prompt, temperature=0.3, max_tokens=2000)
        
        if response.startswith("❌"):
            return {"success": False, "error": "Failed to analyze resume"}
        
        # Extract score from response
        score = None
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith('SCORE:'):
                try:
                    score_text = line.split(':')[1].strip()
                    score = int(score_text.split('/')[0])
                    break
                except:
                    pass
        
        return {
            "success": True,
            "score": score,
            "analysis": response
        }
        
    except Exception as e:
        return {"success": False, "error": f"Analysis failed: {str(e)}"}