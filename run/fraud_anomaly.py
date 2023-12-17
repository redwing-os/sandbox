import grpc
import vectordb_pb2
import vectordb_pb2_grpc

# Additional imports for fraud detection logic
from sklearn.ensemble import IsolationForest
import numpy as np

def main():
    # Setup gRPC channel
    channel = grpc.insecure_channel('localhost:50051')

    # Create a stub (client)
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Let's assume we have a batch of transaction vectors
    transaction_vectors = [
        [100, 34, 16],  # Example vector format [amount, location_id, hour_of_day]
        [200, 21, 14],  # More vectors representing different transactions
        [150, 30, 18],  # ...
        # Add more transactions as needed
    ]

    # Write transaction vectors to the vector database
    for i, vector in enumerate(transaction_vectors):
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"transaction_{i}",
            vector=vector
        )
        response = stub.Write(write_data)
        print(f"Write operation for transaction_{i} successful: {response}")  # Debugging line

    # Read and collect transaction vectors for analysis
    collected_vectors = []
    for i in range(len(transaction_vectors)):
        read_data = vectordb_pb2.VectorReadRequest(key=f"transaction_{i}")
        response = stub.Read(read_data)
        print(f"Read response for transaction_{i}: {response}")  # Inspect the response

        # Modify this part based on the actual structure of the response
        if response.found:
            vector = response.vector  # Adjust this line as needed to correctly extract the vector
            collected_vectors.append(vector)
        else:
            print(f"No vector found for transaction_{i}")

    # Check if collected_vectors is populated correctly
    print(f"Collected Vectors: {collected_vectors}")

    # Ensure that collected_vectors is not empty and correctly formatted
    print(f"Collected Vectors: {collected_vectors}")  # Debugging line

    # Convert to numpy array for processing
    transaction_array = np.array(collected_vectors)
    print(f"Transaction Array Shape: {transaction_array.shape}")  # Debugging line

    # Fraud Detection using Isolation Forest
    # Convert to numpy array for processing
    transaction_array = np.array(collected_vectors)
    clf = IsolationForest(random_state=42)
    clf.fit(transaction_array)

    # Detecting anomalies (potential frauds)
    anomaly_scores = clf.decision_function(transaction_array)
    anomalies = anomaly_scores < 0  # Anomalies are scored less than 0

    # Print potential fraud transactions
    print("Potential Fraud Transactions:")
    for i, is_anomaly in enumerate(anomalies):
        if is_anomaly:
            print(f"Transaction {i} is potentially fraudulent.")

if __name__ == '__main__':
    main()

