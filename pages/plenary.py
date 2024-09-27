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
    key="gtag_app_session1",
    id="G-Q55XHE2GJB",
    event_name="session1_page",
    params={
        "event_category": "session",
        "event_label": "session1",
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

if 'read_texts' not in st.session_state:
    st.session_state.read_texts = set()
else:
    st.session_state.read_texts = set(st.session_state.read_texts)


if 'results' not in st.session_state:
    st.session_state.results = []  # Store the UI interaction results


if 'survey' not in st.session_state:
    st.session_state['survey'] = {'data': {}}

if 'serialised_data' not in st.session_state:
    st.session_state.serialised_data = {}

# initialise the sumup object in session state
if 'sumup' not in st.session_state:
    st.session_state['sumup'] = None
    
if 'current_element' not in st.session_state:
    st.session_state['current_element'] = None
    
if 'custom_values' not in st.session_state:
    st.session_state['custom_values'] = []
    
if 'tx_tag' not in st.session_state:
    st.session_state.tx_tag = None
      
if 'choices' not in st.session_state:
    st.session_state.choices = []
       
if 'price' not in st.session_state:
    st.session_state.price = .01
       
if 'reshuffled' not in st.session_state:
    st.session_state.reshuffled = False


# Replace with your SumUp API credentials
API_BASE_URL = 'https://api.sumup.com/v0.1'
ACCESS_TOKEN = st.secrets["sumup"]["CLIENT_API_SECRET"]

mask_string = lambda s: f"{s[0:4]}***{s[-4:]}"

def generate_random_points(num_points):
    return [{"id": i, "x": random.uniform(0, 100), "y": random.uniform(0, 100)} for i in range(num_points)]

def my_create_dichotomy(key, id = None, kwargs = {}):
    dico_style = """<style>
    div[data-testid='stVerticalBlock']:has(div#dicho_inner):not(:has(div#dicho_outer)) {background-color: #F5F5DC};
    </style>
    """
    script = """<div id = 'dicho_outer'></div>"""
    st.markdown(script, unsafe_allow_html=True)
    st.markdown(dico_style, unsafe_allow_html=True) 
     
    with st.container(border=True):
        script = """<div id = 'dicho_inner'></div>"""
        st.markdown(script, unsafe_allow_html=True)
        # st.title('asd')
        survey = kwargs.get('survey')
        label = kwargs.get('label', 'Confidence')
        name = kwargs.get('name', 'there')
        question = kwargs.get('question', 'Dychotomies, including time...')
        messages = kwargs.get('messages', ["🖤", "Meh. Balloons?", "... in between ..."])
        inverse_choice = kwargs.get('inverse_choice', lambda x: x)
        _response = kwargs.get('response', '## You can always change your mind.')
        col1, col2, col3 = st.columns([3, .1, 1])
        response = survey.dichotomy(name=name, 
                                label=label,
                                question=question,
                                gradientWidth = kwargs.get('gradientWidth', 30), 
                                key=key)
        if response:
            st.markdown('\n')            
            if float(response) < 0.1:
                st.success(messages[0])
            if float(response) > 0.9:
                st.info(messages[1])
            elif 0.1 < float(response) < 0.9:
                st.success(messages[2])
        else:
            st.markdown(f'#### Take your time:', unsafe_allow_html=True)
            st.markdown(_response)
    return response

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

@st.cache_data    
def fetch_data():
    
    conn = db.conn
    table_name = db.table_name
    response = conn.table(table_name).select("session_1_values", "session_1_worldview").execute()
    
    if response and response.data:
        data = response.data
        _data = []
        
        # Display each row of data
        for row in data:
            _data.append(row)
    else:
        st.error(f"No data found in the {table_name} table.")
    
    return _data
    
    return response

@st.cache_data
def _reshuffle(values):
    import random
    random.shuffle(values)

@st.dialog('Cast your preferences dashboard')
def _form_submit():
    with st.spinner("Checking your signature..."):
        signature = st.session_state["username"]
        serialised_data = st.session_state['serialised_data']

        if not serialised_data:
            st.error("No data available. Please ensure data is correctly entered before proceeding.")
        else:
            preferences_exists = db.check_existence(signature)
            st.write(f"Integrating preferences `{mask_string(signature)}`")
            _response = "Yes!" if preferences_exists else "Not yet"
            st.info(f"Some of your preferences exist...{_response}")

            try:
                data = {
                    'signature': signature,
                    'plenary_01': json.dumps(serialised_data),
                }
                # throw an error if signature is null
                if not signature:
                    raise ValueError("Signature cannot be null or empty.")
                
                query = conn.table('discourse-data')                \
                       .upsert(data, on_conflict=['signature'])     \
                       .execute()
                
                if query:
                    st.success("🎊 Preferences integrated successfully!")
                    st.balloons()

            except ValueError as ve:
                st.error(f"Data error: {ve}")                
            except Exception as e:
                st.error("🫥 Sorry! Failed to update data.")
                st.write(e)



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

def question(): 
    name = 'there'
    dicho = my_create_dichotomy(key = "executive", id= "executive",
                        kwargs={'survey': survey,
                            'label': 'future_outlook', 
                            'question': 'Do we exclude? (White: Yes, Black: No, Nuances: We exclude for other reasons)',
                            'gradientWidth': 20,
                            'height': 250,
                            'title': '',
                            'name': f'{name}',
                            'messages': ["*Zero,* black!", 
                                         "*One*. White", 
                                         "*between* gray"],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )
            
    my_create_dichotomy(key = "outlook", id= "outlook",
                        kwargs={'survey': survey,
                            'label': 'future_outlook', 
                            'question': 'Click to express your viewpoint.',
                            'gradientWidth': 30,
                            'height': 250,
                            'title': '',
                            'name': 'intuition',
                            'messages': ["*The future looks* dark like an impending storm", "*The future looks* bright and positive", "*The future looks* gray like an uncertain mix"],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )

# Function to interpret the result and generate a human-readable review
def generate_review(results):
    for idx, result in enumerate(results):
        element = result["element"]
        
        # Extract statement details
        st.write(result)

        # statement = element[1]["statement"]
        # worldview = element[1]["worldview"]
        # category = element[1]["category"]
        
        # # Interpret result
        # if result["result"] == "1":
        #     choice = f"I fully resonated with the 1st statement from the {worldview} worldview."
        # elif result["result"] == "0":
        #     # choice = f"I fully resonated with the statement: '{statement_1}' from the {worldview_1} worldview."
        #     choice = f"I fully resonated with the 2nd statement from the {worldview} worldview."
        # else:
        #     choice = f"Your resonance was divided, showing agreement or disagreement with both statements."

        # Format the review
        # st.write(f"### Review of Interaction {idx + 1}:")
        # st.write(f"**Statement 1** ({worldview_1} - {category_1}): {statement_1}")
        # st.write(f"**Statement 2** ({worldview_2} - {category_2}): {statement_2}")
        # st.write(f"**Result**: {choice}")
    st.write("---")    

def dataset_to_outro(data):
    # name = data['name']
    name = 'You'
    ext = 'will'
    formatted_text = f"""
    ## {name} {ext} submit
    """
    return formatted_text, name, ext

def outro():
    st.markdown("## <center> _Chapter One_</center>", unsafe_allow_html=True)

    formatted_text, name, ext = dataset_to_outro(survey.data)
    st.markdown(formatted_text)
    
    _submit = st.button(f'I {ext} submit, _{name}_')
    
    
    if _submit:
        stream_once_then_write(
            """
            Congrats! 
            
            Thank you for your interest. Save this page in your bookmarks, and check again in a few days.
        
            """
"""
_In the meantime_:""")
    with st.spinner("Thinking?"):
        time.sleep(3)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        text = """
        Your insight could provide the next key piece in this collaborative puzzle. 

        Reach out by email, _submit_ your thoughts — each is a step that brings ideas closer to reality.

        <social.from.scratch@proton.me>

            """
        # stream_once_then_write(text)
        # st.markdown(text)
        if st.session_state['authentication_status']:
            st.toast(f'Authenticated successfully {mask_string(st.session_state["username"])}')
            col1, col2, col3 = st.columns([1, 1, 1])
            # with col2:
                # authenticator.logout()
        st.markdown("""
        `Your dashboard is saved.`
        """)

if __name__ == "__main__":
    
    intro()

    authentifier()

    """
    # What is change _made_ (of)?

Our mission is simple and profound: _to collaboratively shape a new social contract that reflects the complexity and diversity of the world we live in._

The Social Contract, at its core, is about how we relate to each other, our environment, and the systems that govern us. But this cannot be built through one perspective alone. It requires opening ourselves to the full spectrum of points of view, ideas, and perceptions—from the bold and radical to the subtle and _infinitely nuanced_. 

This is the approach of the _Athena_ collective.
"""

    # Data for Voronoi chart
    data = generate_random_points(17)

    with elements("voronoi"):
        with mui.Box(sx={"height": 600}):
            nivo.Voronoi(
                data=data,
                xDomain=[0, 100],
                yDomain=[0, 100],
                enableLinks=True,
                linkLineWidth={30},
                cellLineWidth={30},
                linkLineColor="#cccccc",
                cellLineColor="#c6432d",
                pointSize=30,
                pointColor="#c6432d",
                margin={"top": 10, "right": 10, "bottom": 10, "left": 10},
            )
    st.markdown(f""" <center>The Athena Collective is a group of 17. 
                This image represents the interplay of individual in a collective frame. The dots symbolise the 17 members of the Athena Collective, each an individual with their own perspective which changes dynamically. Grey lines depict (some of) the connections, a web of relationships and interactions that weave the collective together. The red tessellation illustrates how these relationships naturally define spaces of influence and responsibility, as well as boundaries.
    This image tells many stories: it speaks of networks, collaboration, personal agency, shared spaces, and the fluid, evolving nature of social contracts. Each member of the collective shapes the landscape while being shaped by the web they are part of, highlighting the interconnectedness and balance needed to thrive together. Note that connections are _underneath_ the boundaries.</center> """, unsafe_allow_html=True)

    st.markdown(f"# <center>Shifts, pathways, and hope?</center> ", unsafe_allow_html=True)

    st.markdown("### Q1: A choice of three pathways")
    
    """#### Agency is making concious and significant decisions."""

    """
    In yesterday’s keynote presentation, Vivien Schmidt theorises three pathways that the social discourse could follow in the future:
    
1. **Liberal:** prioritising “market” solutions and technocratic governance, this dominant pathway represents continuity or “business as usual”. 

2. **Populist:** reaction to experience of institutional failures, this pathway proposes simplistic, exclusionary and divisive solutions to the interconnected problems.

3. **Progressive:** based around inclusivity, bottom-up solutions, and systemic transformation, this pathway seeks to realign governance to prioritise human and environmental wellbeing and needs.

    """
    
    engage_categories= {'1': 'Liberal', '2': 'Populist', '10': 'Progressive'}
    pathway = create_qualitative('trifurcation',
                        kwargs={"survey": survey, 
                                'label': 'categorical', 
                                "name": "we are at a crossing point.",
                                "question" : "Which route to take: Liberal, Populist, or Progressive?",
                                "categories": engage_categories
                        })
    
    # my_create_dichotomy(key = "outlook", id= "outlook",
    #                 kwargs={'survey': survey,
    #                     'label': 'future_outlook', 
    #                     'question': 'Click to express your viewpoint.',
    #                     'gradientWidth': 40,
    #                     'height': 250,
    #                     'title': '',
    #                     'name': 'intuition',
    #                     'messages': ["*Progressinve", "*The future looks* bright and positive", "*The future looks* gray like an uncertain mix"],
    #                     # 'inverse_choice': inverse_choice,
    #                     'callback': lambda x: ''
    #                     }
    #                 )
    
    feedback_messages = {
        '1': "I've chosen the **Liberal** pathway. This path emphasizes free markets, individual freedoms, and gradual reform. It's the dominant pathway today, but does it address the crises we face?",
        '2': "I've chosen the **Populist** pathway. Populism seeks to empower 'the people' against elites, but is often criticized for oversimplifying complex problems. Do you think it can handle our interconnected crises?",
        '10': "I've chosen the **Progressive** pathway. This path calls for systemic change, inclusivity, and bottom-up approaches. Is _this_ the hopeful, necessary shift we need for a sustainable future?"
    }
    
    if pathway is not None:
        st.write(feedback_messages.get(str(pathway), "Thank you for your dedication so far!"))

    survey.text_area("What are your thoughts on these three pathways?", height=100)

    if st.button("Integrate the Bigger Picture", key="integrate", help="Integrate your data", 
              disabled=not bool(st.session_state['authentication_status']), 
              type='primary',
              use_container_width=True,
              on_click=lambda: _form_submit()):
        """
        Congratulations!

Save this page in your bookmarks and check again in a few days. Otherwise, reach out to us by email. 

social.from.scratch@proton.me

How you feel about the results?"""
        
    if st.session_state['authentication_status']:
        st.markdown(f"#### Signed #`{mask_string(st.session_state['username'])}`.")


    st.divider()
    st.divider()
    st.divider()
    st.divider()
    st.divider()


#     st.markdown("### Q2: Soc transitions: fast or slow?")

#     """
#     #### Global crises highlight the need for significant social transitions.

#     When you think about the social changes we need, do you personally prefer and are happy to support **a fast, decisive _disruptive_ (nonlinear) transition**  (Black), 
#     or a slow, gradual transition that allows for adjustment, compromise, and adaptation (White)? The two choices are _not mutually exclusive_, choose a Shade of 
#     Gray if you believe in a mix of both approaches. 

#     _Remark: This is about how you would like to see change happen, rather than what you think is most likely._

#     """

#     my_create_dichotomy(key = "transitions", id= "executive",
#                         kwargs={'survey': survey,
#                             'label': 'transition_rate', 
#                             'question': 'Click to express your viewpoint.',
#                             'gradientWidth': 20,
#                             'height': 250,
#                             'title': '',
#                             'name': 'intuition',
#                             'messages': ["*Fast transition* rapid and transformative", "*Slow* gradual and long", "*A mix of the two* with the implications of both"],
#                             # 'inverse_choice': inverse_choice,
#                             'callback': lambda x: ''
#                             }
#                         )

#     st.divider()
    
#     """
    
#     """    
#     # my_create_dichotomy(key = "wodak", id= "executive",
#     #                     kwargs={'survey': survey,
#     #                         'label': 'transition_rate', 
#     #                         'question': 'Click to express your viewpoint.',
#     #                         'gradientWidth': 20,
#     #                         'height': 250,
#     #                         'title': '',
#     #                         'name': 'intuition',
#     #                         'messages': ["*Fast transition* rapid and transformative", "*Slow* gradual and long", "*A mix of the two* with the implications of both"],
#     #                         # 'inverse_choice': inverse_choice,
#     #                         'callback': lambda x: ''
#     #                         }
#     #                     )

    
    
#     st.markdown("### Q3: how do you see?")
    
    
#     """
#     During a recent meeting at UNESCO headquarters in Paris, in a conversation addressing migration, social inequalities, and systemic crises, the Chair issued a compelling challenge: “It is time to challenge financial institutions.”
    
#     We are living in a moment of profound uncertainty, where the financial systems that once seemed solid are now being called into question. The world is facing stark inequalities, environmental degradation, and global migration crises. The call to action is clear.
    
#     Should we trust financial institutions as they stand, or is it time to reshape them to serve a broader global good?”

# """
#     # name = 'intuition'
#     # dicho = my_create_dichotomy(key = "executive", id= "executive",
#     #                     kwargs={'survey': survey,
#     #                         'label': 'future_outlook', 
#     #                         'question': 'Are you ready to donate? (White: Yes, Black: No, Nuances: I need time)',
#     #                         'gradientWidth': 20,
#     #                         'height': 250,
#     #                         'title': '',
#     #                         'name': f'{name}',
#     #                         'messages': ["*Zero,* black!", 
#     #                                      "*One*. White", 
#     #                                      "*between* gray"],
#     #                         # 'inverse_choice': inverse_choice,
#     #                         'callback': lambda x: ''
#     #                         }
#     #                     )

#     challenge = create_quantitative("quantitative_key", 
#                                    kwargs={"survey": survey, 
#                                            "label": "fin_challenge", 
#                                            'name': f'Hello, there',
#                                            "question": 'Should we challenge or should we not?',
#                                            "key": "challenge", 
#                                            "data_values": [2, 1]})
#     st.write(challenge)
    
    
#     feedback_messages = {'1': "### I've chosen to support **challenging** financial institutions, questioning of the current systems and power relations, to better serve the general good.",
#                          '2': "### I've chosen **not to challenge** financial institutions. The status quo is _just fine_ and trusts in the current financial systems is deserved."}
#     if challenge is not None:
#         st.info(feedback_messages.get(str(challenge), "Thank you for your dedication so far!"))
    
                
    """
    
    ### Ready to make your voice count?
    
    """
    
    name = survey.text_input("Let's start with your name — we may have already shared ideas.", id="name")
    
    email = st.text_input("Your email address")
    if email:
        try:
            valid = validate_email(email)
            email = valid.email
            survey.data['email'] = email
        except EmailNotValidError as e:
            st.error(str(e))
    st.write("Please check back here in a few days. We may have crafted your dashboard by then.") 


    """
    #### Extra Step for Our Most Engaged Participants:
    
Share Your Vision:
If you could shape the future and understanding, what's one key change you'd like to see in the world?
Is there a question you wish to share? 
It could be about justice, cooperation, technology, or community—anything that speaks to your vision of a better society.

We shall take this into account in shaping workgroups, discussions, and future events.
"""
    philosophical_reflection = survey.text_area("This is your chance to share an idea, a thought, or even a question that's been on your mind.")
    
    results = st.session_state['results']

    data = fetch_data()
    parsed_session = parse_session_data(data)
    
    # Extract all session_1_values data
    all_values_data = []

    for entry in parsed_session:
        if "session_1_values" in entry and entry['session_1_values'] is not None:
            all_values_data.extend(entry["session_1_values"])

    # Extract all session_1_worldview data
    all_worldview_data = []
    for entry in parsed_session:
        if "session_1_worldview" in entry and entry['session_1_worldview'] is not None:
            all_worldview_data.extend(entry["session_1_worldview"])
    
    # all_worldview_data
    from collections import Counter

    # Flatten the list to get all the values together
    # Count the occurrences of each value
    value_counts = Counter(all_values_data)

    # Find the unique and overlapping values
    custom_values = [value for value, count in value_counts.items() if value.startswith("🎁 ")]
    unique_values = [value for value, count in value_counts.items() if count == 1]
    overlapping_values = [(value, count) for value, count in value_counts.items() if count > 1]
    # Prepare the data in the required format

    """
    
    Click the button below to add your inputs to the bunch.
    
    """
    
    st.write(f"Thank you `{name}` for your interest. We will keep in touch!")
    
    st.session_state['serialised_data'] = survey.data
    # st.write(survey.data)
    
    # _form_submit = lambda: outro()
    
    if st.button("Integrate the Bigger Picture", key="integrate-final", help="Integrate your data", 
              disabled=not bool(st.session_state['authentication_status']), 
              type='primary',
              use_container_width=True,
              on_click=lambda: _form_submit()):
        """
        Congratulations!

Save this page in your bookmarks and check again in a few days. Otherwise, reach out to us by email. 

social.from.scratch@proton.me

How you feel about the results?"""
        
    if st.session_state['authentication_status']:
        st.markdown(f"#### Sign #`{mask_string(st.session_state['username'])}`.")

    """
    
    # Results
    """

    """
    # HERE GO THE VISUALISATION // WHAT DOES THIS MEAN, FOR US TO SHARE
    
    """

    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
