"""Streamlit UI - Family Office Intelligence Demo"""
import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag import FamilyOfficeRAG

# Page config
st.set_page_config(
    page_title="Family Office Intelligence RAG",
    page_icon="🏢",
    layout="wide"
)

# Initialize RAG
if 'rag' not in st.session_state:
    with st.spinner("Loading RAG pipeline..."):
        rag = FamilyOfficeRAG()
        records = rag.load_data()
        rag.ingest_data(records)
        st.session_state.rag = rag

rag = st.session_state.rag

# Header
st.title("🏢 Family Office Intelligence RAG")
st.markdown("**Query 48+ verified family offices with semantic search**")
st.divider()

# Sidebar
with st.sidebar:
    st.header("📊 System Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Offices", len(rag.get_all_offices()))
    with col2:
        st.metric("Chunks", "192")

# Main query
query = st.text_input(
    "🔍 Query Family Offices:",
    placeholder="e.g., 'Tech investments in California'",
)

top_k = st.slider("Number of results", 1, 10, 5)

# Search
if query:
    with st.spinner("Searching..."):
        results = rag.search(query, top_k=top_k)
    
    st.markdown(f"### Results for: **{query}**")
    
    if results:
        for i, result in enumerate(results, 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{i}. {result['id']}**")
                st.write(result['text'])
                if result['metadata']:
                    with st.expander("📋 Details"):
                        for key, value in result['metadata'].items():
                            st.write(f"• **{key}**: {value}")
            with col2:
                relevance = max(0, 1 - result['distance'])
                st.metric("Relevance", f"{relevance*100:.0f}%")
            st.divider()
    else:
        st.warning("No results found.")

# Footer
st.markdown("---")
st.caption(f"✅ {len(rag.get_all_offices())} offices | 192 chunks | Streamlit + ChromaDB")
