import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import struct
import numpy as np
from sklearn.ensemble import IsolationForest
import random

def generate_transactions(num_normal, num_anomalous):
    """Generate normal and anomalous transactions."""
    transactions = []

    # Generate normal transactions
    for _ in range(num_normal):
        amount = random.uniform(10, 1000)  # Random transaction amount
        time = random.uniform(0, 24)       # Time of the transaction
        location = random.randint(0, 100)  # Location ID (example)
        transactions.append([amount, time, location])

    # Generate anomalous transactions
    for _ in range(num_anomalous):
        amount = random.uniform(5000, 10000)  # Larger amounts for anomalies
        time = random.uniform(0, 24)
        location = random.randint(0, 100)
        transactions.append([amount, time, location])

    return transactions

def main():
    # Setup gRPC channel and create a stub (client)
    channel = grpc.insecure_channel('localhost:50051')
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Generate transactions
    transactions = generate_transactions(50, 5)  # 50 normal and 5 anomalous

    # Write transactions to the database
    for i, transaction in enumerate(transactions):
        vector_bytes = struct.pack(f'{len(transaction)}f', *transaction)
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"transaction_{i}",
            vector=vector_bytes
        )
        response = stub.Write(write_data)
        print(f"Write operation for transaction_{i} successful: {response}")

    # Read and collect transaction vectors for analysis
    collected_transactions = []
    for i in range(len(transactions)):
        read_data = vectordb_pb2.VectorReadRequest(key=f"transaction_{i}")
        response = stub.Read(read_data)

        if response.found:
            transaction = response.vector  # Transaction vector
            collected_transactions.append(transaction)
        else:
            print(f"No transaction found for transaction_{i}")

    # Anomaly detection using Isolation Forest
    clf = IsolationForest(contamination=0.1)  # Adjust contamination as needed
    clf.fit(collected_transactions)
    scores = clf.decision_function(collected_transactions)
    anomalies = clf.predict(collected_transactions)

    for i, (score, anomaly) in enumerate(zip(scores, anomalies)):
        if anomaly == -1:  # -1 indicates an anomaly
            print(f"Anomalous transaction detected: Transaction_{i}, Score: {score}")

if __name__ == '__main__':
    main()
