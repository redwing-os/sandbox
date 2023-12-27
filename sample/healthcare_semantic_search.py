import grpc
import vectordb_pb2
import vectordb_pb2_grpc
from sentence_transformers import SentenceTransformer

def process_papers(paper_texts):
    """Convert paper texts into semantic vectors."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    paper_vectors = model.encode(paper_texts)
    return paper_vectors

def write_papers_to_database(papers, stub):
    """Process papers and write to the database."""
    
    paper_vectors = process_papers(papers)
    for i, vector in enumerate(paper_vectors):
        vector_bytes = vector.tobytes()
        # Define keyspace and table name
        _keyspace = "redwing_keyspace"
        _table = "vectors"

        # Prepare data for Write
        write_data = vectordb_pb2.VectorWriteRequest(
            keyspace=_keyspace,
            table=_table,
            key=f"paper_{i}",
            vector=vector_bytes
        )
        stub.Write(write_data)

def search_similar_papers(query, stub):
    """Search for semantically similar papers."""
    query_vector = process_papers([query])[0]
    # Define keyspace and table name
    _keyspace = "redwing_keyspace"
    _table = "vectors"
    search_request = vectordb_pb2.VectorSearchRequest(
        query=query_vector.tobytes(),
        top_k=5,
        metric="cosine",
        keyspace=_keyspace,
        table=_table,        
    )
    search_response = stub.Search(search_request)
    return [(match.key, match.score) for match in search_response.matches]

def setup_grpc_channel():
    """Setup gRPC channel and create a stub (client)."""
    channel = grpc.insecure_channel('localhost:50051')
    return vectordb_pb2_grpc.VectorDBStub(channel)

def main():
    # Example research papers
    papers = [
        "Evaluating the Impact of Machine Learning on Healthcare Outcomes",
        "Advancements in Deep Learning for Medical Image Analysis",
        "The Role of Artificial Intelligence in Predicting Epidemic Outbreaks",
        # ... more real papers ...
    ]

    stub = setup_grpc_channel()
    write_papers_to_database(papers, stub)  # Write papers to the database

    # User's search query (this would be replaced by user input in a Streamlit app)
    user_query = "Machine learning applications in healthcare"
    matches = search_similar_papers(user_query, stub)

    print("Top matching papers for your query:")
    for paper_id, score in matches:
        print(f"Paper ID: {paper_id} - Score: {score}")

if __name__ == '__main__':
    main()
