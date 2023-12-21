import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import struct
import numpy as np
from sklearn.ensemble import IsolationForest
import random

def generate_log_data(num_entries):
    """Generate simulated network log data with additional features."""
    log_data = []
    for _ in range(num_entries):
        # Enhanced log data features
        request_size = random.uniform(100, 10000)  # Size of request
        response_time = random.uniform(0, 5)       # Response time in seconds
        error_code = float(random.randint(0, 1))   # 0 for normal, 1 for error, as float
        ip_address = float(random.randint(0, 255)) # Simulated IP address part, as float
        # Convert string data to numerical representations (example approach)
        url_endpoint = ['/login', '/api', '/home', '/user'].index(random.choice(['/login', '/api', '/home', '/user']))
        http_method = ['GET', 'POST', 'PUT', 'DELETE'].index(random.choice(['GET', 'POST', 'PUT', 'DELETE']))
        user_agent = ['browser', 'mobile', 'bot'].index(random.choice(['browser', 'mobile', 'bot']))
        failed_logins = float(random.randint(0, 5)) # Failed login attempts, as float

        log_data.append([request_size, response_time, error_code, 
                         ip_address, url_endpoint, http_method, 
                         user_agent, failed_logins])
    return log_data

def main(num_entries=1000):  # Default value set to 1000
    # Setup gRPC channel and create a stub (client)
    public_ip = "3.83.78.12"  # Replace with your EC2 instance's public IP
    channel = grpc.insecure_channel(f'{public_ip}:50051') # use <your_deployed_terraform_ip>:50051 for deployed sandbox environments 
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Generate log data
    log_data = generate_log_data(1000)  # 200 log entries

    # Write log data to the database
    for i, entry in enumerate(log_data):
        # Ensure all data are floats
        entry_as_floats = list(map(float, entry))
        vector_bytes = struct.pack(f'{len(entry_as_floats)}f', *entry_as_floats)
        write_data = vectordb_pb2.VectorWriteRequest(
            key=f"log_{i}",
            vector=vector_bytes
        )
        stub.Write(write_data)

    # Assuming each log entry should have 8 features
    feature_length = 8

    # Read and collect log data for analysis, removing padding
    collected_logs = []
    for i in range(len(log_data)):
        read_data = vectordb_pb2.VectorReadRequest(key=f"log_{i}")
        response = stub.Read(read_data)
        if response.found:
            vector_list = list(response.vector)[:feature_length]  # Slice to remove padding
            log_entry = np.array(vector_list)
            collected_logs.append(log_entry)

    # Anomaly detection using Isolation Forest
    clf = IsolationForest(contamination=0.05)
    clf.fit(collected_logs)
    anomalies = clf.predict(collected_logs)

    # Calculate mean feature values for normal and anomalous logs
    normal_logs = [collected_logs[i] for i in range(len(collected_logs)) if anomalies[i] != -1]
    anomalous_logs = [collected_logs[i] for i in range(len(collected_logs)) if anomalies[i] == -1]

    # Calculate mean feature values for normal and anomalous logs
    normal_mean = np.mean(normal_logs, axis=0)
    anomalous_mean = np.mean(anomalous_logs, axis=0)

    for i, anomaly in enumerate(anomalies):
        if anomaly == -1:  # -1 indicates an anomaly
            print(f"Threat log entry detected: Log_{i}")
            print("Features of this log:")
            print(collected_logs[i])
            print("Average features of normal logs:")
            print(normal_mean)
            print("Average features of threat logs:")
            print(anomalous_mean)
            print("---")
            
    # Collecting details of threat logs
    threat_details = []
    for i, anomaly in enumerate(anomalies):
        if anomaly == -1:  # -1 indicates an anomaly
            log_detail = {
                'log_id': f'Log_{i}',
                'features': collected_logs[i],
                'normal_mean': normal_mean,
                'anomalous_mean': anomalous_mean
            }
            threat_details.append(log_detail)

    return threat_details, normal_mean, anomalous_mean

if __name__ == '__main__':
    main()

##############################################################################
# Threat log entry detected: Log_976
# ----------------------------------------------------------------------------    
# Features of this log:
# [ 75. 194.   7.  70.  53. 252. 207.  62.]
# ----------------------------------------------------------------------------    
# Average features of normal logs:
# [127.74210526 124.93684211 127.74        68.93368421 127.47684211
#  123.34526316 113.20526316  63.53684211]
# ----------------------------------------------------------------------------    
# Average features of threat logs:
# [103.7  124.7  116.12  68.5  119.16 140.32 149.32  62.36]
# ----------------------------------------------------------------------------
##############################################################################
# request_size
# response_time
# error_code
# ip_address
# url_endpoint
# http_method
# user_agent
# failed_logins
##############################################################################        
# Threat Log Entry: Log_976
# ----------------------------------------------------------------------------
# Features of this log: [ 75. 194. 7. 70. 53. 252. 207. 62.]
# request_size: 75 (The size of the request is relatively small compared to the average of normal logs, which is around 127.74)
# response_time: 194 (This is significantly higher than the average response time in normal logs, suggesting a potential performance issue or anomaly)
# error_code: 7 (A non-zero value indicates an error; however, this value is significantly higher than expected for a binary error code, suggesting a 
# possible encoding issue or a different interpretation of this feature)
# ip_address: 70 (Part of an IP address, interpretation depends on how IP addresses are encoded)
# url_endpoint: 53 (The index corresponding to a specific URL endpoint, interpretation requires the mapping used during encoding)
# http_method: 252 (The index for HTTP method, this is unusually high and might indicate a rare or anomalous method, or a data encoding issue)
# user_agent: 207 (The index for user agent, interpretation requires the mapping used during encoding)
# failed_logins: 62 (A high number of failed login attempts, which could indicate a brute-force attack or some other form of suspicious activity)
# ----------------------------------------------------------------------------
# Interpretation and Considerations:
# ----------------------------------------------------------------------------    
# The features of the logs flagged as threats show some distinct differences from the averages of normal logs, particularly in response_time and failed_logins.
# Some values, particularly for error_code, url_endpoint, http_method, and user_agent, are unusually high and might not align with the expected ranges. This could 
# indicate either a data encoding/interpretation issue or genuinely anomalous values. The high failed_logins in both cases is a strong indicator of 
# suspicious activity, such as attempted security breaches. The interpretation relies heavily on the correct encoding and understanding of each feature, 
# especially for those features that are categorical or encoded in a non-standard way.
# In summary, these logs are flagged as threats due to their significant deviation from typical patterns in certain features, particularly in response time
# and failed login attempts. However, the interpretation of some features requires a review of the data encoding process and the mappings used for categorical data.
#    
##############################################################################      
# ----------------------------------------------------------------------------
      
    