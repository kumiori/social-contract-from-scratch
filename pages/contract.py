import time

import requests
import streamlit as st
from numpy import around
from email_validator import EmailNotValidError, validate_email
from collections import Counter

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
def fetch_plenary_data(verbose=True):
    if verbose:
        st.info(f"Fetching plenary data, column plenary_01")
    _data, empty_rows = fetch_data(column="plenary_01")    
    return _data, empty_rows
   
@st.cache_data(ttl=60)
def fetch_updated_data(verbose=True):
    if verbose:
        st.info(f"Fetching plenary data, column updated_at")
    _data, empty_rows = fetch_data(column="updated_at")    
    return _data, empty_rows
   
@st.cache_data(ttl=60)
def fetch_consent_action_data(verbose=True):
    if verbose:
        st.info(f"Fetching consent action data, column session_4_consent_action")
    _data, empty_rows = fetch_data(column="session_4_consent_action")    
    return _data, empty_rows
    
@st.cache_data(ttl=60)
def fetch_data(column = "*", verbose=True):
    if verbose:
        st.info(f"Fetching all data from the {db.table_name} table.")
    conn = db.conn
    table_name = db.table_name
    response = conn.table(table_name).select(column + ', signature').execute()
    empty_values = 0
    
    if response and response.data:
        data = response.data
        _data = []
        
        for row in data:
            if column == "*":
                if row and row.get(column) != "null":
                    _data.append(row)
                else:
                    empty_values += 1
            else:
                if row and row.get(column) != "null" and row.get(column) is not None:
                    _data.append(row)
                else:
                    empty_values += 1
    else:
        st.error(f"No data found in the {table_name} table.")

    return _data, empty_values
    
@st.cache_data(ttl=60)
def fetch_values_worldview_data(verbose=True):
    if verbose:
        st.info(f"Fetching plenary data, column session_1_values, session_1_worldview")
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
def fetch_values_data(verbose=True):
    if verbose:
        st.info(f"Fetching plenary data, column session_1_values")
    _data, empty_rows = fetch_data(column="session_1_values")    
    return _data, empty_rows

@st.cache_data(ttl=60)
def fetch_worldview_data(verbose=True):
    if verbose:
        st.info(f"Fetching plenary data, column session_1_worldview")
    _data, empty_rows = fetch_data(column="session_1_worldview")    
    return _data, empty_rows

@st.cache_data(ttl=60)
def fetch_consent_data(verbose=True):
    if verbose:
        st.info(f"Fetching plenary data, column consent_00")
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



def hash_to_statement_dict(dict):
    return {value["hash"]: value for value in dict.values()}


def aggregate_worldview_data(data):
    # Initialize a dictionary to hold hash values and corresponding results
    aggregated_data = {}

    # Iterate through each entry in the worldview data
    for statement in data:
        hash_val = statement['hash']
        
        try:
            result = float(statement['result'])

            if hash_val in aggregated_data:
                aggregated_data[hash_val]['sum'] += result
                aggregated_data[hash_val]['count'] += 1
            else:
                aggregated_data[hash_val] = {'sum': result, 'count': 1}

            # Calculate the average for each hash
            for hash_val, stats in aggregated_data.items():
                stats['average'] = stats['sum'] / stats['count']

        except:
                print(f"Invalid result for hash: {hash_val}")
                continue
    return aggregated_data



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

# Define the function to find inactive users based on empty non-auto columns
def find_inactive_users(df, auto_columns=["id", "updated_at", "signature", "created_at"]):
    # Identify the user-defined columns by excluding the auto columns
    user_columns = [col for col in df.columns if col not in auto_columns]
    
    # Filter rows where all user-defined columns are empty (indicating inactivity)
    inactive_users_df = df[df[user_columns].isnull().all(axis=1)]

    # Prepare a dictionary to store signatures and non-null columns (if any)
    inactive_users_info = {}
    
    for index, row in inactive_users_df.iterrows():
        # Get non-null columns for each inactive user
        non_null_columns = row[user_columns].dropna().index.tolist()
        inactive_users_info[row['signature']] = non_null_columns
    
    # Return the signatures and the dictionary of non-null columns
    return list(inactive_users_info.keys()), inactive_users_info

