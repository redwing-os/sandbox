import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import random

def process_papers(paper_texts):
    """Convert paper texts into semantic vectors."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    paper_vectors = model.encode(paper_texts)
    return paper_vectors

def main():
    # Setup gRPC channel and create a stub (client)
    channel = grpc.insecure_channel('localhost:50051')
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Example research papers
    papers = [
        "Deep Learning for Natural Language Processing",
        "Quantum Computing: An Introduction",
        "Climate Change and Renewable Energy Sources",
        # ... more papers ...
    ]

    # Process papers and write to the database
    paper_vectors = process_papers(papers)
    for i, vector in enumerate(paper_vectors):
        vector_bytes = vector.tobytes()
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"paper_{i}",
            vector=vector_bytes
        )
        stub.Write(write_data)

    # User's search query
    user_query = "Machine learning applications in healthcare"
    query_vector = process_papers([user_query])[0]

    # Search for semantically similar papers
    search_request = vectordb_pb2.VectorSearchRequest(
        query=query_vector.tobytes(),
        top_k=5,
        metric="cosine"  # Specify the metric here // cosine, euclidean, manhattan, pearson, jaccard
    )
    search_response = stub.Search(search_request)

    print("Top matching papers for your query:")
    for match in search_response.matches:
        print(f"Paper ID: {match.key} - Score: {match.score}")

if __name__ == '__main__':
    main()