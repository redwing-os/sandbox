import os
import grpc
import pandas_gbq
import vectordb_pb2
import vectordb_pb2_grpc
import pandas as pd
import pandas_gbq
from google.oauth2 import service_account
from sklearn.ensemble import IsolationForest
import time
import logging
import numpy
from dotenv import load_dotenv
import requests
import hmac
import hashlib

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Coinbase API information
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')
COINBASE_PASSPHRASE = os.getenv('COINBASE_PASSPHRASE')
COINBASE_PORTFOLIO_ID = os.getenv('COINBASE_PORTFOLIO_ID')

# Coinbase API URLs
COINBASE_API_URL = "https://api.coinbase.com/api/v3/brokerage"

def create_coinbase_signature(timestamp, method, request_path, body=''):
    """
    Creates a signature for a Coinbase API request.
    """
    message = str(timestamp) + method + request_path + (body or '')
    hmac_key = base64.b64decode(COINBASE_API_SECRET)
    signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
    return signature.hexdigest()

def coinbase_request(method, endpoint, body=None):
    """
    Makes a request to the Coinbase API.
    """
    timestamp = int(time.time())
    request_path = f"/{endpoint}"
    full_url = COINBASE_API_URL + request_path
    signature = create_coinbase_signature(timestamp, method, request_path, body)

    headers = {
        'CB-ACCESS-KEY': COINBASE_API_KEY,
        'CB-ACCESS-SIGN': signature,
        'CB-ACCESS-TIMESTAMP': str(timestamp),
        'CB-ACCESS-PASSPHRASE': COINBASE_PASSPHRASE,
        'Content-Type': 'application/json'
    }

    if method == 'GET':
        response = requests.get(full_url, headers=headers)
    elif method == 'POST':
        response = requests.post(full_url, headers=headers, data=body)
    else:
        raise ValueError("Invalid HTTP method specified")

    return response.json()

def get_market_data(product_id):
    """
    Fetches current market data for a specified product.
    """
    endpoint = f"products/{product_id}/ticker"
    return coinbase_request('GET', endpoint)

def place_trade(product_id, side, amount):
    """
    Places a trade order on Coinbase.
    """
    endpoint = "orders"
    body = {
        'portfolio_id': COINBASE_PORTFOLIO_ID,
        'product_id': product_id,
        'side': side,
        'funds': amount
    }
    return coinbase_request('POST', endpoint, body=json.dumps(body))

def volume_analysis(df):
    logging.info("Analyzing transaction volumes.")
    df['block_date'] = df['block_timestamp'].dt.date
    daily_volume = df.groupby('block_date')['value_eth'].sum()
    return daily_volume

def address_analysis(df):
    logging.info("Analyzing address activity.")
    address_activity = df.groupby('from_address')['value_eth'].agg(['count', 'sum']).sort_values(by='sum', ascending=False)
    return address_activity
def setup_grpc_channel():
    logging.info("Setting up gRPC channel.")
    channel = grpc.insecure_channel('localhost:50051')
    return vectordb_pb2_grpc.VectorDBStub(channel)

