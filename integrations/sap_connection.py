from pyrfc import Connection

# SAP connection parameters
sap_config = {
    'ashost': 'your_sap_host',  # Replace with your SAP host
    'sysnr': '00',              # Replace with your system number
    'client': '000',            # Replace with your client number
    'user': 'your_username',    # Replace with your username
    'passwd': 'your_password'   # Replace with your password
}

# Connect to SAP
try:
    with Connection(**sap_config) as conn:
        result = conn.call('RFC_READ_TABLE', QUERY_TABLE='your_table_name', ROWCOUNT=10)
        for row in result['DATA']:
            print(row)
except Exception as e:
    print(f"Error: {e}")
