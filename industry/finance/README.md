## Financial Institution Compliance Risk

```
python3 compliance_risk_analysis.py
```

To run enhanced analysis with additional criteria:

```
python3 compliance_enhanced_risk_analysis.py
```

This is a Python Script for analyzing institutional compliance risks using customer complaint data from the Consumer Financial Protection Bureau. 

It leverages machine learning to vectorize complaint narratives and employs anomaly detection to identify outliers that may indicate compliance risks.

Dataset can be found here: https://catalog.data.gov/dataset/consumer-complaint-database a `download.sh` file is provided for your convenience to get up and running quickly with this dataset.

## Download Dataset and Run Script

From the `sandbox/industry/finance` directory run the following:

```
sh download.sh

python3 industry/finance/compliance_enhanced_risk_analysis.py
```

Alternative download approach: 3gb complaints .csv file can be downloaded here: https://catalog.data.gov/dataset/consumer-complaint-database

Save the file locally in current directory as `complaints.csv` and run

```
python3 compliance_enhanced_risk_analysis.py
```

## Import Libraries

The script imports a set of libraries crucial for data processing, machine learning, and logging.

```
import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
import time
import logging
```

## Function: `setup_grpc_channel`

Establishes a gRPC channel for communication with the VectorDB service.

```
def setup_grpc_channel():
    channel = grpc.insecure_channel('localhost:50051')
    return vectordb_pb2_grpc.VectorDBStub(channel)
```

## Function: `complaints_to_vectors`

Converts complaint narratives into vector form using the TF-IDF method, preparing them for machine learning analysis.

```
def complaints_to_vectors(df):
    tfidf = TfidfVectorizer(max_features=100)  # Adjust max_features as needed
    narrative_vectors = tfidf.fit_transform(df['Consumer complaint narrative'].dropna()).toarray()
    return narrative_vectors
```

## Function: `write_complaints_to_database`

Writes the vectorized complaint data to VectorDB for persistent storage and analysis.

```
def write_complaints_to_database(df, stub):
    df_clean = df.dropna(subset=['Consumer complaint narrative']).reset_index(drop=True)
    narrative_vectors = complaints_to_vectors(df_clean)
    batch_size = 10  # Adjust batch size as needed
    for i in range(0, len(df_clean), batch_size):
        batch = vectordb_pb2.VectorBatchWriteRequest()
        for j in range(i, min(i + batch_size, len(df_clean))):
            vector_list = narrative_vectors[j - i].tolist()  # Adjust index to start from 0 for each batch
            batch.vectors.append(
                vectordb_pb2.VectorWriteRequest(
                    key=f"complaint_{df_clean.iloc[j]['Complaint ID']}",
                    vector=vector_list
                )
            )
        response = stub.BatchWrite(batch)
```

## Function: `calculate_risk_score`

Calculates a risk score for each complaint based on content analysis and the company's response.

```
def calculate_risk_score(complaint, company_response):
    risk_score = 0

    if isinstance(complaint, str):
        # Increase risk score based on specific issues in the complaint
        if 'discrimination' in complaint.lower():
            risk_score += 5
        if 'privacy' in complaint.lower():
            risk_score += 4
        if 'deceptive' in complaint.lower() or 'unfair' in complaint.lower():
            risk_score += 3
        if 'legal violation' in complaint.lower() or 'ethical violation' in complaint.lower():
            risk_score += 5
        if 'financial loss' in complaint.lower() or 'credit damage' in complaint.lower():
            risk_score += 4
        if 'frequent complaints' in complaint.lower():
            risk_score += 3

    if company_response == 'Closed with explanation':
        risk_score -= 1
    elif company_response != 'Closed with non-monetary relief':
        risk_score += 2

    return risk_score
```

## Function: `enhanced_compliance_risk_detection`

Applies the risk score calculation to the dataset, potentially incorporating additional criteria.

```
def enhanced_compliance_risk_detection(df):
    return df_clean[df_clean['Risk'] == -1]
        df['Risk_Score'] = df.apply(lambda row: calculate_risk_score(
        row['Consumer complaint narrative'],
        row['Company response to consumer'],
    ), axis=1)
    return df
```

## Function: `rank_companies_by_complaints`

Ranks companies by the number and severity of complaints, providing insights into overall compliance risk.

```
def rank_companies_by_complaints(df):
    df['Severity'] = df['Company response to consumer'].apply(lambda x: 1 if x == 'Closed with explanation' else 2)
    company_ranks = df.groupby('Company').agg({'Complaint ID':'count', 'Severity':'mean'}).sort_values(by=['Complaint ID', 'Severity'], ascending=[False, True])
    company_ranks.rename(columns={'Complaint ID':'Total Complaints', 'Severity':'Average Severity'}, inplace=True)
    return company_ranks
```

## Function: `detect_compliance_risks`

Uses the Isolation Forest algorithm to detect outlier complaints that may indicate significant compliance risks.

```
def detect_compliance_risks(df):
    df_clean = df.dropna(subset=['Consumer complaint narrative']).reset_index(drop=True)
    narrative_vectors = complaints_to_vectors(df_clean)
    iso_forest = IsolationForest(contamination=0.05)  
    risks = iso_forest.fit_predict(narrative_vectors)
    df_clean['Risk'] = risks
```

## Main Function

Coordinates the overall process from data ingestion to risk analysis, logging each step for auditing purposes.

```
if name == 'main':
main()
```

## Output

Outputs results to `enhanced_compliance_risks.csv` and `company_rankings.csv`  