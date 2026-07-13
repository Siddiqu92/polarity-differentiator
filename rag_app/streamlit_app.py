import os
import sys
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rag import FamilyOfficeRAG

st.set_page_config(
    page_title="Family Office Intelligence RAG",
    page_icon="🏢",
    layout="wide",
)

if "rag" not in st.session_state:
    with st.spinner("Loading RAG pipeline..."):
        rag = FamilyOfficeRAG()
        records = rag.load_data()
        rag.ingest_data(records)
        st.session_state.rag = rag
        all_offices_list = rag.get_all_offices()
        st.session_state.office_names = sorted(all_offices_list)

rag = st.session_state.rag
office_count = len(rag.get_all_offices())
chunk_count = rag.chunk_count()

st.title("🏢 Family Office Intelligence RAG")
st.markdown(f"**Query {office_count} verified family offices with semantic search**")
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Offices", office_count)
with col2:
    st.metric("Chunks", chunk_count)
with col3:
    st.metric("Coverage", "50 Countries")

st.divider()

st.markdown("### 🔍 Search Options")

selected_office = st.selectbox(
    "Option 1: Select an office",
    options=[""] + st.session_state.office_names,
    index=0,
    label_visibility="collapsed",
)

st.markdown("---")

search_query = st.text_input(
    "Option 2: Search by keyword",
    placeholder="e.g., 'Tech investments', 'California', 'Early-stage'",
    label_visibility="collapsed",
)

top_k = st.slider("Number of results", 1, 50, 10)

st.divider()

query_to_use = None
if selected_office:
    query_to_use = selected_office
elif search_query:
    query_to_use = search_query

if query_to_use:
    st.markdown(f"### Results for: **{query_to_use}**")
    
    with st.spinner("Searching..."):
        results = rag.search(query_to_use, top_k=top_k)
    
    if results:
        st.success(f"Found {len(results)} result(s)")
        
        for i, result in enumerate(results, 1):
            st.markdown(f"**#{i}. {result['id']}**")
            st.write(result["text"])
            
            if result.get("metadata"):
                with st.expander("Details"):
                    st.json(result["metadata"])
            
            st.divider()
    else:
        st.warning("No results found.")
else:
    st.info("Select an office or enter a search term to begin.")

st.markdown("---")
st.caption(f"✅ {office_count} offices | {chunk_count} chunks | Streamlit + ChromaDB")