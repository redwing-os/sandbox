import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import struct

def main():
    # Setup gRPC channel and create a stub (client)
    channel = grpc.insecure_channel('localhost:50051')
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Batch of transaction vectors
    transaction_vectors = [
        [100, 34, 16], [200, 21, 14], [150, 30, 18]  # Add more transactions as needed
    ]

    # Write vectors to the database
    for i, vector in enumerate(transaction_vectors):
        # Pack as float (f32 in Rust)
        vector_bytes = struct.pack(f'{len(vector)}f', *vector)
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"transaction_{i}",
            vector=vector_bytes
        )
        response = stub.Write(write_data)
        print(f"Write operation for transaction_{i} successful: {response}")

    # Read and collect transaction vectors for analysis
    collected_vectors = []
    for i in range(len(transaction_vectors)):
        read_data = vectordb_pb2.VectorReadRequest(key=f"transaction_{i}")
        response = stub.Read(read_data)

        if response.found:
            vector = response.vector  # vector is already a list of floats
            collected_vectors.append(vector)
        else:
            print(f"No vector found for transaction_{i}")

    # Rest of the anomaly detection logic...

if __name__ == '__main__':
    main()