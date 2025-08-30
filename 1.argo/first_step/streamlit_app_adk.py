"""
Streamlit Frontend for FloatChat-Minimal
Single-page app using Google ADK backend
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Any
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="FloatChat — Argo Assistant",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8001"

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources_used" not in st.session_state:
    st.session_state.sources_used = []
if "current_query" not in st.session_state:
    st.session_state.current_query = ""


def call_chat_api(query: str) -> Dict[str, Any]:
    """Call the chat API endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"query": query},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


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
        
        if columns and rows:
            st.subheader(name)
            df_data = {col: [row[i] if i < len(row) else "" for row in rows] 
                      for i, col in enumerate(columns)}
            st.dataframe(df_data)
            if note:
                st.caption(note)
    
    elif block_type == "links":
        name = block.get("name", "Links")
        items = block.get("items", [])
        
        if items:
            st.subheader(name)
            for item in items:
                title = item.get("title", "Link")
                url = item.get("url", "")
                source = item.get("source", "")
                
                if url:
                    st.markdown(f"🔗 [{title}]({url}) *({source})*")
    
    elif block_type == "warning":
        message = block.get("message_md", "")
        st.warning(message)


def main():
    """Main Streamlit app"""
    
    # Title and description
    st.title("🌊 FloatChat — Argo Assistant")
    st.markdown("*AI-powered assistant for ARGO oceanographic data discovery*")
    
    # Sidebar
    with st.sidebar:
        st.header("Session Info")
        
        # API health check
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if health_response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.warning("⚠️ API Issues")
        except Exception as e:
            st.info("ℹ️ API Starting... (refresh in a moment)")
            # Don't stop the app, just show info
        
        st.subheader("Supported Topics")
        st.markdown("""
        - **Program Overview**: What is Argo? How does it work?
        - **Indian Ocean Status**: Argo floats in Arabian Sea, Bay of Bengal
        - **Data Access**: How to download Argo profiles, GDAC portals
        - **Float Locations**: Finding nearby floats, interactive maps
        """)
        
        st.subheader("Example Queries")
        example_queries = [
            "What is the Argo program?",
            "How many Argo floats are in the Indian Ocean?",
            "Where can I download Argo temperature data?",
            "How do I find floats near my coordinates?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.current_query = query
        
        # Sources used in session
        if st.session_state.sources_used:
            st.subheader("Sources This Session")
            for source in st.session_state.sources_used[-5:]:  # Last 5 sources
                domain = source.get("source", "Unknown")
                st.caption(f"📄 {domain}")
    
    # Main chat interface
    st.subheader("Ask about Argo oceanographic data")
    
    # Chat input
    if "current_query" in st.session_state:
        user_input = st.text_input("Your question:", value=st.session_state.current_query)
        del st.session_state.current_query
    else:
        user_input = st.text_input("Your question:", placeholder="e.g., What variables does Argo measure?")
    
    # Process query
    if user_input:
        if st.button("Ask FloatChat", type="primary"):
            with st.spinner("🔍 Searching for the latest information..."):
                # Call API
                response = call_chat_api(user_input)
                
                if response:
                    # Store the conversation
                    st.session_state.messages.append({
                        "user": user_input,
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Update sources
                    sources = response.get("sources_used", [])
                    for source in sources:
                        if source not in st.session_state.sources_used:
                            st.session_state.sources_used.append(source)
    
    # Display conversation history
    if st.session_state.messages:
        st.subheader("Conversation")
        
        for i, msg in enumerate(reversed(st.session_state.messages[-3:])):  # Show last 3 exchanges
            # User message
            with st.chat_message("user"):
                st.write(f"**You:** {msg['user']}")
            
            # Assistant response
            with st.chat_message("assistant"):
                st.write("**FloatChat:**")
                
                response_data = msg["response"]
                
                # Render streamlit blocks
                blocks = response_data.get("streamlit_blocks", [])
                for block in blocks:
                    render_streamlit_block(block)
                
                # Show timestamp
                timestamp = msg.get("timestamp", "")
                if timestamp:
                    st.caption(f"*Response generated at {timestamp[:19]}*")
            
            if i < len(st.session_state.messages) - 1:
                st.divider()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("🏛️ **Owner:** INCOIS/MoES — PoC by DJ")
    
    with col2:
        st.caption("🔧 **Stack:** Google ADK + Streamlit")
    
    with col3:
        if st.button("Clear History"):
            st.session_state.messages = []
            st.session_state.sources_used = []
            st.rerun()


if __name__ == "__main__":
    main()
