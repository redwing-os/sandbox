import grpc
import vectordb_pb2
import vectordb_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
import datetime

def get_current_timestamp():
    now = datetime.datetime.utcnow()
    seconds = int(now.timestamp())
    nanos = int((now - datetime.datetime.fromtimestamp(seconds)).microseconds * 1000)
    return Timestamp(seconds=seconds, nanos=nanos)

def run():
    # Assuming the server is running on localhost:50051
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = vectordb_pb2_grpc.VectorDBStub(channel)

        # Create current timestamps for created_at and updated_at
        current_timestamp = get_current_timestamp()

        # Create and send the write request
        response = stub.Write(
            vectordb_pb2.VectorWriteRequest(
                key="exampleKey", 
                vector=[1.0, 2.0, 3.0]
                # created_at=current_timestamp, 
                # updated_at=current_timestamp
            )
        )
        print("VectorDB client received: " + str(response))

if __name__ == '__main__':
    run()
