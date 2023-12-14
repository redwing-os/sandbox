import sys
import os
import grpc
import importlib.util
import vectordb_pb2
import vectordb_pb2_grpc

def run():
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = vectordb_pb2_grpc.VectorDBStub(channel)
            response = stub.Write(vectordb_pb2.VectorWriteRequest(key="exampleKey", vector=[1.0, 2.0, 3.0]))
            print("VectorDB client received: " + str(response))
    except grpc.RpcError as e:
        print(f"gRPC call failed: {e.details()}")
        status_code = e.code()
        print(f"Status code: {status_code.name}, {status_code.value}")

if __name__ == '__main__':
    run()
