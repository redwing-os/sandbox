import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import struct
import numpy as np
from sklearn.ensemble import IsolationForest
import random

def generate_log_data(num_entries):
    """Generate simulated network log data."""
    log_data = []
    for _ in range(num_entries):
        # Simulating log data features (e.g., request size, response time, error codes)
        request_size = random.uniform(100, 10000)  # Size of request
        response_time = random.uniform(0, 5)      # Response time in seconds
        error_code = random.randint(0, 1)         # 0 for normal, 1 for error
        log_data.append([request_size, response_time, error_code])
    return log_data

def main():
    # Setup gRPC channel and create a stub (client)
    channel = grpc.insecure_channel('localhost:50051')
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Generate log data
    log_data = generate_log_data(200)  # 200 log entries

    # Write log data to the database
    for i, entry in enumerate(log_data):
        vector_bytes = struct.pack(f'{len(entry)}f', *entry)
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"log_{i}",
            vector=vector_bytes
        )
        stub.Write(write_data)

    # Read and collect log data for analysis
    collected_logs = []
    for i in range(len(log_data)):
        read_data = vectordb_pb2.VectorReadRequest(key=f"log_{i}")
        response = stub.Read(read_data)
        if response.found:
            vector_list = list(response.vector)
            log_entry = np.array(vector_list)
            collected_logs.append(log_entry)

    # Anomaly detection using Isolation Forest
    clf = IsolationForest(contamination=0.05)  # Adjust contamination as needed
    clf.fit(collected_logs)
    anomalies = clf.predict(collected_logs)

    for i, anomaly in enumerate(anomalies):
        if anomaly == -1:  # -1 indicates an anomaly
            print(f"Anomalous log entry detected: Log_{i}")

if __name__ == '__main__':
    main()
