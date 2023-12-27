# Vector Streamlit Dashboard

![Dashboard Image](streamlit.png)

Example usage

To run network anomalies: 

```
pip install streamlit
streamlit run network_anomaly_dashboard.py
```

Implementation for the visualization of Vector generated data using Streamlit.

## Healthcare Research Paper Semantic Search App

To run semantic search:

```
streamlit run healthcare_dashboard.py
```

This document outlines the Streamlit application designed for semantic searching of healthcare research papers. The app interacts with a backend service via gRPC to retrieve similar research papers based on a user's query.

## Streamlit Interface

The app uses Streamlit to create a user-friendly web interface that allows users to input search queries and display results.

## Setup

The app requires the `streamlit` package and the `healthcare_semantic_search` module from the `../run` directory.

```
import sys
import streamlit as st
sys.path.append('../run') # Add the /run directory to the Python path

from healthcare_semantic_search import process_papers, search_similar_papers, setup_grpc_channel
```

## Function: `streamlit_app`

The core function that initializes the Streamlit app, sets up the gRPC channel, and handles the search functionality.

```
def streamlit_app():
# ... Function implementation ...
```

### Streamlit Elements:

- **Title**: Displays the title of the app on the page.
  
```
st.title("Healthcare Research Paper Search")
```


- **Setup gRPC Channel**: Establishes a connection with the backend service for search operations.

```
stub = setup_grpc_channel()
```

- **User Query Input**: A text input field for users to enter their search queries.

```
user_query = st.text_input("Enter your search query related to healthcare research papers:")
```

- **Search Button**: When clicked, it triggers the search function and displays a spinner while searching.

```
if st.button("Search"):
# ... Search functionality ...
```

- **Results Display**: After searching, the top matching papers are displayed in a structured format, showing paper IDs and scores.

```
for paper_id, score in matches:
# ... Display code ...
```

## Running the App

To run the app, navigate to the directory containing the Streamlit app script and execute:

```
streamlit run healthcare_dashboard.py
```

## Note

Ensure that the gRPC backend service is running and accessible at the specified address (`localhost:50051` by default) before starting the Streamlit app.

The Streamlit app is intended to be intuitive and user-friendly, making it suitable for researchers, students, and professionals looking for simulated healthcare-related literature. To make this production-ready be sure to use a real dataset of research papers.






