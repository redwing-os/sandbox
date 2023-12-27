import sys
import streamlit as st
sys.path.append('../sample')  # Add the /sample directory to the Python path

from healthcare_semantic_search import process_papers, search_similar_papers, setup_grpc_channel

def streamlit_app():
    st.title("Healthcare Research Paper Search")

    # Setup gRPC channel
    stub = setup_grpc_channel()

    # Text input for user query
    user_query = st.text_input("Enter your search query related to healthcare research papers:")

    # Button to trigger the search
    if st.button("Search"):
        with st.spinner("Searching for similar papers..."):
            matches = search_similar_papers(user_query, stub)

            st.header("Top matching papers for your query:")
            for paper_id, score in matches:
                col1, col2 = st.columns([3, 1])  # Adjust the ratio of the column widths as needed
                with col1:
                    st.write(f"Paper ID: {paper_id}")  # You'll need to replace this with the actual title if you have it
                with col2:
                    st.write(f"Score: {score}")

if __name__ == "__main__":
    streamlit_app()
