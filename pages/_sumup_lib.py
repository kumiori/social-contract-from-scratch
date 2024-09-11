
import streamlit as st
import requests

def get_sumup_transaction_history(num_transactions):
    # Define the SumUp transaction history endpoint URL
    transaction_history_url = 'https://api.sumup.com/v0.1/me/transactions/history'

    # Define the query parameters for the API request
    params = {
        'limit': 100,
        'order': 'descending',
        'statuses[]': 'SUCCESSFUL',
        'types[]': 'PAYMENT', 
        # 'changes_since': '2017-10-23T08:23:00.000Z'
    }

    params = {
        'limit': num_transactions,
        'order': 'descending',
        # 'statuses[]': 'SUCCESSFUL',
        'types[]': 'PAYMENT', 
        # 'changes_since': '2017-10-23T08:23:00.000Z'
    }

    # Define the request headers with the access token
    headers = {
        'Authorization': f'Bearer {st.secrets["sumup"]["CLIENT_API_SECRET"]}'
    }

    # Make an HTTP GET request to the SumUp transaction history endpoint
    response = requests.get(transaction_history_url, params=params, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code in [200, 201, 202, 204]:
        # st.write(response.json())
        # Extract the transaction history from the response
        transaction_history = response.json()
        # st.write('Transaction History:')
        return transaction_history
        # for transaction in transaction_history:
            # st.write(transaction)
    else:
        # Display an error message if the request failed
        st.error(f'Error: {response.text}')

def get_transaction_details(tx_id):
    # Define the SumUp transaction details endpoint URL
    api_endpoint = f'https://api.sumup.com/v0.1/me/transactions'

    # Define the request headers with the client API secret from Streamlit secrets
    headers = {
        'Authorization': f'Bearer {st.secrets["sumup"]["CLIENT_API_SECRET"]}'
    }
    params = {
        'id': tx_id
    }
    # Make an HTTP GET request to the SumUp transaction details endpoint
    response = requests.get(api_endpoint, headers=headers, data=params)

    # Check if the request was successful (status code 200)
    if response.status_code in [200, 201, 202, 204]:
        # Extract the transaction details from the response
        transaction_details = response.json()
        # st.write('Transaction Details:')
        # st.json(transaction_details, expanded=False)
        return transaction_details
    else:
        # Display an error message if the request failed
        st.error(f'Error: {response.text}')
        return None

from datetime import datetime

def display_transaction_details(transaction_data):
    # Parsing the transaction data
    transaction_id = transaction_data.get("id", "N/A")
    amount = transaction_data.get("amount", "N/A")
    currency = transaction_data.get("currency", "N/A")
    payment_type = transaction_data.get("payment_type", "N/A")
    status = transaction_data.get("status", "N/A")
    timestamp = transaction_data.get("timestamp", "N/A")
    local_time = transaction_data.get("local_time", "N/A")
    card_type = transaction_data.get("card", {}).get("type", "N/A")
    card_last_4_digits = transaction_data.get("card", {}).get("last_4_digits", "N/A")
    product_summary = transaction_data.get("product_summary", "N/A")
    products = transaction_data.get("products", [])
    receipt_url = next((link["href"] for link in transaction_data.get("links", []) if link["rel"] == "receipt" and link["type"] == "image/png"), "N/A")

    # Convert timestamps to human-readable format
    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
    local_time = datetime.strptime(local_time, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S %Z")

    # Displaying the important information
    st.write(f"Transaction ID: {transaction_id}")
    st.write(f"Amount: {amount} {currency}")
    st.write(f"Status: {status}")
    st.write(f"Payment Type: {payment_type}")
    st.write(f"Timestamp (UTC): {timestamp}")
    st.write(f"Local Time: {local_time}")
    st.write(f"Card Type: {card_type} (Last 4 digits: {card_last_4_digits})")
    st.write(f"Product Summary: {product_summary}")
    st.write(f"Receipt URL (PNG): {receipt_url}")

    st.write("\nProducts:")
    for product in products:
        name = product.get("name", "N/A")
        price = product.get("price", "N/A")
        quantity = product.get("quantity", "N/A")
        total_price = product.get("total_price", "N/A")
        st.write(f" - {name}: {quantity} x {price} = {total_price} {currency}")

