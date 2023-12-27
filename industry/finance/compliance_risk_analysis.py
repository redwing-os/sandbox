import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
import time
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_grpc_channel():
    logging.info("Setting up gRPC channel.")
    channel = grpc.insecure_channel('localhost:50051')
    return vectordb_pb2_grpc.VectorDBStub(channel)

def complaints_to_vectors(df):
    logging.info("Converting complaint narratives to vectors using TF-IDF.")
    tfidf = TfidfVectorizer(max_features=100)  # Adjust max_features as needed
    narrative_vectors = tfidf.fit_transform(df['Consumer complaint narrative'].dropna()).toarray()
    return narrative_vectors

def write_complaints_to_database(df, stub):
    logging.info("Writing complaints to the database in batches.")
    # Drop NaN values and reset the index so it aligns with the narrative_vectors array
    df_clean = df.dropna(subset=['Consumer complaint narrative']).reset_index(drop=True)
    narrative_vectors = complaints_to_vectors(df_clean)
    
    _keyspace = "redwing_keyspace"
    _table = "vectors"
    batch_size = 10  # Adjust batch size as needed

    for i in range(0, len(df_clean), batch_size):
        batch = vectordb_pb2.VectorBatchWriteRequest(keyspace=_keyspace, table=_table)
        # Make sure the loop handles the final batch which may be smaller than batch_size
        for j in range(i, min(i + batch_size, len(df_clean))):
            vector_list = narrative_vectors[j - i].tolist()  # Adjust index to start from 0 for each batch
            batch.vectors.append(
                vectordb_pb2.VectorWriteRequest(
                    keyspace=_keyspace,
                    table=_table,                    
                    key=f"complaint_{df_clean.iloc[j]['Complaint ID']}",
                    vector=vector_list
                )
            )
        response = stub.BatchWrite(batch)
        logging.info(f"Batch {i//batch_size + 1} write status: {'Success' if response.success else 'Failure'}")

def rank_companies_by_complaints(df):
    logging.info("Ranking companies based on the number and severity of complaints.")
    df['Severity'] = df['Company response to consumer'].apply(lambda x: 1 if x == 'Closed with explanation' else 2)
    company_ranks = df.groupby('Company').agg({'Complaint ID':'count', 'Severity':'mean'}).sort_values(by=['Complaint ID', 'Severity'], ascending=[False, True])
    company_ranks.rename(columns={'Complaint ID':'Total Complaints', 'Severity':'Average Severity'}, inplace=True)
    return company_ranks

def detect_compliance_risks(df):
    logging.info("Using Isolation Forest to detect complaints that are outliers, potentially indicating compliance risks.")
    # Drop NaN values and reset the index to align with narrative_vectors
    df_clean = df.dropna(subset=['Consumer complaint narrative']).reset_index(drop=True)
    narrative_vectors = complaints_to_vectors(df_clean)
    iso_forest = IsolationForest(contamination=0.05)  # Adjust contamination as needed
    risks = iso_forest.fit_predict(narrative_vectors)
    df_clean['Risk'] = risks
    # Return only the outliers from the cleaned DataFrame
    return df_clean[df_clean['Risk'] == -1]

def main():
    logging.info("Starting the compliance risk analysis script.")
    start_time = time.time()

    try:
        # Load the complaint data into a DataFrame
        complaints_df = pd.read_csv('complaints.csv', low_memory=False)
        logging.info("Complaints data loaded successfully.")

        stub = setup_grpc_channel()

        # Write the complaint data to the vector database
        write_complaints_to_database(complaints_df, stub)

        # Rank companies by number and severity of complaints
        company_rankings = rank_companies_by_complaints(complaints_df)
        logging.info("Company rankings completed.")

        # Output the ranked list of companies to a CSV file
        company_rankings.to_csv('company_rankings.csv')
        logging.info("Company rankings outputted to CSV file.")

        # Detect potential compliance risks
        compliance_risks = detect_compliance_risks(complaints_df)
        logging.info("Detection of potential compliance risks completed.")
        
        # Output potential compliance risks to a CSV file
        compliance_risks.to_csv('compliance_risks.csv')
        logging.info("Potential compliance risks outputted to CSV file.")


    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Script run time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()
