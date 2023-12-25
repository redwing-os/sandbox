import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import struct
from sklearn.decomposition import PCA

# Set up gRPC channel and create a stub (client)
def setup_grpc_channel():
    """Setup gRPC channel and create a stub (client)."""
    channel = grpc.insecure_channel('localhost:50051')
    return vectordb_pb2_grpc.VectorDBStub(channel)

def utility_data_to_vectors(df):
    """Convert utility data into vectors using PCA."""
    rate_data = df[['comm_rate', 'ind_rate', 'res_rate']]

    # Check if the DataFrame has only one row or fewer features than n_components
    n_samples, n_features = rate_data.shape
    n_components = min(3, n_features, n_samples)

    if n_samples > 1:
        # Apply PCA only if there are more than one samples
        pca = PCA(n_components=n_components)
        rate_vectors = pca.fit_transform(rate_data.values)
    else:
        # If only one sample, return it as is without PCA
        rate_vectors = rate_data.values

    return rate_vectors

# Write utility data to the vector database
def write_utility_data_to_database(df, stub):
    """Process utility data and write to the database."""
    rate_vectors = utility_data_to_vectors(df)
    for i, vector in enumerate(rate_vectors):
        vector_list = vector.tolist()
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"utility_{df.iloc[i]['zip']}",  # Using ZIP code as a unique key
            vector=vector_list
        )
        response = stub.Write(write_data)
        if response.success:  # Check the correct field in the response
            print(f"Successfully wrote data for ZIP {df.iloc[i]['zip']}")
        else:
            print(f"Failed to write data for ZIP {df.iloc[i]['zip']}")

# Semantic search in the vector database
def search_for_anomalies(query_vector, stub):
    """Search for anomalous utility rates in the database."""
    search_request = vectordb_pb2.VectorSearchRequest(
        query=query_vector.tobytes(),
        top_k=10,  # Modify as needed to retrieve a suitable number of similar rates
        metric="cosine"
    )
    search_response = stub.Search(search_request)
    return [(match.key, match.score) for match in search_response.matches]

# Detect anomalies using Isolation Forest
def detect_anomalies(df):
    """Detect anomalies in the utility data."""
    rate_data = df[['comm_rate', 'ind_rate', 'res_rate']].values
    # Initialize Isolation Forest model
    iso_forest = IsolationForest(contamination=0.05)
    # Fit the model on the rate data
    iso_forest.fit(rate_data)
    # Predict anomalies (-1 for anomalies, 1 for normal data points)
    anomalies = iso_forest.predict(rate_data)
    return anomalies

# Main function to process the data and find optimization opportunities
def main():
    # Load IOU and non-IOU utility data into DataFrames (Pandas)
    iou_df = pd.read_csv('iou_zipcodes_2020.csv')  # File path for IOU data
    non_iou_df = pd.read_csv('non_iou_zipcodes_2020.csv')  # File path for non-IOU data
    
    # Set up the gRPC channel
    stub = setup_grpc_channel()

    # Write IOU utility data to the vector database
    print("Processing IOU data...")
    write_utility_data_to_database(iou_df, stub)

    # Write non-IOU utility data to the vector database
    print("Processing non-IOU data...")
    write_utility_data_to_database(non_iou_df, stub)

    # Detect anomalies in the IOU utility data
    print("Detecting anomalies in IOU data...")
    iou_anomaly_labels = detect_anomalies(iou_df)
    iou_df['anomaly'] = iou_anomaly_labels

    # Detect anomalies in the non-IOU utility data
    print("Detecting anomalies in non-IOU data...")
    non_iou_anomaly_labels = detect_anomalies(non_iou_df)
    non_iou_df['anomaly'] = non_iou_anomaly_labels

    # Process IOU data for optimization opportunities based on anomalies
    process_anomalies_for_optimization(iou_df, stub)

    # Process non-IOU data for optimization opportunities based on anomalies
    process_anomalies_for_optimization(non_iou_df, stub)

def process_anomalies_for_optimization(df, stub):
    """
    Processes anomalies in the provided DataFrame for optimization opportunities.
    Prints out the details of the anomalous rates and any similar rates found.
    """
    for index, row in df[df['anomaly'] == -1].iterrows():  # Loop through anomalous entries
        anomaly_vector = utility_data_to_vectors(pd.DataFrame([row]))
        similar_rates = search_for_anomalies(anomaly_vector[0], stub)
        
        print(f"Anomalous rates found for ZIP {row['zip']}:")
        for similar_rate in similar_rates:
            print(f"Similar rate found with key: {similar_rate[0]} and similarity score: {similar_rate[1]}")
        
        # Generate specific recommendations based on the anomalies detected
        avg_comm_rate = df['comm_rate'].mean()
        avg_ind_rate = df['ind_rate'].mean()
        avg_res_rate = df['res_rate'].mean()

        if row['comm_rate'] > avg_comm_rate * 1.2:  # Threshold for the commercial rate, adjust as necessary
            print(f"Recommendation: The commercial rate for ZIP {row['zip']} is significantly above average and may require a rate review.")
            # Add logic for energy-saving recommendations
        elif row['ind_rate'] > avg_ind_rate * 1.2:  # Threshold for the industrial rate
            print(f"Recommendation: The industrial rate for ZIP {row['zip']} is significantly above average and may benefit from energy optimization solutions.")
            # Add logic for energy-saving recommendations
        elif row['res_rate'] > avg_res_rate * 1.2:  # Threshold for the residential rate
            print(f"Recommendation: The residential rate for ZIP {row['zip']} is significantly above average. Consider investigating meter accuracy or offering energy-saving tips to consumers.")

        # Additional recommendations can be added here based on the anomaly type and utility needs

if __name__ == '__main__':
    main()

