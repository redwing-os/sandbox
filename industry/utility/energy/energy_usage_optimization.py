import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
import csv
import time

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
    _keyspace="redwing_keyspace"
    _table="vectors"
    for i in range(0, len(df), batch_size):
        batch = vectordb_pb2.VectorBatchWriteRequest()
        for j in range(i, min(i + batch_size, len(df))):
            vector_list = rate_vectors[j].tolist()
            batch.vectors.append(
                vectordb_pb2.VectorWriteRequest(
                    keyspace=_keyspace,
                    table=_table,
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
    anomaly_data = []  # List to store data for each anomaly

    # Calculate average rates for comparison
    avg_comm_rate = df['comm_rate'].mean()
    avg_ind_rate = df['ind_rate'].mean()
    avg_res_rate = df['res_rate'].mean()

    for index, row in df[df['anomaly'] == -1].iterrows():  # Loop through anomalous entries
        anomaly_vector = utility_data_to_vectors(pd.DataFrame([row]))
        similar_rates = search_for_anomalies(anomaly_vector[0], stub)[:1]  # Assuming you want only the top match

        anomaly_record = {
            "zip": row['zip'],
            "eiaid": row['eiaid'],
            "utility_name": row['utility_name'],
            "state": row['state'],
            "service_type": row['service_type'],
            "ownership": row['ownership'],
            "comm_rate": row['comm_rate'],
            "ind_rate": row['ind_rate'],
            "res_rate": row['res_rate'],
            "similar_zip": similar_rates[0][0] if similar_rates else None,
            "similar_data": similar_rates[0][1] if similar_rates else None
        }

        # Analyze why the rate is considered anomalous
        reasons = []
        if row['comm_rate'] > avg_comm_rate * 1.2:
            reasons.append("commercial rate significantly higher than average")
        if row['ind_rate'] > avg_ind_rate * 1.2:
            reasons.append("industrial rate significantly higher than average")
        if row['res_rate'] > avg_res_rate * 1.2:
            reasons.append("residential rate significantly higher than average")

        anomaly_reason = "; ".join(reasons) if reasons else "Rates differ significantly from typical values"
        anomaly_record["anomaly_reason"] = anomaly_reason
        anomaly_data.append(anomaly_record)

    return anomaly_data

def main():
    start_time = time.time()  # Start the timer
    
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

    # Collecting anomaly data
    iou_anomalies = process_anomalies_for_optimization(iou_df, stub)
    non_iou_anomalies = process_anomalies_for_optimization(non_iou_df, stub)

    all_anomalies = iou_anomalies + non_iou_anomalies

    # Write the anomaly data to a CSV file
    with open('anomaly_report.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=all_anomalies[0].keys())
        writer.writeheader()
        writer.writerows(all_anomalies)

    print("Anomaly report generated: anomaly_report.csv")

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    print(f"Script run time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()
