import streamlit as st
import requests

# Base URL of your FastAPI server
API_URL = "http://localhost:8000/query/"

st.title("ChatDB: Natural Language Interface to Databases")

st.markdown("""
Welcome to **ChatDB 45**!  
Type your question in natural language, and we'll handle the rest — converting it to SQL/Mongo, executing it, and showing you the results.
""")

# Input for Natural Language Query
nl_query = st.text_area("🔍 Enter Your Natural Language Query")

if st.button("Run Query"):
    if not nl_query.strip():
        st.warning("⚠️ Please enter a valid query.")
    else:
        with st.spinner("Processing your query..."):
            try:
                response = requests.post(API_URL, json={"nl_query": nl_query})
                if response.status_code == 200:
                    st.success("✅ Query Executed Successfully!")
                    result = response.json()
                    st.markdown("### 📄 Result:")
                    st.json(result)
                else:
                    st.error(f"❌ Error: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚨 Connection Error: {e}")