def calculate_data_density(df, signature_column="signature", auto_columns=["id", "updated_at", "signature", "created_at"]):
    
    # Calculate byte sizes for each entry in the DataFrame
    byte_df = df.map(lambda x: len(str(x).encode('utf-8')) if pd.notnull(x) else 0)
    # print(byte_df)
    # Drop auto columns and select user-defined session columns for normalization
    session_columns = [col for col in df.columns if col != signature_column and col not in auto_columns]
    
    # Calculate max values per column and handle columns with all zeros
    max_values = byte_df[session_columns].max(axis=0)
    max_values = max_values.replace(0, 1)  # Replace zero max values with 1 to avoid NaN during division
    
    # Normalize each column by its maximum byte size
    norm_byte_df = byte_df[session_columns].div(max_values, axis=1)
    
    # Normalize each column (session) by its maximum byte size
    # Prepare the output data structure
    output_data = []
    for index, row in norm_byte_df.iterrows():
        _signature = df.loc[index, signature_column]
        _label = "Myself" if _signature == st.session_state["username"] else _signature[0:3]
        user_data = {
            "id": _label,
            "data": [{"x": session.replace("_", " ").title(), 
                      "y": row[session]} for session in session_columns]
        }
        output_data.append(user_data)
    
    return output_data


def aggregate_structure_participation_data(data):
    # Initialize a list to store parsed session data
    parsed_data = []
    # Parse each user's session and attach the signature
    for idx, session_json in data['session_2_structure_participation'].items():
        session_data = json.loads(session_json)
        signature = data['signature'][idx]
        session_data['signature'] = signature
        parsed_data.append(session_data)
    
    # Convert the parsed data to a DataFrame for easier analysis
    df = pd.json_normalize(parsed_data)
    # Aggregation metrics
    aggregation = {
        # Count unique responses for categorical fields
        "exclude_criteria": Counter(df['exclude_criteria.value'].dropna()),
        "strategic_choice": Counter(df['What is a _strategic_ choice?.value'].dropna()),
        "thoughts": df['Share your thoughts:.value'].dropna().tolist(),  # Collect all comments
        
        # Calculate averages for numeric fields
        "future_outlook": list(df['future_outlook.value'].astype(float).values),
        "transition_rate": list(df['transition_rate.value'].astype(float).values),
        
        # Count preferred modes of participation
        "preferred_mode_counts": Counter([mode for sublist in df['preferred_mode'].dropna() for mode in sublist])
    }
    
    # Convert aggregation to a readable format for easy interpretation
    return aggregation

