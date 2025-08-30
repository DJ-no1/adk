"""
Test script to verify Streamlit functionality
"""

import streamlit as st
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

st.title("🌊 FloatChat-Minimal Test")
st.write("Testing basic Streamlit functionality...")

# Test session state
if "test_counter" not in st.session_state:
    st.session_state.test_counter = 0

st.write(f"Session state working: {st.session_state.test_counter}")

# Test text input
user_input = st.text_input("Test input:", placeholder="Type something...")

if user_input:
    st.write(f"You typed: {user_input}")
    st.session_state.test_counter += 1

# Test imports
try:
    from agent_adk import floatchat_agent, floatchat_minimal
    st.success("✅ Agent imports working")
    
    # Test intent classification
    if user_input:
        intent = floatchat_minimal.classify_intent(user_input)
        st.info(f"Intent classified as: {intent}")
        
except Exception as e:
    st.error(f"❌ Import error: {e}")

st.info("Basic Streamlit test complete!")
