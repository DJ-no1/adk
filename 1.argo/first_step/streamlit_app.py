"""
Streamlit Frontend for FloatChat-Minimal
Single-page app for ARGO oceanographic data assistance
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

# Configure page
st.set_page_config(
    page_title="FloatChat — Argo Assistant (Step 1)",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sources_used" not in st.session_state:
    st.session_state.sources_used = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def render_streamlit_block(block: Dict[str, Any]):
    """Render a Streamlit block based on its type"""
    block_type = block.get("type")
    
    if block_type == "text":
        style = block.get("style", "body")
        content = block.get("content_md", "")
        
        if style == "title":
            st.title(content)
        elif style == "subtitle":
            st.subheader(content)
        elif style == "caption":
            st.caption(content)
        else:  # body
            st.markdown(content)
    
    elif block_type == "metrics":
        items = block.get("items", [])
        if items:
            cols = st.columns(len(items))
            for i, item in enumerate(items):
                with cols[i]:
                    st.metric(
                        label=item.get("label", ""),
                        value=item.get("value", ""),
                        help=item.get("help")
                    )
    
    elif block_type == "table":
        name = block.get("name", "Table")
        columns = block.get("columns", [])
        rows = block.get("rows", [])
        note = block.get("note")
        
        st.subheader(name)
        if rows and columns:
            df_data = {}
            for i, col in enumerate(columns):
                df_data[col] = [row[i] if i < len(row) else "" for row in rows]
            
            st.dataframe(df_data, use_container_width=True)
        
        if note:
            st.caption(note)
    
    elif block_type == "links":
        name = block.get("name", "Links")
        items = block.get("items", [])
        
        st.subheader(name)
        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")
            source = item.get("source", "")
            
            if url:
                if source:
                    st.markdown(f"🔗 [{title}]({url}) - *{source}*")
                else:
                    st.markdown(f"🔗 [{title}]({url})")
    
    elif block_type == "warning":
        message = block.get("message_md", "")
        st.warning(message)
    
    else:
        st.error(f"Unknown block type: {block_type}")


def call_chat_api(query: str) -> Dict[str, Any]:
    """Call the chat API endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "query": query,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Chat API call failed: {e}")
        return {"error": str(e)}


def call_search_api(query: str, site_filter: List[str] = None, time_range: str = "year", top_k: int = 5) -> Dict[str, Any]:
    """Call the search API endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": query,
                "site_filter": site_filter,
                "time_range": time_range,
                "top_k": top_k
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Search API call failed: {e}")
        return {"error": str(e)}


def check_api_health() -> bool:
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🌊 FloatChat — Argo Assistant")
    st.caption("Step 1: Web Search-Based ARGO/INCOIS Data Discovery")
    
    # Check API status
    if not check_api_health():
        st.error("⚠️ API service is not running. Please start the FastAPI backend first.")
        st.code("python api.py")
        st.stop()
    
    # Sidebar with session info and sources
    with st.sidebar:
        st.header("Session Info")
        st.text(f"Session ID: {st.session_state.session_id}")
        st.text(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Sources used in this session
        if st.session_state.sources_used:
            st.header("Sources Used")
            unique_domains = set()
            for source in st.session_state.sources_used:
                domain = source.get("domain", "unknown")
                title = source.get("title", "")
                if domain not in unique_domains:
                    st.text(f"• {domain}")
                    unique_domains.add(domain)
        
        # API status
        st.header("System Status")
        if check_api_health():
            st.success("✅ API Online")
        else:
            st.error("❌ API Offline")
        
        # Intent examples
        st.header("Example Queries")
        example_queries = [
            "What is Argo and what variables does it measure?",
            "Status of Argo floats in Indian Ocean",
            "How to download Argo data?",
            "Find nearest Argo floats to coordinates"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.user_input = query
                st.rerun()
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Text input
        user_input = st.text_input(
            "Ask about ARGO floats, oceanographic data, or Indian Ocean observations:",
            value=st.session_state.get("user_input", ""),
            placeholder="e.g., What is the current status of Argo floats in the Arabian Sea?",
            key="main_input"
        )
    
    with col2:
        # Submit button
        submit_clicked = st.button("Ask FloatChat", type="primary", use_container_width=True)
    
    # Advanced search option
    with st.expander("🔍 Direct Search (Advanced)"):
        st.write("Bypass the agent and search directly:")
        
        search_col1, search_col2 = st.columns([2, 1])
        
        with search_col1:
            search_query = st.text_input("Search query:", placeholder="Argo temperature profiles")
        
        with search_col2:
            time_range = st.selectbox("Time range:", ["year", "month", "week", "any"])
        
        # Domain filter
        domain_options = [
            "incois.gov.in",
            "argo.ucsd.edu", 
            "euro-argo.eu",
            "ncei.noaa.gov",
            "ocean-ops.org",
            "ifremer.fr"
        ]
        
        selected_domains = st.multiselect("Filter domains (optional):", domain_options)
        
        search_clicked = st.button("Direct Search", key="direct_search")
        
        if search_clicked and search_query:
            with st.spinner("Searching..."):
                search_result = call_search_api(
                    query=search_query,
                    site_filter=selected_domains if selected_domains else None,
                    time_range=time_range,
                    top_k=5
                )
                
                if "error" not in search_result:
                    st.success(f"Found {len(search_result.get('results', []))} results")
                    
                    for result in search_result.get("results", []):
                        with st.container():
                            st.markdown(f"**{result.get('title', '')}**")
                            st.markdown(f"🔗 [{result.get('url', '')}]({result.get('url', '')})")
                            st.text(result.get("snippet", ""))
                            st.caption(f"Source: {result.get('source', '')}")
                            st.divider()
                else:
                    st.error(f"Search failed: {search_result['error']}")
    
    # Process main query
    if (submit_clicked or st.session_state.get("user_input")) and user_input:
        # Clear the session state input
        if "user_input" in st.session_state:
            del st.session_state.user_input
        
        # Add to chat history
        st.session_state.chat_history.append({
            "query": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Call API
        with st.spinner("Searching and analyzing..."):
            result = call_chat_api(user_input)
        
        if "error" not in result:
            # Display response blocks
            for block in result.get("streamlit_blocks", []):
                render_streamlit_block(block)
            
            # Update sources
            sources = result.get("sources_used", [])
            st.session_state.sources_used.extend(sources)
            
            # Display assistant summary in an expander
            summary = result.get("assistant_summary_md", "")
            if summary:
                with st.expander("📝 Assistant Summary"):
                    st.markdown(summary)
        
        else:
            st.error(f"Error: {result['error']}")
    
    # Chat history
    if st.session_state.chat_history:
        st.header("Recent Queries")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
            with st.expander(f"Query {len(st.session_state.chat_history) - i}: {chat['query'][:50]}..."):
                st.text(f"Time: {chat['timestamp']}")
                st.text(f"Query: {chat['query']}")
    
    # Footer
    st.divider()
    st.caption("FloatChat-Minimal v0.1.0 | INCOIS/MoES — PoC by DJ | Step 1: Web Search Only")
    
    # System constraints reminder
    with st.expander("ℹ️ System Information"):
        st.markdown("""
        **Current Constraints (Step 1):**
        - No authentication required (fully public)
        - All data comes from web search in this session
        - No local NetCDF parsing (links & summaries only)
        - No background processing
        
        **Supported Queries:**
        - Program overview and variables
        - Indian Ocean float status
        - Data access instructions
        - Finding nearby floats (guidance)
        """)


if __name__ == "__main__":
    main()
