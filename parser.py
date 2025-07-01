# parser.py

import fitz  # PyMuPDF
import re
import os
from typing import List, Optional, Dict, Any
import streamlit as st

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts and returns cleaned text from all pages of a PDF with enhanced processing.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Cleaned and formatted text from the PDF
    """
    try:
        if not os.path.exists(pdf_path):
            return "❌ PDF file not found"
        
        doc = fitz.open(pdf_path)
        full_text = ""
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Try different extraction methods for better quality
            page_text = ""
            
            # Method 1: Standard text extraction
            text = page.get_text()
            if text.strip():
                page_text = text
            
            # Method 2: If standard extraction fails, try block-based extraction
            if not page_text.strip():
                blocks = page.get_text("blocks")
                page_text = "\n".join([block[4] for block in blocks if len(block) > 4])
            
            # Method 3: If still no text, try dict-based extraction (more detailed)
            if not page_text.strip():
                text_dict = page.get_text("dict")
                page_text = extract_text_from_dict(text_dict)
            
            if page_text.strip():
                full_text += f"\n--- Page {page_num + 1} ---\n"
                full_text += page_text + "\n"
        
        doc.close()  # Important: close the document to free memory
        
        if not full_text.strip():
            return "❌ No text could be extracted from this PDF"
        
        # Clean and format the extracted text
        cleaned_text = clean_extracted_text(full_text)
        
        return cleaned_text
        
    except Exception as e:
        return f"❌ Failed to extract text: {str(e)}"

def extract_text_from_dict(text_dict: Dict[Any, Any]) -> str:
    """
    Extract text from PyMuPDF text dictionary format.
    
    Args:
        text_dict: Text dictionary from PyMuPDF
    
    Returns:
        Extracted text string
    """
    text = ""
    
    try:
        if "blocks" in text_dict:
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            line_text = ""
                            for span in line["spans"]:
                                if "text" in span:
                                    line_text += span["text"]
                            if line_text.strip():
                                text += line_text + "\n"
                        elif "bbox" in line:  # Fallback for different structure
                            text += str(line) + "\n"
    except Exception:
        pass  # Return whatever text we managed to extract
    
    return text

def clean_extracted_text(text: str) -> str:
    """
    Clean and format extracted text for better readability and processing.
    
    Args:
        text: Raw extracted text
    
    Returns:
        Cleaned and formatted text
    """
    if not text:
        return ""
    
    # Remove page markers for cleaner text
    text = re.sub(r'\n--- Page \d+ ---\n', '\n\n', text)
    
    # Fix common PDF extraction issues
    text = fix_common_pdf_issues(text)
    
    # Normalize whitespace
    text = normalize_whitespace(text)
    
    # Remove excessive line breaks but preserve paragraph structure
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def fix_common_pdf_issues(text: str) -> str:
    """
    Fix common issues that occur during PDF text extraction.
    
    Args:
        text: Text with potential PDF extraction issues
    
    Returns:
        Text with common issues fixed
    """
    # Fix hyphenated words that got split across lines
    text = re.sub(r'-\s*\n\s*', '', text)
    
    # Fix words that got split without hyphens (common in PDFs)
    # This is a conservative approach to avoid breaking intentional formatting
    text = re.sub(r'([a-z])\n([a-z])', r'\1\2', text)
    
    # Fix bullet points and list formatting
    text = re.sub(r'^\s*[•·▪▫‣⁃]\s*', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-−–—]\s*', '- ', text, flags=re.MULTILINE)
    
    # Fix common character encoding issues
    replacements = {
        ''': "'", ''': "'", '"': '"', '"': '"',
        '–': '-', '—': '-', '…': '...',
        'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff',
        '�': ' ',  # Replace unknown characters
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving meaningful structure.
    
    Args:
        text: Text to normalize
    
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Remove spaces at beginning and end of lines
    text = re.sub(r'^ +| +$', '', text, flags=re.MULTILINE)
    
    # Remove empty lines but preserve double line breaks for paragraphs
    lines = text.split('\n')
    cleaned_lines = []
    prev_empty = False
    
    for line in lines:
        if line.strip():
            cleaned_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            cleaned_lines.append('')
            prev_empty = True
    
    return '\n'.join(cleaned_lines)

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    Splits text into overlapping chunks with improved sentence boundary detection.
    
    Args:
        text: Input text to chunk
        chunk_size: Target number of words per chunk
        overlap: Number of overlapping words between chunks
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # First, try to split by sentences for better chunks
    sentences = split_into_sentences(text)
    
    if not sentences:
        # Fallback to word-based chunking
        return chunk_by_words(text, chunk_size, overlap)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        # If adding this sentence would exceed chunk size, finalize current chunk
        if current_word_count + sentence_words > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
            
            # Start new chunk with overlap
            overlap_sentences = get_overlap_sentences(current_chunk, overlap)
            current_chunk = overlap_sentences + [sentence]
            current_word_count = sum(len(s.split()) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_words
    
    # Add the last chunk
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        if chunk_text.strip():
            chunks.append(chunk_text)
    
    # Filter out very short chunks (less than 10 words)
    chunks = [chunk for chunk in chunks if len(chunk.split()) >= 10]
    
    return chunks if chunks else [text]  # Return original text if chunking failed

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using improved sentence boundary detection.
    
    Args:
        text: Text to split
    
    Returns:
        List of sentences
    """
    # Simple sentence splitting with common abbreviations handling
    abbreviations = {
        'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Ph.D.', 'M.D.', 'B.A.', 'M.A.',
        'Inc.', 'Ltd.', 'Corp.', 'Co.', 'etc.', 'vs.', 'e.g.', 'i.e.',
        'Jan.', 'Feb.', 'Mar.', 'Apr.', 'Jun.', 'Jul.', 'Aug.', 'Sep.',
        'Oct.', 'Nov.', 'Dec.', 'U.S.', 'U.K.', 'U.N.'
    }
    
    # Replace abbreviations temporarily
    temp_text = text
    replacements = {}
    for i, abbr in enumerate(abbreviations):
        placeholder = f"__ABBR_{i}__"
        replacements[placeholder] = abbr
        temp_text = temp_text.replace(abbr, placeholder)
    
    # Split on sentence endings
    sentences = re.split(r'[.!?]+\s+', temp_text)
    
    # Restore abbreviations
    for i, sentence in enumerate(sentences):
        for placeholder, abbr in replacements.items():
            sentence = sentence.replace(placeholder, abbr)
        sentences[i] = sentence.strip()
    
    # Filter out empty sentences
    sentences = [s for s in sentences if s and len(s.split()) > 2]
    
    return sentences

