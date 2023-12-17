import grpc
import vectordb_pb2
import vectordb_pb2_grpc

def run_tests():
    channel = grpc.insecure_channel('localhost:50051')
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Test Embed and Write operation
    # Example: converting a 3x3 matrix to a vector and storing it
    data_matrix = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0] # Example structured data
    rows, cols = 3, 3
    embed_and_write_request = vectordb_pb2.VectorEmbedAndWriteRequest(key="test_matrix", data=data_matrix, rows=rows, cols=cols)
    embed_and_write_response = stub.EmbedAndWrite(embed_and_write_request)
    assert embed_and_write_response.success, "Embed and Write operation failed"

    print("All tests passed successfully.")

if __name__ == "__main__":
    run_tests()
