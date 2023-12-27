import grpc
import vectordb_pb2
import vectordb_pb2_grpc
import struct
import numpy as np
from sklearn.linear_model import LinearRegression
import random

def generate_sales_data(num_products, num_days):
    """Generate sales data for products over a period of time."""
    sales_data = {}
    for product_id in range(num_products):
        daily_sales = [random.randint(10, 100) for _ in range(num_days)]  # Simulate daily sales
        sales_data[product_id] = daily_sales
    return sales_data

def main():
    # Setup gRPC channel and create a stub (client)
    channel = grpc.insecure_channel('localhost:50051')
    stub = vectordb_pb2_grpc.VectorDBStub(channel)

    # Generate sales data
    num_products = 10  # Number of products
    num_days = 30      # Number of days in the sales history
    sales_data = generate_sales_data(num_products, num_days)
    _keyspace = "redwing_keyspace"
    _table = "vectors"
    # Write sales data to the database
    for product_id, daily_sales in sales_data.items():
        for day, sales in enumerate(daily_sales):
            data = [product_id, day, sales]
            vector_bytes = struct.pack(f'{len(data)}f', *data)

            # Prepare data for Write
            write_data = vectordb_pb2.VectorWriteRequest(
                keyspace=_keyspace,
                table=_table,
                key=f"product_{product_id}_day_{day}",
                vector=vector_bytes
            )
            stub.Write(write_data)

    # Read and collect sales data for analysis
    collected_data = []
    for product_id in range(num_products):
        product_sales = []
        for day in range(num_days):
            read_data = vectordb_pb2.VectorReadRequest(
                    keyspace=_keyspace,
                    table=_table,
                    key=f"product_{product_id}_day_{day}"
                )
            response = stub.Read(read_data)
            if response.found:
                vector_list = list(response.vector)
                if len(vector_list) == 12:  # Check if the vector has the expected 12 elements
                    sales = vector_list[-1]  # Extract the sales data (assuming it's the last element)
                    product_sales.append(sales)
                else:
                    print(f"Unexpected number of elements in vector for product {product_id}, day {day}")
        if len(product_sales) == num_days:
            collected_data.append((product_id, product_sales))
        else:
            print(f"Insufficient data for product {product_id}")

    # Forecast future demand for each product
    for product_id, product_sales in collected_data:
        X = np.array(range(len(product_sales))).reshape(-1, 1)  # Days
        y = np.array(product_sales)  # Sales
        model = LinearRegression()
        model.fit(X, y)

        # Predict the next day's sales
        next_day_sales = model.predict([[num_days]])
        print(f"Predicted sales for product {product_id} on day {num_days}: {next_day_sales[0]}")

if __name__ == '__main__':
    main()