def generate_structure_participation_narrative(data, participants_count, verbose=False):
    # Unpack the data for clarity
    exclude_criteria = data["exclude_criteria"]
    strategic_choice = data["strategic_choice"]
    thoughts = data["thoughts"]
    future_outlook = data["future_outlook"]
    transition_rate = data["transition_rate"]
    preferred_modes = data["preferred_mode_counts"]
    
    # Narrative components

    # Exclusion Criteria Narrative
    exclusion_responses = exclude_criteria.get("0", 0)
    exclusion_part = (f"In this gathering, `{participants_count} participants` explore foundational questions about inclusion. "
                      f"`{exclusion_responses} of them` think that exclusion criteria shouldn't play a role in this social contract, "
                      f"leaning towards openness without strict boundaries.")

    # Strategic Choice Narrative
    inclusion_count = strategic_choice.get("Inclusion", 0)
    exclusion_count = strategic_choice.get("Exclusion", 0)
    uncertain_count = strategic_choice.get("I don't know", 0)

    if inclusion_count > exclusion_count:
        strategic_part = (f"Most participants favored inclusion as a guiding principle, though some felt uncertain. "
                          f"While `{inclusion_count} spoke clearly for inclusion`, `{uncertain_count} weren't quite sure` "
                          f"where they stood, indicating a need for further conversation.")
    else:
        strategic_part = (f"While inclusion resonated with some, there was an honest reflection on the potential need for boundaries. "
                          f"`{exclusion_count} voiced exclusion` as a strategic choice, suggesting that the group balance openness with discernment.")

    # Thoughts Narrative
    thought_responses = [thought for thought in thoughts if thought]
    if thought_responses:
        thoughts_part = "Some participants shared reflections, expressing the need to `" + ", ".join(thought_responses) + "`."
    else:
        thoughts_part = "Participants were introspective, holding space for each other's thoughts without necessarily voicing their own."

    # Future Outlook Narrative
    dark_count = future_outlook.count(0)
    gray_count = sum(1 for x in future_outlook if 0 < x < 1)
    bright_count = future_outlook.count(1)

    if bright_count > dark_count and bright_count > gray_count:
        future_part = (f"The group's outlook on the future was cautiously optimistic. `{bright_count}` participants saw a positive future, "
                       f"while {gray_count} felt a mix of hope and uncertainty.")
    else:
        future_part = (f"The future brought mixed feelings. `{dark_count} saw a looming darkness`, while others felt hopeful or uncertain. "
                       f"The range of outlooks painted a picture of both caution and resilience.")

    # Transition Rate Narrative
    high_transition = sum(1 for rate in transition_rate if rate >= 0.5)
    low_transition = participants_count - high_transition
    if high_transition > low_transition:
        transition_part = (f"Interestingly, a significant portion of the group seemed ready for quick transitions, "
                           f"with `{high_transition}` seeing change as something to embrace rather than fear.")
    else:
        transition_part = (f"Most participants felt a slower approach to change was more sustainable, with `{low_transition} preferring "
                           f"a gradual transition` rather than abrupt shifts.")

    # Preferred Modes Narrative
    play_count = preferred_modes.get("Play", 0)
    listen_count = preferred_modes.get("Listen", 0)
    preferred_modes_part = (f"When it came to how they engaged, the group leaned into creativity and receptivity. "
                            f"`{play_count} are drawn to play` as a mode of exploration, while `{listen_count} value listening`, "
                            f"creating a balance between active participation and attentiveness.")

    # Combine narrative components
    narrative = (
        f"{exclusion_part} \n\n {strategic_part}  \n\n {thoughts_part}  \n\n {future_part}  \n\n {transition_part}  \n\n {preferred_modes_part}"
    )
    
    return narrative

