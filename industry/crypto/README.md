## Algorithmic Cryptocurrency Trading with BigQuery and Vectors

This script is a comprehensive tool designed to analyze Ethereum transactions using BigQuery, vectorize data, and interact with the Coinbase API for market data and trading actions. It's structured to fetch Ethereum transaction data, analyze it for anomalies, calculate volume metrics, and fetch Ethereum's current market price. 

The major integrations - BigQuery, Coinbase API, CoinMarketCap, and an anomaly detection model - provide a robust framework for analyzing cryptocurrency transactions and responding to market conditions.

This project includes a Python script that integrates with Google BigQuery to retrieve Ethereum transaction data and analyzes it for potential trading opportunities. The script is designed to interact with a vector database, allowing for further analysis and storage of processed data.

### Core Functionality:

-BigQuery Integration: Fetches Ethereum transaction data for detailed analysis.

-Anomaly Detection: Utilizes IsolationForest from Scikit-Learn for identifying unusual transactions.

-Vectorization of Data: Transforms transaction data into a format suitable for machine learning and analysis.

-Coinbase API Integration: Fetches current Ethereum market prices and can be expanded to place trades on the Coinbase platform.

-MACD Calculation: (Commented out due to plan limitations) Can calculate the Moving Average Convergence Divergence, a trend-following momentum indicator.
Potential Expansions

### Future Potential Improvements

-Enhanced Market Analysis: Integrate more sophisticated trading algorithms and indicators.

-Automated Trading: Implement strategies for automated buying/selling based on certain triggers.

-Portfolio Management: Extend the script to manage a diverse cryptocurrency portfolio.

-Real-Time Data Processing: Adapt the script to work with real-time transaction data for more dynamic analysis and trading decisions.

-Integration with Other APIs: Incorporate data from other cryptocurrency exchanges and financial APIs for a broader market view.

### Prerequisites

To run the script, you will need:

-Python 3.6 or later.

-Access to Google Cloud Platform with BigQuery API enabled.

-A service account on Google Cloud with permissions to access BigQuery.

-Environment variables including `BIGQUERY_PRIVATE_KEY` containing the service account key 

-A running instance of our vector database with gRPC endpoint exposed.

-The required Python packages installed.

Installation

Before running the script, install the necessary Python packages using pip. It's recommended to use a virtual environment.

```
pip install grpcio pandas pandas-gbq google-auth dot-env grpc sklearn numpy requests hmac hashlib
```

Make sure to have the grpcio package for gRPC communication, pandas for data manipulation, pandas-gbq for interfacing with Google BigQuery, and google-auth for authentication.

### Setup

Clone the repository to your local machine.

Navigate to the project directory.

Set up the `BIGQUERY_PRIVATE_KEY` .env file with your Google service account credentials and client which can be generated from a `service account` here: https://console.cloud.google.com/apis/credentials

```
BIGQUERY_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nAIzaSyC1s6PgiD10UBgUjYIdplfyYjyE2ZIWFPM\n-----END PRIVATE KEY-----\n" Register One here: console.cloud.google.com/apis/credentials
COINMARKETCAP_API_KEY= Register one here: https://pro.coinmarketcap.com/account
COINBASE_API_KEY= Register one here https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key
COINBASE_API_SECRET=
COINBASE_PASSPHRASE=
COINBASE_PORTFOLIO_ID=
```

Now from the credentials page be sure that you have generated a service account. Afterwards, in the Python file update the following from what you generate in the admin console. Important to note that this key needs to be generated from a service account which can be found in `credentials > service accounts > keys > add key > create new key > JSON`

```
service_account_info = {
    "type": "service_account",
    "project_id": "{your-project-id}",
    "private_key_id": "{private-key-id}",
    "private_key": os.getenv("BIGQUERY_PRIVATE_KEY"),
    "client_email": "{email}@{project-id}.iam.gserviceaccount.com",
    "client_id": "{your-client-id}",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vector%40vector-sandbox.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
```

It is important to note that you must add your service account with these permissions, not your main admin account's email! It will look something like this {email-id}@{project-id}.iam.gserviceaccount.com

In order for this script to execute you must configure your IAM roles accordingly as last step. Go to `IAM` and from there enter your principal as the email associated with your Google Admin Console account and grant permission. Edit the service account's permissions and add the role "BigQuery Job User". If you need to perform more actions like creating or modifying datasets/tables, consider adding "BigQuery Data Editor" or "BigQuery Admin" roles.

Ensure that your vector database is running and accessible through gRPC.

### Usage

Run the script with the following command:

```
python3 algorithmic_trading.py
```

The script will execute the following steps:

```
-Setup gRPC Channel: Initializes a gRPC channel to communicate with the vector database.

-Fetch Data from BigQuery: Retrieves Ethereum transaction data from BigQuery for a specific date.

-Analyze Data: Processes the data to identify trading opportunities. (This step requires implementation based on your strategy.)

-Write Data to Vector DB: Stores the analyzed data in a vector database for further use.

-Trading Algorithm Logic
```

The analyze_data function within the script is intended to be customized with your trading logic. For example, you could implement technical analysis strategies using indicators such as moving averages or RSI.

### Vector Database Interaction

The script is designed to work with any vector database that supports gRPC communication. You will need to implement the write_data_to_vector_db function to convert your data into vectors and write it to the database.

### Logging

The script includes logging to provide status updates and error messages during execution. Ensure the logging level is set appropriately for your environment.

### Security and Authentication

The script uses Google Cloud service account credentials to access BigQuery. Ensure that your credentials are kept secure and your `BIGQUERY_PRIVATE_KEY` environment variable alongside othres is not exposed.

### Contribution

Contributions are welcome. If you have suggestions for improvements or new features, please open an issue or a pull request.

### License

`MIT`

### Contact

For support or issues please reach out to hello [at] redwing.ai

### Disclaimer

This script is for educational and demonstration purposes only. Engage in cryptocurrency trading at your own risk. Ensure compliance with local laws and regulations.
