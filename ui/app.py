"""
Gemini RAG Streamlit UI

A modern web interface for asking questions about your documents.
Connects to the Pathway RAG backend via REST API.
"""

import os
import requests
import streamlit as st
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Document Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for modern, clean design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Root variables */
    :root {
        --primary: #6366f1;
        --primary-hover: #4f46e5;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --bg-secondary: #f8fafc;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border: #e2e8f0;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header styles */
    .app-header {
        text-align: center;
        padding: 2rem 0 3rem;
    }

    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .app-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 400;
    }

    /* Question input styling */
    .stTextArea textarea {
        font-size: 1rem;
        border-radius: 12px;
        border: 2px solid var(--border);
        padding: 1rem;
        transition: border-color 0.2s;
    }

    .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.4);
    }

    /* Answer card */
    .answer-card {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
    }

    .answer-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        color: #a78bfa !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }

    .answer-content {
        font-size: 1.05rem;
        line-height: 1.8;
        color: #e2e8f0 !important;
    }

    /* Source cards */
    .source-card {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        transition: all 0.2s;
    }

    .source-card:hover {
        border-color: var(--primary);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }

    .source-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }

    .source-badge {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
    }

    .source-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.95rem;
    }

    .source-content {
        color: #475569 !important;
        font-size: 0.9rem;
        line-height: 1.6;
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        max-height: 200px;
        overflow-y: auto;
    }

    /* Status badge */
    .status-connected {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #ecfdf5;
        color: #059669;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .status-disconnected {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #fef2f2;
        color: #dc2626;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    /* Stats cards */
    .stat-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
    }

    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--primary);
    }

    .stat-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Sidebar */
    .css-1d391kg {
        background: #f8fafc;
    }

    /* Section headers */
    .section-header {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1.5rem 0 1rem;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    .app-footer a {
        color: var(--primary);
        text-decoration: none;
    }
    .answer-box{
        background-color: #000000;
            }
  

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 0.95rem;
    }

    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--primary);
    }
</style>
""", unsafe_allow_html=True)


def check_backend_status():
    """Check if the backend is connected and return stats."""
    try:
        response = requests.post(f"{BACKEND_URL}/v1/statistics", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None


def get_document_list():
    """Get list of indexed documents."""
    try:
        response = requests.post(f"{BACKEND_URL}/v2/list_documents", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


# Header
st.markdown("""
<div class="app-header">
    <div class="app-title">📚 Document Q&A</div>
    <div class="app-subtitle">Ask questions about your documents, powered by AI</div>
</div>
""", unsafe_allow_html=True)

# Check backend status
is_connected, stats = check_backend_status()

# Main layout - centered content
col_left, col_main, col_right = st.columns([1, 4, 1])

with col_main:
    # Status indicator
    if is_connected:
        file_count = stats.get("file_count", 0) if stats else 0
        st.markdown(f"""
        <div style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;">
            <span class="status-connected">● Connected</span>
            <span class="status-connected">📄 {file_count} documents indexed</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 2rem;">
            <span class="status-disconnected">● Disconnected - Backend unavailable</span>
        </div>
        """, unsafe_allow_html=True)

    # Question input
    question = st.text_area(
        "What would you like to know?",
        placeholder="Ask anything about your documents...",
        height=120,
        label_visibility="collapsed",
    )

    # Default context depth (number of document chunks to use)
    num_sources = 5

    # Submit button
    ask_clicked = st.button("Ask Question", type="primary", use_container_width=True, disabled=not is_connected)

    # Process question
    if ask_clicked:
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Searching documents..."):
                try:
                    payload = {
                        "prompt": question,
                        "return_context_docs": True,  # Always get context for confidence calculation
                    }

                    response = requests.post(
                        f"{BACKEND_URL}/v2/answer",
                        json=payload,
                        timeout=60,
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # Calculate confidence score based on context docs
                        confidence_score = 0.0
                        context_docs = result.get("context_docs", [])

                        if context_docs:
                            # Calculate confidence based on:
                            # 1. Number of relevant documents found
                            # 2. Text length of retrieved content (more content = higher confidence)
                            num_docs = min(len(context_docs), num_sources)
                            total_text_length = sum(len(doc.get("text", "")) for doc in context_docs[:num_sources])

                            # Base score from document count (max 50%)
                            doc_score = min(num_docs / num_sources, 1.0) * 50

                            # Content richness score (max 50%)
                            # Assume good content is around 2000+ chars total
                            content_score = min(total_text_length / 2000, 1.0) * 50

                            confidence_score = doc_score + content_score

                            # Adjust if answer indicates no information found
                            answer_text = result.get("response", "").lower()
                            if any(phrase in answer_text for phrase in ["i don't have", "no information", "cannot find", "not found", "i'm not able"]):
                                confidence_score = max(confidence_score * 0.3, 10)

                        confidence_score = min(confidence_score, 100)  # Cap at 100%

                        # Determine confidence level and color
                        if confidence_score >= 80:
                            confidence_color = "#10b981"  # Green
                            confidence_label = "High"
                        elif confidence_score >= 50:
                            confidence_color = "#f59e0b"  # Amber
                            confidence_label = "Medium"
                        else:
                            confidence_color = "#ef4444"  # Red
                            confidence_label = "Low"

                        # Display answer with confidence score
                        answer_text = result.get("response", "No answer could be generated.")
                        st.markdown(f"""
                        <div class="answer-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <div class="answer-label" style="margin-bottom: 0;">
                                    <span>✨</span> Answer
                                </div>
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 0.8rem; color: #94a3b8;">Confidence:</span>
                                    <span style="
                                        background: {confidence_color}20;
                                        color: {confidence_color};
                                        padding: 0.25rem 0.75rem;
                                        border-radius: 20px;
                                        font-size: 0.85rem;
                                        font-weight: 600;
                                    ">{confidence_score:.0f}% ({confidence_label})</span>
                                </div>
                            </div>
                            <div class="answer-content">{answer_text}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.error(f"Error: Unable to get response from the server.")

                except requests.exceptions.Timeout:
                    st.error("The request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the backend service.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Sidebar - Document Management
with st.sidebar:
    st.markdown("### 📄 Documents")

    docs = get_document_list()

    if docs:
        st.success(f"{len(docs)} documents indexed")

        st.markdown("---")

        for doc in docs[:15]:
            path = doc.get("path", "Unknown")
            filename = os.path.basename(path)
            st.markdown(f"• `{filename}`")

        if len(docs) > 15:
            st.caption(f"... and {len(docs) - 15} more")
    else:
        st.info("No documents indexed yet")
        st.caption("Add documents to the data/ folder and restart the backend.")

    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    st.caption(f"Backend: `{BACKEND_URL}`")

    if is_connected and stats:
        last_indexed = stats.get("last_indexed", 0)
        if last_indexed:
            try:
                dt = datetime.fromtimestamp(last_indexed)
                st.caption(f"Last indexed: {dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass

# Footer
st.markdown("""
<div class="app-footer">
    <p>Powered by <strong>Pathway</strong> • <strong>Gemini AI</strong> • <strong>Docling</strong></p>
</div>
""", unsafe_allow_html=True)
