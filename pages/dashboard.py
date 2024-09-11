import streamlit as st
import requests
import time
from numpy import around

if st.secrets["runtime"]["STATUS"] == "Production":
    st.set_page_config(
        page_title="The Social Contract from Scratch",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

st.markdown(
        """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        [data-testid="stHeader"] {
            display: none
            }
    </style>
    """,
        unsafe_allow_html=True,
    )

import json
from datetime import datetime
from streamlit_lottie import st_lottie

import pandas as pd
import philoui
import streamlit.components.v1 as components
import streamlit_shadcn_ui as ui
import yaml
from philoui.authentication_v2 import AuthenticateWithKey
from philoui.io import QuestionnaireDatabase as IODatabase
from philoui.io import conn, create_dichotomy, create_equaliser, create_qualitative, create_quantitative
from philoui.survey import CustomStreamlitSurvey
from philoui.texts import hash_text, stream_text
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row
from streamlit_timeline import timeline
from yaml import SafeLoader
from streamlit_player import st_player
from streamlit_gtag import st_gtag
from pages._sumup_lib import get_transaction_details, display_transaction_details



st_gtag(
    key="gtag_app_dashboard",
    id="G-Q55XHE2GJB",
    event_name="dashboard_main_page",
    params={
        "event_category": "apply_philantrhopy",
        "event_label": "test_dashboard",
        "value": 97,
    },
)

db = IODatabase(conn, "discourse-data")

with open("assets/discourse.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.write(f.read())
    
with open('assets/credentials.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    now = datetime.now()

db = IODatabase(conn, "discourse-data")

# ============================== AUTH ===========================

authenticator = AuthenticateWithKey(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
fields_connect = {'Form name':'Connect', 'Email':'Email', 'Username':'Username',
            'Password':'Password', 'Repeat password':'Repeat password',
            'Register':' Here • Now ', 'Captcha':'Captcha'}
fields_forge = {'Form name':'Forge access key', 'Email':'Email', 'Username':'Username',
            'Password':'Password', 'Repeat password':'Repeat password',
            'Register':' Here • Now ', 'Captcha':'Captcha'}

# ==================

@st.cache_data
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
        'types[]': 'PAYMENT', 
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

def intro():
    cols = st.columns(4, vertical_alignment="center")
    today = datetime.now()
    target_date = datetime(today.year, 9, 26)

    # Calculate the time delta
    time_delta = target_date - today
        
    with cols[0]:
        ui.metric_card(title=".", content='0', description="Consents, so far.", key="card1")
    with cols[1]:
        st.button('Dashboard', key='connect', disabled=True, use_container_width=True)

    #     ui.metric_card(title="Total GAME", content="0.1 €", description="Since  _____ we start", key="card2")
    with cols[2]:
        ui.metric_card(title="Days to go", content=f"{time_delta.days}", description="Before start of the conference", key="card3")
    with cols[3]:
        st.markdown("#### Questions")
        ui.badges(badge_list=[("experimental", "secondary")], class_name="flex gap-2", key="viz_badges2")
        # ui.badges(badge_list=[("production", "outline")], class_name="flex gap-2", key="viz_badges3")
        # switch_value = ui.switch(default_checked=True, label="Enable economic", key="switch1")
        whitelist = ui.button(text="Join the XXX", url="", key="link_btn")
        if whitelist:
            st.toast("XXX")

    st.markdown("# <center>The Social Contract from Scratch</center>", unsafe_allow_html=True)

    st.markdown("## <center>A meeting of Social and Natural Sciences, Philosophy, and Arts.</center>", unsafe_allow_html=True)
    # st.markdown('<center>`wait a minute`</center>', unsafe_allow_html=True)
    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}")

    st.divider()
    st.markdown(f"# <center>Dashboard</center> ", unsafe_allow_html=True)
    
    st_lottie("https://lottie.host/91efca67-fa13-43db-8302-f5c182af8152/ufDyVWvWdR.json")
    # st_lottie("https://lottie.host/d8addf11-2974-4c28-80be-df3d9d7273c5/9FuMagA41S.json")
    # st_lottie("https://lottie.host/ec578eca-0d54-4173-b4a4-9bd5eadf577c/bIR9lUB6Sk.json")
    # st_lottie("https://lottie.host/8d0158ec-6eaf-4867-a96c-4774fd2890e2/wFLLXK2Tmj.json")

@st.cache_data
def return_SCFS_details(num_transactions, transaction_rows):
    
    _my_bar = st.progress(0, "Fetching transaction details")
    transactions = []
    filtered_transactions = []
    for i in range(num_transactions):
        _my_bar.progress((i+1)/num_transactions)
        # time.sleep(.1)
        transaction_id = transaction_rows[i]["Transaction ID"]
        # st.write(f"Fetching transaction details for ID: {transaction_id}")
        transaction_details = get_transaction_details(transaction_id)
        transactions.append(transaction_details)


    for transaction in transactions:
        # st.write(transaction.get("product_summary", ""))
        if "Social Contract from Scratch" in transaction.get("product_summary", ""):
            filtered_transactions.append(transaction)

    return filtered_transactions

if __name__ == "__main__":
    
    intro()
    num_transactions = 10
    tx_history = get_sumup_transaction_history(num_transactions)
    transaction_rows = []
    for transaction in tx_history["items"]:
        row = {
            "Timestamp": transaction["timestamp"],
            "Transaction Code": transaction["transaction_code"],
            "Amount": transaction["amount"],
            "Currency": transaction["currency"],
            "Status": transaction["status"],
            "Card Type": transaction["card_type"],
            "Payment Type": transaction["payment_type"],
            "Transaction ID": transaction["transaction_id"],
        }
        transaction_rows.append(row)

    details = return_SCFS_details(num_transactions, transaction_rows)
    transaction_rows = []
    for transaction in details:
        row = {
            "Amount": transaction["amount"],
            "Timestamp": transaction["local_time"],
            "Status": transaction["status"],
            "Transaction Code": transaction["transaction_code"],
            "Product": transaction.get("product_summary", "N/A"),
            "Receipt_url": next((link["href"] for link in transaction.get("links", []) if link["rel"] == "receipt" and link["type"] == "image/png"), "N/A")
        }
        transaction_rows.append(row)

    df = pd.DataFrame(transaction_rows)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df_successful = df[df['Status'] == 'SUCCESSFUL']
    df_failed = df[df['Status'] == 'FAILED']

    # Sum the amounts for all 'SUCCESSFUL' transactions
    total_amount = df_successful['Amount'].sum()
    # st.write(f"Total transactions: {len(df)}")
    # st.write(f"Total FAILED: {len(df_failed)}")
    # st.write(f"Total FAILED: {len(df_successful)}")
    # st.write(f"Total Amount for SUCCESSFUL transactions: {total_amount}")

    # st.write(df_successful)
    
    
    cols = st.columns(4, vertical_alignment="center")
        
    with cols[0]:
        ui.metric_card(title="Total funds", content=f'{total_amount:.2f}', description="€, so far.", key="fund")
    with cols[1]:
        ui.metric_card(title="Donations", content=f'{len(df_successful):d}', description="so far.", key="donations")

    #     ui.metric_card(title="Total GAME", content="0.1 €", description="Since  _____ we start", key="card2")
    with cols[2]:
        ui.metric_card(title="Rate", content=f"{len(df_successful)/len(df):.0%}", description="of success", key="success")
    with cols[3]:
        st.markdown("#### Questions")
        ui.badges(badge_list=[("existential", "secondary")], class_name="flex gap-2", key="exp")
        # ui.badges(badge_list=[("production", "outline")], class_name="flex gap-2", key="viz_badges3")
        # switch_value = ui.switch(default_checked=True, label="Enable economic", key="switch1")
        whitelist = ui.button(text="Join Dinner", url="", key="link_action")
        if whitelist:
            st.toast("XXX")
    
    if st.session_state['authentication_status']:
        st.toast('Initialised authentication model')
        authenticator.logout()
        st.write(f'`Your signature is {st.session_state["username"][0:4]}***{st.session_state["username"][-4:]}`')
    elif st.session_state['authentication_status'] is False:
        st.error('Access key does not open')
    elif st.session_state['authentication_status'] is None:
        authenticator.login('Connect', 'main', fields = fields_connect)
        st.warning('Please use your access key')
