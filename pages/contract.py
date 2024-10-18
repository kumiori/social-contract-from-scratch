import time

import requests
import streamlit as st
from numpy import around
from email_validator import EmailNotValidError, validate_email

if st.secrets["runtime"]["STATUS"] == "Production":
    st.set_page_config(
        page_title="The Social Contract from Scratch • Structure and Participation",
        page_icon="✨",
        # layout="wide",
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

import hashlib
import json
import random
from datetime import datetime

import pandas as pd
import philoui
import plotly.express as px
import streamlit.components.v1 as components
import streamlit_shadcn_ui as ui
import yaml
from philoui.authentication_v2 import AuthenticateWithKey
from philoui.io import QuestionnaireDatabase as IODatabase
from philoui.io import (conn, create_dichotomy, create_equaliser,
                        create_qualitative, create_quantitative)
from philoui.survey import CustomStreamlitSurvey
from philoui.texts import hash_text, stream_once_then_write, stream_text
from streamlit_elements import elements, mui, nivo
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row
from streamlit_gtag import st_gtag
from streamlit_pills_multiselect import pills
from streamlit_player import st_player
from streamlit_timeline import timeline
from yaml import SafeLoader

st_gtag(
    key="gtag_app_contract1",
    id="G-Q55XHE2GJB",
    event_name="contract_page",
    params={
        "event_category": "contract",
        "event_label": "contract",
        "value": 97,
    },
)

config = {
  "credentials": {
    "webapp": "discourse-players",
    "usernames": {
    }
  },
  "cookie": {
    "expiry_days": 30,
    "expiry_minutes": 30,
    "key": "discourse_panel_cookie",
    "name": "discourse_panel_cookie"
  },
  "preauthorized": {
    "emails": ""
  }
}

mask_string = lambda s: f"{s[0:4]}***{s[-4:]}"

authenticator = AuthenticateWithKey(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days'],
    pre_authorized=config['preauthorized'],
)
fields_connect = {'Form name':'Open with your access key', 'Email':'Email', 'Username':'Username',
            'Password':'Password', 'Repeat password':'Repeat password',
            'Register':' Retrieve access key ', 'Captcha':'Captcha'}
fields_forge = {'Form name':'Where is my access key?', 'Email':'Email', 'Username':'Username',
            'Password':'Password', 'Repeat password':'Repeat password',
            'Register':' Here • Now ', 'Captcha':'Captcha'}

db = IODatabase(conn, "discourse-data")

with open("assets/discourse.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.write(f.read())
    
with open('assets/credentials.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    now = datetime.now()

survey = CustomStreamlitSurvey()

# initialise the sumup object in session state
if 'sumup' not in st.session_state:
    st.session_state['sumup'] = None


# Replace with your SumUp API credentials
API_BASE_URL = 'https://api.sumup.com/v0.1'
ACCESS_TOKEN = st.secrets["sumup"]["CLIENT_API_SECRET"]


def generate_random_points(num_points):
    return [{"id": i, "x": random.uniform(0, 100), "y": random.uniform(0, 100)} for i in range(num_points)]

@st.cache_data(ttl=60)
def fetch_plenary_data():
    _data, empty_rows = fetch_data(column="plenary_01")    
    return _data, empty_rows
   
@st.cache_data(ttl=60)
def fetch_updated_data():
    _data, empty_rows = fetch_data(column="updated_at")    
    return _data, empty_rows
   
@st.cache_data(ttl=60)
def fetch_consent_action_data():
    _data, empty_rows = fetch_data(column="session_4_consent_action")    
    return _data, empty_rows
    
@st.cache_data(ttl=60)
def fetch_data(column = "*, signature"):
    conn = db.conn
    table_name = db.table_name
    response = conn.table(table_name).select(column + ', signature').execute()
    if response and response.data:
        data = response.data
        _data = []
        empty_values = 0
        for row in data:
            if row.get(column) and row.get(column) != "null":
                _data.append(row)
            else:
                empty_values += 1
    else:
        st.error(f"No data found in the {table_name} table.")
    
    return _data, empty_values
    
@st.cache_data(ttl=60)
def fetch_values_worldview_data():
    conn = db.conn
    table_name = db.table_name
    response = conn.table(table_name).select("session_1_values", "session_1_worldview").execute()
    # _data, empty_rows = fetch_data(column="plenary_01")    

    if response and response.data:
        data = response.data
        _data = []
        
        # Display each row of data
        for row in data:
            _data.append(row)
    else:
        st.error(f"No data found in the {table_name} table.")
    
    return _data
    
@st.cache_data(ttl=60)
def fetch_values_data():
    _data, empty_rows = fetch_data(column="session_1_values")    
    return _data, empty_rows

@st.cache_data(ttl=60)
def fetch_worldview_data():
    _data, empty_rows = fetch_data(column="session_1_worldview")    
    return _data, empty_rows

@st.cache_data(ttl=60)
def fetch_consent_data():
    conn = db.conn
    table_name = db.table_name
    response = conn.table(table_name).select("consent_00").execute()
    
    if response and response.data:
        data = response.data
        _data = []
        
        # Display each row of data
        for row in data:
            _data.append(row)
    else:
        st.error(f"No data found in the {table_name} table.")
    
    return _data
    
def intro():
    cols = st.columns(4, vertical_alignment="center")
    today = datetime.now()
    target_date = datetime(today.year, 9, 27)

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
        switch_value = ui.switch(default_checked=True, label="Economic mode", key="switch1")
        # if switch_value:
        st.toast(f"Economic mode is {switch_value}")
        # whitelist = ui.link_button(text="Check the results", url="http://localhost:8502/plenary#people-bring-values-into-the-social-contract", key="link_btn")
        # st.markdown('<a href="#results" target="_self">Results</a>',unsafe_allow_html=True)
        # if whitelist:
            # st.toast("Whitelist")
            # join_waitlist()

    st.markdown("# <center>Inter•Active•Plenary</center>", unsafe_allow_html=True)

    st.markdown("## <center>Time to Redraw the Social Contract (from Scratch).</center>", unsafe_allow_html=True)

    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')} - Plenary", unsafe_allow_html=True)

    st.divider()

def data_density(data, empty_rows, progress_bar=False):
    _density = around((len(data) / (len(data) + empty_rows)) * 100, 2)
    st.write(f"Data density: {_density}%") 
    if progress_bar:
        st.progress(_density/100)
        
def parse_structure_participation(data):
    parsed_data = []

    for entry in data:
        # Extract the session_2_structure_participation JSON string
        session_participation = entry.get("session_2_structure_participation")

        if session_participation:
            try:
                # Convert the JSON string to a dictionary
                session_dict = json.loads(session_participation)

                # Extract relevant fields
                exclude_criteria = session_dict.get("exclude_criteria", {}).get("value")
                strategic_choice = session_dict.get("What is a _strategic_ choice?", {}).get("value")
                share_thoughts = session_dict.get("Share your thoughts:", {}).get("value")
                future_outlook = session_dict.get("future_outlook", {}).get("value")
                transition_rate = session_dict.get("transition_rate", {}).get("value")
                preferred_mode = session_dict.get("preferred_mode", [])
                conflict_resolution = session_dict.get("conflict_resolution_elements")
                feedback = session_dict.get("I Wish To Read and Maybe Share Feedback", {}).get("value")
                exclude_criteria_ext = session_dict.get("exclude_criteria_ext", {}).get("value")

                # Append the extracted data to the list
                parsed_data.append({
                    "exclude_criteria": exclude_criteria,
                    "strategic_choice": strategic_choice,
                    "share_thoughts": share_thoughts,
                    "future_outlook": future_outlook,
                    "transition_rate": transition_rate,
                    "preferred_mode": preferred_mode,
                    "conflict_resolution": conflict_resolution,
                    "feedback": feedback,
                    "exclude_criteria_ext": exclude_criteria_ext,
                    "signature": entry.get("signature")
                })

            except json.JSONDecodeError:
                print(f"Error parsing JSON for entry: {entry.get('signature')}")

    return parsed_data

def parse_plenary(dataset):
    """
    Function to extract relevant data from the plenary session dataset.
    Args:
        dataset (dict): The dataset collected from the plenary session.

    Returns:
        dict: Extracted data including name, thoughts on pathways, and an open-ended contribution.
    """
    extracted_data = {}

    # Extract the name
    if 'name' in dataset:
        extracted_data['name'] = dataset['name'].get('value', '')

    # Extract thoughts on pathways
    if 'What are your thoughts on these three pathways?' in dataset:
        extracted_data['thoughts_on_pathways'] = dataset['What are your thoughts on these three pathways?'].get('value', '')

    # Extract open-ended ideas or questions
    if 'This is your chance to share an idea, a thought, or even a question that\'s been on your mind.' in dataset:
        extracted_data['open_idea'] = dataset['This is your chance to share an idea, a thought, or even a question that\'s been on your mind.'].get('value', '')

    # Extract categorical choice
    if 'categorical' in dataset:
        extracted_data['categorical_choice'] = dataset['categorical'].get('value', None)

    return extracted_data

def parse_feedback(data):
    parsed_data = []

    for entry in data:
        session = entry.get("session_4_consent_action")
        parsed_entry = {
            "willingness": session.get("willingness", {}).get("value"),
            "spectrum_relations": session.get("spectrum_relations", {}).get("value"),
            "transparency": session.get("transparency", {}).get("value"),
            "open_decision_making": session.get("open_decision_making", {}).get("value"),
            "clear_communication": session.get("clear_communication", {}).get("value"),
            "collaborative_technologies": session.get("collaborative_technologies", {}).get("value")
        }
        parsed_data.append(parsed_entry)

    # Convert to pandas DataFrame for easier manipulation and visualization
    df = pd.DataFrame(parsed_data)
    return df


def parse_session_data(data):
    parsed_data = []
    
    for entry in data:
        # Check if the entry has values for session_1_values and session_1_worldview
        session_1_values = entry.get("session_1_values")
        session_1_worldview = entry.get("session_1_worldview")
        
        # Parse session_1_values if it exists and isn't null
        if session_1_values:
            try:
                session_1_values = json.loads(session_1_values)
                parsed_data.append({
                    "session_1_values": session_1_values,
                })
            except json.JSONDecodeError:
                session_1_values = None
        
        # Parse session_1_worldview if it exists and isn't null
        if session_1_worldview:
            try:
                session_1_worldview = json.loads(session_1_worldview)
                parsed_data.append({
                    "session_1_worldview": session_1_worldview
                })
            except json.JSONDecodeError:
                session_1_worldview = None
        
    
    return parsed_data


def authentifier():

    tab2, tab1, = st.tabs(["I am returning", "I am new"])
    
    with tab2:
        if st.session_state['authentication_status'] is None:
            authenticator.login('Connect', 'main', fields = fields_connect)
            st.warning('Please use your access key')

        else:
            st.markdown(f"#### My access key is already forged, its signature is `{mask_string(st.session_state['username'])}`.")

    with tab1:
        if st.session_state['authentication_status'] is None:
            """
            We have a key in store, for you to proceed.
            Click `Here • Now` after filling the captcha, to retrieve it. 
            """
            try:
                match = True
                success, access_key, response = authenticator.register_user(data = match, captcha=True, pre_authorization=False, fields = fields_forge)
                if success:
                    st.success('Key successfully forged')
                    st.toast(f'Access key: {access_key}')
                    st.session_state['username'] = access_key
                    st.markdown(f"### Your access key is `{access_key}`. Now connect using the key and keep it safe! it will allow you to access the next steps.")
            except Exception as e:
                st.error(e)
        else:
            st.info('It seems that I am already connected')
                # with col2:
            authenticator.logout()


def check_signature_presence_in_data(data, signature):
    # Use the any() function to check if any row has the matching signature
    return any(entry.get('signature') == signature for entry in data)

def get_row_by_signature(data, signature):
    # Use next() to find the first row where the signature matches
    return next((entry for entry in data if entry.get('signature') == signature), None)

if __name__ == "__main__":
    intro()
    authentifier()
    
    "### Structure and participation"
    data, empty_rows = fetch_data(column="session_2_structure_participation")
    # print length of data and empty rows
    st.write(f"Length of data: {len(data)}")
    st.write(f"Empty rows: {empty_rows}")
    st.write(f"Data density: {around((len(data) / (len(data) + empty_rows)) * 100, 2)}%") 
    presence = check_signature_presence_in_data(data, st.session_state["username"])
    st.write("Signature presence in data: ", presence)
    _my_data = get_row_by_signature(data, st.session_state["username"])
    st.write("My data:", _my_data)
    "---"
    rows = []
    
    # st.json(data)
    # Iterate over the data and collect plenary session values
    parse_structure = parse_structure_participation(data)
    st.table(parse_structure)
    
    "### Plenary"

    data, empty_rows = fetch_plenary_data()
    st.write(f"Length of data: {len(data)}")
    st.write(f"Empty rows: {empty_rows}")
    data_density(data, empty_rows, progress_bar=True)
    presence = check_signature_presence_in_data(data, st.session_state["username"])
    st.write("Signature presence in data: ", presence)

    
    for entry in data:
        plenary_values = entry.get("plenary_01")
        
        if plenary_values:
            # Parse the JSON string into a Python dictionary
            plenary_dict = json.loads(plenary_values)
            
            # Extract relevant fields from the parsed dictionary
            name = plenary_dict.get("name", {}).get("value", "")
            pathways_thoughts = plenary_dict.get("What are your thoughts on these three pathways?", {}).get("value", "")
            idea_or_question = plenary_dict.get("This is your chance to share an idea, a thought, or even a question that's been on your mind.", {}).get("value", "")
            
            # Append the extracted information to the rows list
            rows.append({
                "name": name,
                "thoughts_on_pathways": pathways_thoughts,
                "idea_or_question": idea_or_question
            })

    # Convert the rows into a pandas DataFrame
    df = pd.DataFrame(rows)

    # Display the DataFrame for further processing
    st.table(df)
    
    "### Values and Worldview"
    "#### Values"
    
    # data, empty_rows = fetch_values_worldview_data()
    data, empty_rows = fetch_values_data()
    st.write(f"Length of data: {len(data)}")
    st.write(f"Empty rows: {empty_rows}")

    data_density(data, empty_rows, progress_bar=True)
    
    presence = check_signature_presence_in_data(data, st.session_state["username"])
    st.write("Signature presence in data: ", presence)
    _my_data = get_row_by_signature(data, st.session_state["username"])
    st.write("My data:", _my_data)
    "---"

    parsed_session = parse_session_data(data)

    # Extract all session_1_values data

    all_values_data = []
    for entry in parsed_session:
        if "session_1_values" in entry and entry['session_1_values'] is not None:
            all_values_data.extend(entry["session_1_values"])

    from collections import Counter

    # Flatten the list to get all the values together
    # Count the occurrences of each value
    value_counts = Counter(all_values_data)

    # Find the unique and overlapping values
    custom_values = [value for value, count in value_counts.items() if value.startswith("🎁 ")]
    unique_values = [value for value, count in value_counts.items() if count == 1]
    overlapping_values = [(value, count) for value, count in value_counts.items() if count > 1]
    # Prepare the data in the required format

    words = []
    for value, count in value_counts.items():
        word_data = {
            "text": value,  # The actual value
            "value": count,  # The frequency of the value
            "color": "#{:06x}".format(random.randint(0, 0xFFFFFF)),  # Random color for now, can be adjusted
        }
        words.append(word_data)
    # print(words)
    # if st.button("Visualize word cloud"):
    # return_obj = wordcloud.visualize(words, 
    #                                 tooltip_data_fields={'text':'Company', 'value':'Mentions'}, per_word_coloring=False)

    # st.write(return_obj)

    st.write("Unique Values: ")
    st.json(unique_values, expanded=False)
    st.write("Shared Values: ")
    st.json(overlapping_values, expanded=False)

    "#### Worldview"
    # Extract all session_1_worldview data

    from pages.input_data_worldviews import worldviews
    data, empty_rows = fetch_worldview_data()
    
    
    presence = check_signature_presence_in_data(data, st.session_state["username"])
    st.write("Signature presence in data: ", presence)

    parsed_session = parse_session_data(data)

    all_worldview_data = []
    
    for entry in parsed_session:
        if "session_1_worldview" in entry and entry['session_1_worldview'] is not None:
            all_worldview_data.extend(entry["session_1_worldview"])
    
    # all_worldview_data

    # this is duplicated from input_data_worldviews.py
    def assign_hash_to_dictionary(worldviews):
        id_counter = 1
        statement_dict = {}
        
        for worldview, types in worldviews.items():
            for category, statements in types.items():
                for statement in statements:
                    # hash statement to create unique ID
                    statement_hash = hashlib.md5(statement.encode()).hexdigest()
                    statement_dict[id_counter] = {
                        "worldview": worldview,
                        "category": category,
                        "statement": statement,
                        "hash": statement_hash
                    }
                    id_counter += 1
        return statement_dict


    import importlib  
    session1 = importlib.import_module("pages.session-1")
    
    # all_worldview_data
    signed_worldview_data = assign_hash_to_dictionary(worldviews)

    aggregated_data = session1.aggregate_worldview_data(all_worldview_data)
    
    _resonating_statements = {key: value for key, value in aggregated_data.items() if value["average"] > 0.7}

    # Filter for statements that do not resonate < 0.3
    _non_resonating_statements = {key: value for key, value in aggregated_data.items() if value["average"] < 0.3}


    # Display results
    st.subheader("Statements that resonate more widely")

    resonating_statements = [session1.hash_to_statement_dict(signed_worldview_data).get(h) for h in _resonating_statements.keys()]
    for _statement in resonating_statements:
        if _statement and 'statement' in _statement:
            st.markdown(f"#### ✨ {_statement['statement']}")    # st.write(resonating_statements)
    st.subheader("\nStatements that dissonate")
    # st.write(_non_resonating_statements)
    non_resonating_statements = [session1.hash_to_statement_dict(signed_worldview_data).get(h) for h in _non_resonating_statements.keys()]
    for _statement in non_resonating_statements:
        if _statement and 'statement' in _statement:
            st.markdown(f"🔕 {_statement['statement']}")

    "### Updates"
    data, empty_rows = fetch_updated_data()
    # st.json(data)
    df = pd.DataFrame(data)

    # Convert updated_at to timezone-aware datetime
    df['updated_at'] = pd.to_datetime(df['updated_at'], utc=True)

    # Get current time with timezone (UTC)
    current_time = pd.Timestamp.now(tz='UTC')

    # Calculate days since last update
    df['days_since_update'] = (current_time - df['updated_at']).dt.days
    df = df.sort_values('days_since_update', ascending=True)

    # st.table(df)
    # # Create a bar chart for days since update
    fig = px.bar(df, x='signature', y='days_since_update', title="Days Since Last Update", labels={'days_since_update': 'Days'}, color='days_since_update')
    fig.update_layout(
        xaxis_title="Date of Update", 
        yaxis_title="Days Since Last Update",
        xaxis=dict(showticklabels=False),
        showlegend=False,
        height=300,
    )

    st.plotly_chart(fig)

    "### Consent/Action"
    data, empty_rows = fetch_consent_action_data()
    st.write(f"Length of data: {len(data)}")
    st.write(f"Empty rows: {empty_rows}")

    data_density(data, empty_rows, progress_bar=True)
    
    presence = check_signature_presence_in_data(data, st.session_state["username"])
    st.write("Signature presence in data: ", presence)
    _my_data = get_row_by_signature(data, st.session_state["username"])
    st.write("My data:", _my_data)
    "---"
    # st.json(data)
    
    for entry in data:
        session = entry.get("session_4_consent_action")
        st.json(session)
        # st.write(entry.get("session_4_consent_action").get("willingness", {}).get("value"))
    
    # df = parse_feedback(data)
    # st.table(df)    
    "### Consent"

    # extracted_data = parse_plenary(data)
    # df = pd.DataFrame(extracted_data)  
    # st.table(df)