import sys
import streamlit as st
sys.path.append('../sample')  # Adjust the path as necessary

from network_enhanced_threat_detection import main

def display_features(features, title):
    st.subheader(title)
    col1, col2 = st.columns(2)
    with col1:
        st.write("Feature")
        st.write("request_size")
        st.write("response_time")
        st.write("error_code")
        st.write("ip_address")
        st.write("url_endpoint")
        st.write("http_method")
        st.write("user_agent")
        st.write("failed_logins")
    with col2:
        st.write("Value")
        for value in features:
            st.write(value)

def streamlit_app():
    st.title("Network Log Anomaly Detection")

    num_entries = st.sidebar.number_input("Number of log entries", min_value=100, max_value=10000, value=1000)
    
    if st.button("Analyze Log Data"):
        with st.spinner("Analyzing..."):
            threat_details, normal_mean, anomalous_mean = main(num_entries)

            st.header("Anomaly Detection Results")
            for detail in threat_details:
                st.subheader(f"Threat Log Entry: {detail['log_id']}")
                display_features(detail['features'], "Features of this log:")
                display_features(normal_mean, "Average features of normal logs:")
                display_features(anomalous_mean, "Average features of threat logs:")
                st.write("---")

if __name__ == "__main__":
    streamlit_app()