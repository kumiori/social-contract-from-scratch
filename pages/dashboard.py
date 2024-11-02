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

# st.markdown(
#         """
#     <style>
#         [data-testid="collapsedControl"] {
#             display: none
#         }
#         [data-testid="stHeader"] {
#             display: none
#             }
#     </style>
#     """,
#         unsafe_allow_html=True,
#     )

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
    cols = st.columns(4, vertical_alignment="center")

    st.markdown("# <center>The Social Contract from Scratch</center>", unsafe_allow_html=True)

    st.markdown("## <center>A meeting of Social and Natural Sciences, Philosophy, and Arts.</center>", unsafe_allow_html=True)
    # st.markdown('<center>`wait a minute`</center>', unsafe_allow_html=True)
    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}")

    st.divider()
    st.markdown(f"# <center>Dashboard</center> ", unsafe_allow_html=True)
    
    st_lottie("https://lottie.host/91efca67-fa13-43db-8302-f5c182af8152/ufDyVWvWdR.json")

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

def fetch_data_by_signature(verbose=True, signature=None):
    # response = db.fetch_data(kwargs={'verbose': True})
    # return response

    # Fetch only data that matches the provided signature
    if verbose:
        st.write(f"Fetching data for signature: {signature} from the {db.table_name} table.")
        
    response = (
        db.conn.table(db.table_name)
        .select("*")
        .eq("signature", signature)
        .execute()
    )
    
    # Check if any data is returned
    if response and response.data:
        return response.data[0]  # Return the first matching row or handle as needed
    else:
        st.write(f"No data found for signature: {signature} in the {db.table_name} table.")
        return None

def create_discourse_personal(personal_data):
    name = personal_data.get("name", {}).get("value", "No name provided")
    email = personal_data.get("email", {}).get("value", "No email provided")
    signature = personal_data.get("signature", {}).get("value", "No signature provided")
    phone = personal_data.get("phone", {}).get("value", "No phone number provided")
    
    # Athena range dates
    athena_range = personal_data.get("athena-range-dates", [])
    if athena_range:
        start_date = athena_range[0]
        end_date = athena_range[1]
        travel_dates = f"from {start_date['day']}/{start_date['month']}/{start_date['year']} to {end_date['day']}/{end_date['month']}/{end_date['year']}"
    else:
        travel_dates = "No travel dates provided"
    
    # Extra comments
    extra = personal_data.get("extra", {}).get("value", "No additional comments provided")
    
    # Travel expenses
    travel_expenses = personal_data.get("Travel expenses", {}).get("value", "No travel expenses provided")
    
    # Travel preferences
    travel_preferences = personal_data.get("travel_preferences", {}).get("value", [])
    if travel_preferences:
        travel_preferences_str = ", ".join(travel_preferences)
    else:
        travel_preferences_str = "No travel preferences provided"
    
    # Food preferences
    food_preferences = personal_data.get("food_preferences", {}).get("value", [])
    if food_preferences:
        food_preferences_str = ", ".join(food_preferences)
    else:
        food_preferences_str = "No food preferences provided"
    
    # Build the improved discourse
    discourse = (f"Greetings! My name is `{name}`, and I am excited to share that I will be participating in the upcoming event in Athens. "
                 f"You can reach me at `{email}`, and my signature for official purposes is `{signature}`. "
                 f"Though I typically prefer to communicate via email, my phone number is also available for immediate contact if needed: `{phone}`. "
                 f"\n\nI am eagerly anticipating my trip to Athens, where I’ll be staying `{travel_dates}`. "
                 f"This journey holds significant value to me, and I have a few preferences that I believe will ensure a seamless experience. "
                 f"For instance, it would be greatly appreciated if a quiet room could be arranged during my stay. "
                 f"\n\nIn terms of travel, my expenses amount to `{travel_expenses}`. I plan to travel via `{travel_preferences_str}`. "
                 f"Finally, I would like to note that my food preferences are `{food_preferences_str}`.")
    
    return discourse

