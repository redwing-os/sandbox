import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import struct
import numpy as np
import random
from sklearn.neighbors import NearestNeighbors

def generate_user_profiles(num_users, num_products):
    """Generate user profiles with product ratings."""
    user_profiles = []
    for _ in range(num_users):
        profile = [random.uniform(0, 5) for _ in range(num_products)]  # 0-5 rating for each product
        user_profiles.append(profile)
    return user_profiles

def main():
    # Setup gRPC channel and create a stub (client)
    channel = grpc.insecure_channel('localhost:50051')
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Generate user profiles
    user_profiles = generate_user_profiles(100, 20)  # 100 users, 20 products

    # Write user profiles to the database
    for i, profile in enumerate(user_profiles):
        vector_bytes = struct.pack(f'{len(profile)}f', *profile)
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"user_{i}",
            vector=vector_bytes
        )
        response = stub.Write(write_data)
        print(f"Write operation for user_{i} successful: {response}")

    # Read and collect user profiles for recommendation
    collected_profiles = []
    for i in range(len(user_profiles)):
        read_data = vectordb_pb2.VectorReadRequest(key=f"user_{i}")
        response = stub.Read(read_data)

        if response.found:
            # Convert the RepeatedScalarContainer to a list, then to a numpy array
            vector_list = list(response.vector)
            profile = np.array(vector_list)
            collected_profiles.append(profile)
        else:
            print(f"No profile found for user_{i}")

    # Product recommendation using Nearest Neighbors
    model = NearestNeighbors(n_neighbors=3)  # Finds the 3 nearest neighbors
    model.fit(collected_profiles)

    # Recommend products for a specific user
    user_id = 0  # Example user
    distances, indices = model.kneighbors([collected_profiles[user_id]])
    recommended_products = set()
    for index in indices[0]:
        if index != user_id:
            recommended_products.update(np.nonzero(collected_profiles[index])[0])
    print(f"Recommended products for user_{user_id}: {recommended_products}")

if __name__ == '__main__':
    main()
