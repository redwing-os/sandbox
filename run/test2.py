import grpc
import vectordb_pb2
import vectordb_pb2_grpc

def run():
    # Assuming the server is running on localhost:50051
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = vectordb_pb2_grpc.VectorDBStub(channel)
        response = stub.Write(vectordb_pb2.VectorWriteRequest(key="exampleKey", vector=[1.0, 2.0, 3.0]))
        print("VectorDB client received: " + str(response))

if __name__ == '__main__':
    run()