def get_overlap_sentences(sentences: List[str], overlap_words: int) -> List[str]:
    """
    Get sentences for overlap based on word count.
    
    Args:
        sentences: List of sentences
        overlap_words: Target number of overlap words
    
    Returns:
        List of sentences for overlap
    """
    if not sentences:
        return []
    
    overlap_sentences = []
    word_count = 0
    
    # Take sentences from the end until we reach overlap word count
    for sentence in reversed(sentences):
        sentence_words = len(sentence.split())
        if word_count + sentence_words <= overlap_words:
            overlap_sentences.insert(0, sentence)
            word_count += sentence_words
        else:
            break
    
    return overlap_sentences

def chunk_by_words(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Fallback chunking method using word boundaries.
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words
    
    Returns:
        List of text chunks
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)
        if chunk.strip():
            chunks.append(chunk)
        
        if i + chunk_size >= len(words):
            break
    
    return chunks

def extract_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    Extract metadata from PDF file.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Dictionary containing PDF metadata
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        
        # Get additional information
        page_count = len(doc)
        file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        
        doc.close()
        
        return {
            'title': metadata.get('title', 'Unknown'),
            'author': metadata.get('author', 'Unknown'),
            'subject': metadata.get('subject', 'Unknown'),
            'creator': metadata.get('creator', 'Unknown'),
            'producer': metadata.get('producer', 'Unknown'),
            'creation_date': metadata.get('creationDate', 'Unknown'),
            'modification_date': metadata.get('modDate', 'Unknown'),
            'page_count': page_count,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2)
        }
    except Exception as e:
        return {'error': f"Failed to extract metadata: {str(e)}"}

def get_text_statistics(text: str) -> Dict[str, Any]:
    """
    Generate statistics about the extracted text.
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with text statistics
    """
    if not text:
        return {}
    
    words = text.split()
    sentences = split_into_sentences(text)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Character count (excluding spaces)
    char_count_no_spaces = len(re.sub(r'\s', '', text))
    
    # Average words per sentence
    avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
    
    # Estimated reading time (average 200 words per minute)
    reading_time_minutes = len(words) / 200
    
    return {
        'total_characters': len(text),
        'characters_no_spaces': char_count_no_spaces,
        'total_words': len(words),
        'total_sentences': len(sentences),
        'total_paragraphs': len(paragraphs),
        'average_words_per_sentence': round(avg_words_per_sentence, 1),
        'estimated_reading_time_minutes': round(reading_time_minutes, 1)
    }