def create_practical_discourse(practical_questions):
    # Personal information
    
    # Go forward status
    st.write(practical_questions)
    practical_questions = json.loads(practical_questions)

    # go_forward = practical_questions.get("go_forward", {}).get("value", "No decision provided")
    
    # Travel modes and departure location
    travel_modes = practical_questions.get("Travel modes:", {}).get("value", [])
    travel_modes_str = ", ".join(travel_modes) if travel_modes else "No travel modes provided"
    
    departure_location = practical_questions.get("departure_location", {}).get("value", "No departure location provided")
    departure_coordinates = practical_questions.get("departure_location_coordinates", {}).get("value", "No coordinates provided")
    
    # Accommodation feedback
    accommodation_feedback = practical_questions.get("accommodation_feedback", {}).get("value", "No feedback provided")
    
    # Financial support
    financial_support = practical_questions.get("Financial support", {}).get("value", "No financial support requested")
    financial_details = practical_questions.get("Financial details", {}).get("value", [])
    financial_details_str = ", ".join(financial_details) if financial_details else "No specific details provided"
    
    # Building the compelling discourse
    discourse = (f"I am thrilled to take the next step in addressing critical issues surrounding the social contract. "
                 f"As part of this initiative, I will be departing from `{departure_location}` (coordinates: `{departure_coordinates}`) "
                 f"and have arranged travel via `{travel_modes_str}` to ensure seamless participation."
                 f"\n\nMy accommodation feedback, rated `{accommodation_feedback}` out of 5, reflects my commitment to optimizing the experience "
                 f"and creating a comfortable environment for all. In line with this, I am requesting financial support for key areas such as `{financial_details_str}`, "
                 f"which will enable me to fully focus on contributing to this essential dialogue."
                 f"\n\nMoreover, I believe there is immense value in connecting with a plenary speaker, and I am eager to explore synergies "
                 f"that could elevate the conversation to new heights.")

    return discourse

def create_discourse_with_scratches_and_questions(exercise_data):
    # Scratches (reflections)
    exercise_data = json.loads(exercise_data)
    try:
        # Extract user ID dynamically and parse the JSON string
        user_id = next(iter(exercise_data))
        inner_data = json.loads(exercise_data[user_id])
    except (json.JSONDecodeError, TypeError, StopIteration) as e:
        return f"Error decoding JSON or invalid input: {e}"
    
    # Scratches (reflections)
    scratches = inner_data.get("scratches", {})
    scratches_list = ", ".join(scratches.values()) if scratches else "No scratches provided"
    
    # Questions
    questions = inner_data.get("questions", {})
    questions_list = ", ".join(questions.values()) if questions else "No questions provided"
    
    # Problems and Solutions
    problems = inner_data.get("problems", {}).get("value", "No problems provided")
    solutions = inner_data.get("solutions", {}).get("value", "No solutions provided")
    
    # Plans
    plan_b = inner_data.get("plan_b", {}).get("value", "No Plan B provided")
    plan_omega = inner_data.get("plan_omega", {}).get("value", "No worst case scenario provided")
    plan_a = inner_data.get("plan_a", {}).get("value", "No main plan provided")
    
    # Equalisers (potential outcomes)
    equaliser_0 = inner_data.get("equaliser_0", {}).get("value", "No value provided")
    equaliser_1 = inner_data.get("equaliser_1", {}).get("value", "No value provided")
    equaliser_2 = inner_data.get("equaliser_2", {}).get("value", "No value provided")
    equaliser_3 = inner_data.get("equaliser_3", {}).get("value", "No value provided")
    equaliser_4 = inner_data.get("equaliser_4", {}).get("value", "No value provided")
    equaliser_5 = inner_data.get("equaliser_5", {}).get("value", "No value provided")
    
    # Building the more compelling and structured discourse
    discourse = (f"I am deeply committed to reimagining the social contract from the ground up. "
                 f"My reflections—what I refer to as **scratches**—focus on key areas such as `{scratches_list}`. "
                 f"These reflections serve as the foundation for exploring how we, as a collective, can build a more resilient and adaptive societal framework."
                 f"\n\nTo foster meaningful interaction, I’ve posed several critical questions for reflection: `{questions_list}`. "
                 f"These questions invite us to challenge the status quo and actively participate in shaping a future that embraces complexity and diversity."
                 f"\n\nLooking ahead, some challenges that I foresee include: `{problems}`. "
                 f"However, I firmly believe that solutions lie in `{solutions}`. "
                 f"\n\nIn case of unforeseen setbacks, I have considered a Plan B: `{plan_b}`. "
                 f"And for the worst-case scenario, Plan Ω would involve: `{plan_omega}`. "
                 f"\n\nOur main strategy, Plan A, is: `{plan_a}`. "
                 f"\n\nIn thinking about potential outcomes and our vision for the future, it’s crucial to consider several key areas: "
                 f"first, `{equaliser_0}` for New Future Events, `{equaliser_1}` for New Grassroots & Participatory Policies, "
                 f"`{equaliser_2}` for Pilot Projects, `{equaliser_3}` for Remote Collaborative Working Groups, "
                 f"`{equaliser_4}` for the Observatory of Perceptions, and `{equaliser_5}` for Executive Actions.")
    
    return discourse