def fetch_data_from_bigquery():
    logging.info("Fetching data from BigQuery.")
        
    # Load the environment variables from the .env file
    load_dotenv()

    query = """
        SELECT 
            nonce,
            from_address,
            to_address,
            CAST(value AS FLOAT64) / POW(10, 18) AS value_eth,
            gas,
            receipt_cumulative_gas_used,
            receipt_effective_gas_price,
            block_timestamp,
            block_number,
            CASE receipt_status WHEN 1 THEN 'Success' ELSE 'Failure' END AS status
        FROM `bigquery-public-data.crypto_ethereum.transactions`
        WHERE DATE(block_timestamp) = "2023-12-27"
        LIMIT 1000
    """

    # Construct a dictionary for the service account credentials
    service_account_info = {
        "type": "service_account",
        "project_id": "vector-sandbox",
        "private_key_id": "0826950ebad2a467ad7083d5f13df15e5c6c7948",
        "private_key": os.getenv("BIGQUERY_PRIVATE_KEY"),
        "client_email": "vector@vector-sandbox.iam.gserviceaccount.com",
        "client_id": "111349678665442531010",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vector%40vector-sandbox.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    # Ensure the private key is present
    if service_account_info["private_key"] is None:
        raise Exception("The 'BIGQUERY_PRIVATE_KEY' environment variable is not set.")

    # Construct a BigQuery client object using the credentials
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    # Run the BigQuery query and return the dataframe
    df = pandas_gbq.read_gbq(query, credentials=credentials)

    # Print the dataframe to check if it's correct
    print(df.head())
    print(df.columns)

    return df

def analyze_data(df):
    logging.info("Analyzing data for potential trades.")
    # Anomaly detection based on volume
    anomaly_detection = IsolationForest(n_estimators=100)
    df['anomaly_score'] = anomaly_detection.fit_predict(df[['value_eth']])
    anomalies = df[df['anomaly_score'] == -1]
    return anomalies

def calculate_macd(prices, short_window=12, long_window=26, signal=9):
    """
    Calculate MACD and MACD Signal line.
    """
    short_ema = prices.ewm(span=short_window, adjust=False).mean()
    long_ema = prices.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    macd_signal = macd.ewm(span=signal, adjust=False).mean()

    return macd, macd_signal

def fetch_historical_data(symbol, convert='USD', limit=100):
    """
    Fetch historical price data for the specified cryptocurrency.
    """
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"
    parameters = {
        'symbol': symbol,
        'convert': convert,
        'limit': limit
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }

    try:
        response = requests.get(url, headers=headers, params=parameters)
        response.raise_for_status()
        data = response.json()
        prices = pd.DataFrame(data['data']['quotes'])
        prices['timestamp'] = pd.to_datetime(prices['timestamp'])
        prices.set_index('timestamp', inplace=True)
        prices = prices['quote'][convert]['price']
        return prices
    except Exception as e:
        logging.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()
    
def get_crypto_price(symbol, convert='USD'):
    """
    Fetches the latest price of a cryptocurrency from CoinMarketCap.
    """
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {
        'slug': symbol.lower(),
        'convert': convert
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }

    try:
        response = requests.get(url, headers=headers, params=parameters)
        response.raise_for_status()  # This will check for HTTPError
        data = response.json()

        # Extract the first ID found in the data
        first_id = list(data['data'].keys())[0]

        if first_id in data['data']:
            price_info = data['data'][first_id]['quote'][convert]
            return price_info['price']
        else:
            logging.error("Invalid data format received from API.")
            return None
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
    except Exception as e:
        logging.error(f"Error fetching cryptocurrency price: {e}")

    return None
    
def preprocess_and_vectorize(df):
    logging.info("Preprocessing and vectorizing data.")
    
    # Correct column names according to the DataFrame
    df['gas_normalized'] = df['gas'] / df['gas'].max()
    df['value_eth_normalized'] = df['value_eth'] / df['value_eth'].max()
    df['receipt_effective_gas_price_normalized'] = df['receipt_effective_gas_price'] / df['receipt_effective_gas_price'].max()

    # Convert to numpy array for vectorization
    features = [
        'gas_normalized',
        'value_eth_normalized',
        'receipt_effective_gas_price_normalized'
    ]
    vectors = df[features].to_numpy()

    return vectors

def batch_write_data_to_vector_db(vectors, df, stub, batch_size=10): # sets default batch size to 100 as fallback
    logging.info("Writing data to the vector database in batches.")
    
    _keyspace = "redwing_keyspace"
    _table = "vectors"

    total_vectors = len(vectors)
    for start_idx in range(0, total_vectors, batch_size):
        batch = vectordb_pb2.VectorBatchWriteRequest(keyspace=_keyspace, table=_table)
        end_idx = min(start_idx + batch_size, total_vectors)

        for i in range(start_idx, end_idx):
            unique_key = str(df.iloc[i]['nonce']) + '_' + str(df.iloc[i]['from_address'])
            vector_list = vectors[i].tolist() if isinstance(vectors[i], numpy.ndarray) else list(vectors[i])

            vector_req = vectordb_pb2.VectorWriteRequest(
                key=unique_key,
                vector=vector_list
            )
            batch.vectors.append(vector_req)

        response = stub.BatchWrite(batch)
        if response.success:
            logging.info(f"Batch {start_idx // batch_size + 1} written successfully.")
        else:
            logging.error(f"Failed to write batch {start_idx // batch_size + 1}: {response.error_message}")

        # Optional: Print progress
        print(f"Processed {end_idx} / {total_vectors} vectors")


def write_data_to_vector_db(vectors, df, stub):
    logging.info("Writing data to the vector database individually.")

    for i, vector in enumerate(vectors):
        unique_key = str(df.iloc[i]['nonce']) + '_' + str(df.iloc[i]['from_address'])
        # Convert vector to list if it's numpy array
        vector_list = vector.tolist() if isinstance(vector, numpy.ndarray) else list(vector)
        vector_req = vectordb_pb2.VectorWriteRequest(
            keyspace="redwing_keyspace",
            table="vectors",
            key=unique_key,
            vector=vector_list  # This should be a list of floats
        )

        try:
            # Send individual write request
            response = stub.Write(vector_req)
            if response.success:
                logging.info(f"Data for key {unique_key} written to vector database successfully.")
            else:
                logging.error(f"Failed to write data for key {unique_key} to vector database.")
        except grpc.RpcError as e:
            logging.error(f"An RPC error occurred: {e.details()}")
            
def main():
    logging.info("Starting the trading algorithm script.")
    start_time = time.time()

    try:
        stub = setup_grpc_channel()
        df = fetch_data_from_bigquery()
        logging.info("Data fetched successfully.")
        
        vectors = preprocess_and_vectorize(df)
        batch_write_data_to_vector_db(vectors, df, stub, 10)
        # Perform analyses
        anomalies = analyze_data(df)
        daily_volume = volume_analysis(df)
        active_addresses = address_analysis(df)

        # Output results or make recommendations based on the analyses
        print("Anomalies:")
        print(anomalies.head())
        print("\nDaily Volume:")
        print(daily_volume.head())
        print("\nActive Addresses:")
        print(active_addresses.head())

        # Fetch the latest price of Ethereum (ETH)
        eth_price = get_crypto_price('ethereum')
        logging.info(f"Current Ethereum price: {eth_price}")        

        # Display the latest Ethereum price and MACD values
        logging.info(f"Current Ethereum price: {eth_price}")

        # Calculate MACD
        # eth_historical = fetch_historical_data('ethereum', limit=100)         # requires upgraded CoinMarketCap Plan
        # macd, macd_signal = calculate_macd(eth_historical)                    # requires upgraded CoinMarketCap Plan
        # print("Latest MACD values:\n", macd.tail(), "\n", macd_signal.tail()) # requires upgraded CoinMarketCap Plan

        # Automated Coinbase trade placement for demonstration purposes only
        # trade_response = place_trade('ETH-USD', 'buy', os.getenv('ETH_TRADE_AMOUNT'))
        # logging.info(f"Trade response: {trade_response}")

        # Here you can integrate more analysis, indicators, and trading strategies
        
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Script run time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()
