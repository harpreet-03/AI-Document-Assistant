# summarizer.py

import os
import requests
import streamlit as st  # Added missing import
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def call_gemini(prompt: str) -> str:
    """
    Makes API call to Gemini and returns the response text.
    """
    if not GEMINI_API_KEY:
        return "❌ GEMINI_API_KEY not found in environment variables."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_msg = f"Gemini API Error: {response.status_code} - {response.text}"
            st.error(error_msg)
            return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Exception occurred: {e}"
        st.error(error_msg)
        return f"❌ {error_msg}"

def call_gemini_for_qa(prompt: str) -> str:
    """
    Makes API call to Gemini specifically for Q&A tasks.
    """
    return call_gemini(prompt)

def generate_summary_and_tasks(text: str) -> str:
    """
    Generates summary and tasks from the given text using Gemini.
    """
    prompt = f"""
You are an intelligent AI assistant that reads any document or text and extracts useful insights.

Your job:
1. First, detect the type of content (e.g., resume, meeting notes, legal document, research paper, project plan, etc.).
2. Provide a concise 4–5 line summary that captures the main points, adapted to the document type.
3. Extract a list of actionable tasks or next steps (if any) in this format:
- [ ] Task Description (Due Date if known) – Assigned to (if known)

Text:
{text[:4000]}

If the document has no obvious actionable tasks, say: "No specific actionable tasks found, but here's the summary above."
"""
    return call_gemini(prompt)