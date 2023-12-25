import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA

def setup_grpc_channel():
    """Setup gRPC channel and create a stub (client)."""
    channel = grpc.insecure_channel('localhost:50051')
    return vectordb_pb2_grpc.VectorDBStub(channel)

def utility_data_to_vectors(df):
    """Convert utility data into vectors using PCA."""
    rate_data = df[['comm_rate', 'ind_rate', 'res_rate']]
    n_samples, n_features = rate_data.shape
    n_components = min(3, n_features, n_samples)

    if n_samples > 1:
        pca = PCA(n_components=n_components)
        rate_vectors = pca.fit_transform(rate_data.values)
    else:
        rate_vectors = rate_data.values

    return rate_vectors

def write_utility_data_to_database(df, stub):
    """Process utility data and write to the database in batches."""
    rate_vectors = utility_data_to_vectors(df)
    batch_size = 150
    for i in range(0, len(df), batch_size):
        batch = vectordb_pb2.VectorBatchWriteRequest()
        for j in range(i, min(i + batch_size, len(df))):
            vector_list = rate_vectors[j].tolist()
            batch.vectors.append(
                vectordb_pb2.VectorWriteRequest(
                    key=f"utility_{df.iloc[j]['zip']}",
                    vector=vector_list
                )
            )
        response = stub.BatchWrite(batch)
        if response.success:
            print(f"Successfully wrote batch starting with ZIP {df.iloc[i]['zip']}")
        else:
            print(f"Failed to write batch starting with ZIP {df.iloc[i]['zip']}")

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

def detect_anomalies(df):
    """Detect anomalies in the utility data."""
    rate_data = df[['comm_rate', 'ind_rate', 'res_rate']].values
    iso_forest = IsolationForest(contamination=0.05)
    iso_forest.fit(rate_data)
    anomalies = iso_forest.predict(rate_data)
    return anomalies

def process_anomalies_for_optimization(df, stub):
    """Processes anomalies in the provided DataFrame for optimization opportunities."""
    for index, row in df[df['anomaly'] == -1].iterrows():
        anomaly_vector = utility_data_to_vectors(pd.DataFrame([row]))
        # Fetch similar rates and analyze only top 1 similar rate
        similar_rates = search_for_anomalies(anomaly_vector[0], stub)[:1]
        if similar_rates:
            similar_key = similar_rates[0][0]
            similar_df_row = df[df['zip'] == int(similar_key.split('_')[1])].iloc[0]
            print(f"Anomalous rate for ZIP {row['zip']}: {row.to_dict()}")
            print(f"Similar rate: ZIP {similar_df_row['zip']}, Data: {similar_df_row.to_dict()}")

        avg_comm_rate = df['comm_rate'].mean()
        avg_ind_rate = df['ind_rate'].mean()
        avg_res_rate = df['res_rate'].mean()

        if row['comm_rate'] > avg_comm_rate * 1.2:
            print(f"Recommendation: Review commercial rate for ZIP {row['zip']}.")
        elif row['ind_rate'] > avg_ind_rate * 1.2:
            print(f"Recommendation: Optimize industrial rate for ZIP {row['zip']}.")
        elif row['res_rate'] > avg_res_rate * 1.2:
            print(f"Recommendation: Investigate residential rate for ZIP {row['zip']}.")

def main():
    # Load IOU and non-IOU utility data into DataFrames
    iou_df = pd.read_csv('iou_zipcodes_2020.csv')
    non_iou_df = pd.read_csv('non_iou_zipcodes_2020.csv')

    stub = setup_grpc_channel()

    print("Processing IOU data...")
    write_utility_data_to_database(iou_df, stub)

    print("Processing non-IOU data...")
    write_utility_data_to_database(non_iou_df, stub)

    print("Detecting anomalies in IOU data...")
    iou_df['anomaly'] = detect_anomalies(iou_df)

    print("Detecting anomalies in non-IOU data...")
    non_iou_df['anomaly'] = detect_anomalies(non_iou_df)

    process_anomalies_for_optimization(iou_df, stub)
    process_anomalies_for_optimization(non_iou_df, stub)

if __name__ == '__main__':
    main()