def create_discourse_consent(consent_data):
    # print(consent_data)
    consent_data = json.loads(consent_data)
    try:
        # Extract user ID dynamically and parse the JSON string
        user_id = next(iter(consent_data))
        inner_data = json.loads(consent_data[user_id])
    except (json.JSONDecodeError, TypeError, StopIteration) as e:
        return f"Error decoding JSON or invalid input: {e}"

    name = consent_data.get("name", {}).get("value", "Anonymous")
    willingness_value = float(consent_data.get("willingness", {}).get("value", 0))

    # Create discourse based on willingness
    discourse = (f"My willingness is `{willingness_value}` to relinquish some degree of personal freedom and participation in decision-making. "
                 f"On the other hand, my willingness is `{1 - willingness_value}` to actively engage, develop, and contribute to living in a harmonious, integrated society."
                 f"\n\nSigned, `{name}`")

    return discourse


def transaction_stuff():
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
    # print(df)

def find_empty_fields(data):
    empty_fields = []

    # Check each key-value pair at the top level
    for key, value in data.items():
        # print(key, value)
        # Check if the top-level value is empty or None
        if value in [None, "null", "", []]:
            empty_fields.append((key, "Top-level session"))
        elif isinstance(value, dict):
            # Check nested dictionary values
            for sub_key, sub_value in value.items():
                # Ensure sub_value is a dictionary with "value" and "label" keys
                if isinstance(sub_value, dict) and sub_value.get("value") in [None, "null", "", []]:
                    empty_fields.append((sub_key, sub_value.get("label", "No label")))
        elif isinstance(value, list):
            # Check each item in the list if it is a dictionary with fields to validate
            for item in value:
                if isinstance(item, dict):
                    for list_key, list_value in item.items():
                        if list_value in [None, "null", "", []]:
                            empty_fields.append((list_key, "No label in list item"))
    return empty_fields

if __name__ == "__main__":
    
    intro()
    
    if st.session_state['authentication_status']:
        st.toast('Initialised authentication model')
        st.write(f'`Your signature is {st.session_state["username"][0:4]}***{st.session_state["username"][-4:]}`')
        
        user_data = fetch_data_by_signature(signature = st.session_state["username"])
        st.write(user_data)
        all_columns = list(user_data.keys())
        print(all_columns)
        exclude_columns = ['id', 'updated_at', 'signature', 'created_at']

        progress_columns = [col for col in all_columns if col not in exclude_columns]

        empty_fields = find_empty_fields(user_data)
        st.write(empty_fields)
        st.markdown(f"## Progress: {(len(progress_columns) - len(empty_fields))/len(progress_columns):.0%}")
        st.progress((len(progress_columns) - len(empty_fields))/len(progress_columns))
        # display missing fields
        if empty_fields:
            st.write("### Missing fields:")
            for field, label in empty_fields:
                st.write(f"- {field} ({label})")
        
        """### Personal data"""
        authenticator.logout()
        
        if user_data is not None:
            st.write(f"--- ID: {user_data['id']} ---")
            st.write(f"Updated at: {user_data['updated_at']}")

            # Personal Details Section
            st.write(user_data['personal_data'])
            personal_data = json.loads(user_data['personal_data'])
            st.write("# Personal Details:")
            if personal_data is not None:
                st.markdown(create_discourse_personal(personal_data))
            else:
                st.write("No personal available. [Link to Personal Questionnaire]")
            
            # Practical Questions Section
            st.write("# Practical Questions:")
            practical_questions = user_data['practical_questions_01']
            if practical_questions is not None:
                st.markdown(create_practical_discourse(practical_questions))
            else:
                st.write("No practical questions available. [Link to Practical Questionnaire]")

            # Philanthropy Section
            st.write("# Philanthropy:")
            philanthropy = user_data['philanthropy_01']
            if philanthropy is not None:
                st.json(philanthropy)
            else:
                st.write("No philanthropy data available. [Link to Philanthropy Questionnaire]")

            # Exercise Section
            st.write("# Exercise:")
            st.write(user_data['exercise_01'])
            exercise = user_data['exercise_01']
            if exercise is not None:
                st.markdown(create_discourse_with_scratches_and_questions(exercise))
            else:
                st.write("No exercise data available. [Link to Exercise Questionnaire]")

            # Consent Section
            st.write("# Consent:")
            consent = user_data['consent_00']
            if consent is not None:
                st.markdown(create_discourse_consent(consent))
            else:
                st.write("No consent data available. [Link to Consent Form]")
                            
            
        else:
            st.write(f"No data found with signature: {st.session_state['username']}")
            
        st.divider()
        """
        # Aggregated data
        """
        # data = pd.DataFrame(user_data)
        
        # st.write(data.columns)
        
        # st.write(data["updated_at"].to_json())
        
    elif st.session_state['authentication_status'] is False:
        st.error('Access key does not open')
    elif st.session_state['authentication_status'] is None:
        authenticator.login('Connect', 'main', fields = fields_connect)
        st.warning('Please use your access key')
