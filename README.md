# 🤖 AI Document Assistant

<div align="center">

![AI Document Assistant](https://img.shields.io/badge/AI-Document%20Assistant-blue?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)

*An intelligent document analysis platform powered by Google Gemini AI*

[🚀 Live Demo](https://harpreet-03-ai-assistant-app-dpkcwa.streamlit.app) • [📖 Documentation](#documentation) • [🤝 Contributing](#contributing)

</div>

---

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [✨ Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [📖 Documentation](#-documentation)
- [🎯 Use Cases](#-use-cases)
- [🧠 AI Capabilities](#-ai-capabilities)
- [🔧 Configuration](#-configuration)
- [📈 Performance](#-performance)
- [🎓 Learning Journey](#-learning-journey)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [💬 Final Thoughts](#-final-thoughts)

---

## 🌟 Overview

**AI Document Assistant** is a cutting-edge Streamlit application that revolutionizes document analysis and processing. Built with Google's powerful Gemini AI, it transforms how users interact with their documents through intelligent analysis, contextual Q&A, and professional resume scoring.

### 🎯 What Makes It Special?

- **🧠 Intelligent Document Analysis**: Automatically detects document types and provides tailored insights
- **💬 Contextual Q&A System**: Ask questions about your documents and get AI-powered answers
- **📊 ATS Resume Scoring**: Professional resume analysis with actionable feedback
- **🗄️ Persistent Memory**: Documents are remembered across sessions
- **🎨 Modern UI/UX**: Clean, responsive interface built with Streamlit

---

## ✨ Features

### 🔍 **Document Analysis Engine**
- **Smart Document Detection**: Automatically identifies document types (Resume, Meeting Notes, Legal Documents, etc.)
- **Contextual Summarization**: Generates document-specific summaries and action items
- **Entity Extraction**: Identifies key people, organizations, dates, and technologies
- **Task Identification**: Extracts actionable items and deadlines

### 💭 **Intelligent Q&A System**
- **Context-Aware Responses**: Ask questions about uploaded documents
- **Suggested Questions**: AI generates relevant questions about your content
- **Memory Integration**: Answers based on complete document context
- **Natural Language Processing**: Understands complex queries

### 📈 **ATS Resume Scorer**
- **Comprehensive Analysis**: 100-point scoring system for resume optimization
- **Keyword Optimization**: Identifies missing keywords and skills
- **Formatting Assessment**: Evaluates ATS-friendly formatting
- **Job Description Matching**: Tailored analysis based on specific job requirements
- **Actionable Recommendations**: Specific improvements for better ATS compatibility

### 🗃️ **Document Management**
- **Persistent Storage**: Documents saved across sessions
- **Search Functionality**: Find relevant information quickly
- **Version Control**: Track document changes and updates
- **Batch Processing**: Handle multiple documents efficiently

---

## 🛠️ Tech Stack

### **Frontend & UI**
```python
Streamlit 1.28.0+     # Interactive web application framework
HTML/CSS/JavaScript   # Custom styling and interactions
```

### **AI & Machine Learning**
```python
Google Gemini 2.0     # Large Language Model for analysis
Sentence Transformers # Document embedding and similarity
FAISS                 # Vector similarity search
```

### **Document Processing**
```python
PyMuPDF (fitz)       # PDF text extraction and parsing
Python-dotenv        # Environment variable management
```

### **Data Management**
```python
Pandas               # Data manipulation and analysis
NumPy                # Numerical computations
Pickle               # Object serialization for persistence
```

### **Deployment & Monitoring**
```python
Streamlit Cloud      # Cloud deployment platform
Git/GitHub           # Version control and CI/CD
```

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))
- Git (for cloning)

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/ai-document-assistant.git
cd ai-document-assistant
```

### **2. Set Up Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configure API Key**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### **4. Run the Application**
```bash
streamlit run app.py
```

### **5. Open Your Browser**
Navigate to `http://localhost:8501` and start analyzing documents!

---

## 📖 Documentation

### **Core Modules**

#### 📄 **`app.py`** - Main Application
The central Streamlit application that orchestrates all features:
- User interface management
- Session state handling
- Feature routing (Document Analysis vs ATS Scoring)
- File upload and processing coordination

#### 🧠 **`summarizer.py`** - AI Engine
Handles all AI-related operations:
```python
# Key Functions
call_gemini()              # Core API communication
detect_document_type()     # Smart document classification
generate_summary_and_tasks() # Contextual analysis
analyze_ats_score()        # Resume scoring system
generate_questions()       # Suggested question generation
```

#### 🗄️ **`memory.py`** - Persistence Layer
Manages document storage and retrieval:
```python
# Key Functions
store_document()          # Save documents with metadata
search_documents()        # Semantic search capabilities
get_all_documents()       # Retrieve document library
remove_document()         # Document deletion
```

#### 📑 **`parser.py`** - Document Processing
Extracts and processes document content:
```python
# Key Functions
extract_text_from_pdf()   # PDF text extraction
extract_metadata()        # Document metadata extraction
clean_text()              # Text preprocessing
```

### **API Integration**

#### **Google Gemini Configuration**
```python
# Environment Variables
GEMINI_API_KEY = "your-api-key"
GEMINI_MODEL = "gemini-2.0-flash"

# Rate Limiting
MAX_RETRIES = 3
TIMEOUT = 45
MAX_INPUT_LENGTH = 30000
```

---

## 🎯 Use Cases

### **📋 Business & Professional**
- **Meeting Notes Analysis**: Extract action items and decisions
- **Contract Review**: Identify key terms and obligations
- **Project Documentation**: Summarize requirements and deliverables
- **Business Reports**: Extract KPIs and insights

### **🎓 Academic & Research**
- **Research Paper Analysis**: Understand methodology and findings
- **Literature Review**: Extract key concepts and citations
- **Thesis Documentation**: Organize chapters and references
- **Academic Planning**: Track progress and deadlines

### **💼 HR & Recruitment**
- **Resume Screening**: ATS compatibility analysis
- **Job Description Matching**: Skill gap identification
- **Candidate Assessment**: Qualification evaluation
- **Interview Preparation**: Key talking points extraction

### **⚖️ Legal & Compliance**
- **Legal Document Review**: Risk assessment and compliance
- **Policy Analysis**: Requirement extraction
- **Regulatory Documentation**: Compliance checking
- **Due Diligence**: Key information identification

---

## 🧠 AI Capabilities

### **Document Type Detection**
The AI automatically identifies document types with high accuracy:

| Document Type | Key Features Detected | Analysis Focus |
|---------------|----------------------|----------------|
| **Resume/CV** | Skills, experience, education | ATS optimization, gaps |
| **Meeting Notes** | Decisions, action items, attendees | Task extraction, follow-ups |
| **Legal Documents** | Terms, parties, obligations | Risk assessment, compliance |
| **Research Papers** | Methodology, findings, citations | Academic insights, applications |
| **Business Reports** | KPIs, metrics, recommendations | Strategic insights, actions |

### **Advanced NLP Features**
- **Semantic Understanding**: Contextual comprehension beyond keywords
- **Entity Recognition**: People, organizations, dates, locations
- **Sentiment Analysis**: Tone and emotion detection
- **Relationship Mapping**: Connections between concepts
- **Temporal Reasoning**: Timeline and sequence understanding

---

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional Performance Tuning
MAX_RETRIES=3
TIMEOUT=45
MAX_INPUT_LENGTH=30000
```

### **Streamlit Configuration**
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
maxUploadSize = 200
enableXsrfProtection = true
```

### **Advanced Settings**
```python
# Gemini Model Configuration
TEMPERATURE = 0.7        # Creativity level (0.0-1.0)
MAX_TOKENS = 2048       # Response length limit
TOP_P = 0.8             # Nucleus sampling
TOP_K = 40              # Top-k sampling
```

---

## 📈 Performance

### **Benchmarks**
- **Document Processing**: < 3 seconds for typical PDFs
- **AI Analysis**: 5-15 seconds depending on document size
- **Memory Search**: < 1 second for semantic queries
- **UI Response**: Real-time for most interactions

### **Scalability**
- **Concurrent Users**: Optimized for individual use
- **Document Size**: Up to 10MB PDFs supported
- **Memory Usage**: Efficient chunking for large documents
- **API Limits**: Built-in rate limiting and retry logic

### **Optimization Features**
- **Intelligent Chunking**: Documents split for optimal processing
- **Caching**: Session-based caching for repeated queries
- **Lazy Loading**: Documents loaded on-demand
- **Error Recovery**: Graceful handling of API failures

---

## 🎓 Learning Journey

### **🚀 Technical Skills Developed**

#### **AI/ML Integration**
- **Large Language Models**: Practical implementation of Google Gemini
- **Prompt Engineering**: Crafting effective prompts for different document types
- **Vector Search**: Implementing semantic similarity with FAISS
- **NLP Techniques**: Text processing, entity extraction, and classification

#### **Software Engineering**
- **Clean Architecture**: Separation of concerns and modular design
- **Error Handling**: Robust exception management and user feedback
- **Testing**: Unit testing and integration testing strategies
- **Documentation**: Comprehensive code documentation and README

### **🛠️ Problem-Solving Highlights**

#### **Challenge 1: Memory Persistence**
**Problem**: Documents disappeared after browser refresh
**Solution**: Implemented pickle-based persistent storage with session state management

#### **Challenge 2: Large Document Processing**
**Problem**: API timeouts with large documents
**Solution**: Intelligent text chunking and progressive processing with user feedback

#### **Challenge 3: Context-Aware Q&A**
**Problem**: Generic responses not relevant to uploaded documents
**Solution**: Dynamic prompt engineering with document context injection

#### **Challenge 4: ATS Scoring Accuracy**
**Problem**: Generic resume analysis without industry specifics
**Solution**: Multi-criteria scoring system with job description matching

### **📚 Key Learnings**

1. **AI Integration Patterns**: Best practices for LLM integration in production apps
2. **User Experience Design**: Balancing AI complexity with intuitive interfaces
3. **Performance Optimization**: Techniques for responsive AI-powered applications
4. **Error Resilience**: Building robust systems that handle API failures gracefully
5. **Scalable Architecture**: Designing systems that can grow with user needs

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### **🐛 Bug Reports**
Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

### **✨ Feature Requests**
Have an idea? I'd love to hear it:
- Describe the feature and its benefits
- Provide use cases and examples
- Consider implementation complexity

### **🔧 Code Contributions**

#### **Getting Started**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper documentation
4. Add tests for new functionality
5. Commit with descriptive messages
6. Push and create a pull request

#### **Development Guidelines**
- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Include type hints where appropriate
- Add unit tests for new features
- Update documentation as needed

#### **Areas for Contribution**
- **New Document Types**: Add support for additional formats
- **AI Improvements**: Enhance analysis accuracy and insights
- **UI/UX Enhancements**: Improve user interface and experience
- **Performance Optimization**: Speed improvements and resource efficiency
- **Integration Features**: Add new API integrations and services

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 💬 Final Thoughts

> *"The future of document analysis isn't just about reading text—it's about understanding context, extracting insights, and empowering users to make informed decisions. This AI Document Assistant represents a step toward that future, where artificial intelligence becomes a true partner in knowledge work."*

### **🌟 Project Impact**

This project demonstrates the practical application of modern AI technologies in solving real-world problems. By combining the power of large language models with thoughtful user experience design, we've created a tool that doesn't just process documents—it understands them.

### **🚀 Future Vision**

The AI Document Assistant is more than just a document analyzer; it's a foundation for intelligent knowledge management. As AI continues to evolve, this platform will grow to support new document types, provide deeper insights, and offer more sophisticated analysis capabilities.

### **🤝 Community & Growth**

Built with love for the developer and AI community, this project serves as both a practical tool and a learning resource. Whether you're a student exploring AI integration, a developer building similar solutions, or a professional seeking document analysis capabilities, this project offers valuable insights and a solid foundation.

---

<div align="center">

**Made with ❤️ and powered by 🤖 AI**

*If this project helped you, please consider giving it a ⭐ on GitHub!*

[![GitHub Stars](https://img.shields.io/github/stars/yourusername/ai-document-assistant?style=social)](https://github.com/yourusername/ai-document-assistant)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/ai-document-assistant?style=social)](https://github.com/yourusername/ai-document-assistant)


</div>

---

*Last updated: July 2025*