if __name__ == "__main__":
    intro()
    authentifier()
    
    all_data, empty_rows = fetch_data()

    df = pd.DataFrame(all_data)
    f"""Empty rows {empty_rows}"""
    # st.table(df.head())
    # st.write(df.columns)    
    
    _columns = ["id", "updated_at", "signature", "personal_data", "path_001", "created_at", "practical_questions_01", "philanthropy_01", "exercise_01", "consent_00", "remote_05", "session_1_values", "session_1_worldview", "session_2_structure_participation", "session_3_relations_systems_healing", "session_4_consent_action", "plenary_01"] 
    _auto_columns = ["id", "updated_at", "signature", "created_at"]

    inactive_users, inactive_users_info = find_inactive_users(df, auto_columns=_auto_columns)
    # Call the function to get the desired format
    heatmap_data_density = calculate_data_density(df)
    st.json(heatmap_data_density[0:10])
    with elements("nivo_charts"):

        with mui.Box(sx={"height": 600}):
            nivo.HeatMap(
                data=heatmap_data_density,
                margin={ "top": 100, "right": 90, "bottom": 60, "left": 50 },
                # colors={'scheme': 'brown_blueGreen'},
                colors={
                    'type': 'diverging',
                    'scheme': 'red_yellow_blue',
                    'divergeAt': 0.,
                    'minValue': 0,
                    'maxValue': 1
                },
                valueFormat=">-.0%",
                # cellComponent="circle",
                enableLabels = False,
                axisTop={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": -90,
                    "legend": 'x',
                    "legendOffset": 46,
                    "truncateTickAt": 0
                },
                annotations={
                        "type": 'rect',
                        "match": {
                            "id": 'Myself."Personal_Data"'
                        },
                        "note": 'Bus in Germany',
                        "noteX": 120,
                        "noteY": -130,
                        "offset": 6,
                        "noteTextOffset": 5,
                        "borderRadius": 2
                },
                legends = [
                    {
                        "anchor": 'bottom',
                        "translateX": 0,
                        "translateY": 30,
                        "length": 400,
                        "thickness": 8,
                        "direction": 'row',
                        "tickPosition": 'after',
                        "tickSize": 3,
                        "tickSpacing": 4,
                        "tickOverlap": False,
                        "tickFormat": '>-.0%',
                        "title": 'Energy (data) density →',
                        "titleAlign": 'start',
                        "titleOffset": 4
                    }
                ]
            )

        
        
    f"""{len(inactive_users)} Inactive users"""
    if inactive_users:
        f"""Inactive users: {inactive_users}"""
        f"""Inactive users info: {inactive_users_info}"""
    
    
    
    """---"""
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
    
    df = pd.DataFrame(data)
    
    aggregated = aggregate_structure_participation_data(df)
    
    st.write(aggregated)
    
    _narrative = generate_structure_participation_narrative(aggregated, len(data))
    st.markdown(_narrative)
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
    # session1 = importlib.import_module("pages.session-1")
    
    # all_worldview_data
    signed_worldview_data = assign_hash_to_dictionary(worldviews)

    aggregated_data = aggregate_worldview_data(all_worldview_data)
    
    _resonating_statements = {key: value for key, value in aggregated_data.items() if value["average"] > 0.7}

    # Filter for statements that do not resonate < 0.3
    _non_resonating_statements = {key: value for key, value in aggregated_data.items() if value["average"] < 0.3}


    # Display results
    st.subheader("Statements that resonate more widely")

    resonating_statements = [hash_to_statement_dict(signed_worldview_data).get(h) for h in _resonating_statements.keys()]
    for _statement in resonating_statements:
        if _statement and 'statement' in _statement:
            st.markdown(f"#### ✨ {_statement['statement']}")    # st.write(resonating_statements)
    st.subheader("\nStatements that dissonate")
    # st.write(_non_resonating_statements)
    non_resonating_statements = [hash_to_statement_dict(signed_worldview_data).get(h) for h in _non_resonating_statements.keys()]
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
    fig = px.bar(df, x='signature', y='days_since_update', title="Days Since Last Update",
                 log_y=True,
                 labels={'days_since_update': 'Days'}, color='days_since_update')
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
    
    # for entry in data:
    #     session = entry.get("session_4_consent_action")
    #     st.json(session)
        # st.write(entry.get("session_4_consent_action").get("willingness", {}).get("value"))
    
    
    """
    #### Willingness
    'messages': ["I am unwilling! *Does not sound like a good deal,* let's question these fundamentals", 
                                         "*Plenty of willingness*. And full trust in the authority", 
                                         "*My willingness is* conditional"]
    """
    
    
    
    """
How Can We Implement Effective Transparency?

1.	**Open Decision-Making:** Decisions, especially those affecting large groups, should be made in an open forum or through participatory mechanisms. This allows for the inclusion of diverse voices and ensures that the rationale behind decisions is clear and understood.
    """
    """
2.	**Clear and Accessible Communication:** Transparency isn't just about making information available, it's about making it accessible and understandable to everyone involved. Whether it's through open-source technology, clear reporting systems, or regular updates, people should be able to easily access and interpret the information they need.
"""
    """
3.	**Collaborative Technologies**: Leveraging technology can enhance transparency. Blockchain, for example, provides immutable and transparent ledgers for financial transactions and contracts. Collaborative platforms allow for real-time tracking of project progress and decision-making, ensuring everyone stays informed and engaged.
    """
    """
4.	**Feedback Loops**: Transparency should also be a two-way street. It's not just about providing information but also creating feedback mechanisms where individuals can voice concerns, offer suggestions, or hold decision-makers accountable. These loops ensure that transparency is dynamic and responsive to the community's needs.

## New Forms of Collaboration

Transparency is the cornerstone of our collaborative systems.
    """
    
    # df = parse_feedback(data)
    # st.table(df)    
    "### Consent"

    # extracted_data = parse_plenary(data)
    # df = pd.DataFrame(extracted_data)  
    # st.table(df)