import sys
import os
import grpc
import importlib.util
import vectordb_pb2
import vectordb_pb2_grpc

def main():
    # Setup gRPC channel
    channel = grpc.insecure_channel('localhost:50051')

    # Create a stub (client)
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Define keyspace and table name
    _keyspace = "redwing_keyspace"
    _table = "vectors"

    # Prepare data for Write
    write_data = vectordb_pb2.VectorWriteRequest(
        keyspace=_keyspace,
        table=_table,
        key="vector_key_123",
        vector=[0.5, 1.2, 3.4]
    )

    # Testing Write Method
    write_response = stub.Write(write_data)
    print("Write response:", write_response)

    # Prepare data for Read
    read_data = vectordb_pb2.VectorReadRequest(
        keyspace=_keyspace,
        table=_table,
        key="vector_key_123"
    )

    # Testing Read Method
    read_response = stub.Read(read_data)
    print("Read response:", read_response)

    # Prepare data for Update
    update_data = vectordb_pb2.VectorUpdateRequest(
        keyspace=_keyspace,
        table=_table,
        key="vector_key_123",
        vector=[2.3, 4.5, 6.7]
    )

    # Testing Update Method
    update_response = stub.Update(update_data)
    print("Update response:", update_response)

    # Prepare data for Delete
    delete_data = vectordb_pb2.VectorDeleteRequest(
        keyspace=_keyspace,
        table=_table,
        key="vector_key_123"
    )

    # Testing Delete Method
    delete_response = stub.Delete(delete_data)
    print("Delete response:", delete_response)

    # Prepare data for Batch Write
    batch_write_data = vectordb_pb2.VectorBatchWriteRequest(
        keyspace=_keyspace,
        table=_table,    
        vectors=[
            vectordb_pb2.VectorWriteRequest(
                key="vector_key_456",
                vector=[4.5, 5.6, 6.7]
            ),
            vectordb_pb2.VectorWriteRequest(
                key="vector_key_789",
                vector=[7.8, 8.9, 9.0]
            )
        ]
    )

    # Testing Batch Write Method
    batch_write_response = stub.BatchWrite(batch_write_data)
    print("Batch Write response:", batch_write_response)

if __name__ == '__main__':
    main()
