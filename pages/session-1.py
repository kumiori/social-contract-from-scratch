import streamlit as st
import requests
import time
from numpy import around
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

import json
from datetime import datetime
from streamlit_pills_multiselect import pills
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
import hashlib
import random
from philoui.texts import hash_text, stream_text, stream_once_then_write
from streamlit_elements import elements, mui, nivo

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


def resumes_statements(results):
    # List to store the statements the user resonates with
    resonated_statements = []
    dissonated_statements = []
    _statements = []
    
    # Iterate through each result
    for result in results:
        element = result["element"]
        st.write(element)        
        st.write(result)        
        _statements.append({"element": element[1]['hash'], "resonance": result})
    return _statements

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
                    'session_1_values': json.dumps(serialised_data["values"]),
                    'session_1_worldview': json.dumps(serialised_data["worldview"])
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
        switch_value = ui.switch(default_checked=True, label="Economic mode", key="switch1")
        # if switch_value:
        st.toast(f"Economic mode is {switch_value}")
        whitelist = ui.button(text="Check the results", url="", key="link_btn")
        # if whitelist:
            # st.toast("Whitelist")
            # join_waitlist()

    st.markdown("# <center>Values, Patterns & Nuances</center>", unsafe_allow_html=True)

    st.markdown("## <center>People bring values into the Social Contract.</center>", unsafe_allow_html=True)

    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')} - Session 1", unsafe_allow_html=True)

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
    # Introduction
    
We continue the journey with the _Athena Collective_ — we are an group of thinkers, scholars, artists, practicioners, and changemakers. 
    
Our mission is simple and profound: _to collaboratively shape a new social contract that reflects the complexity and diversity of the world we live in._

The Social Contract, at its core, is about how we relate to each other, our environment, and the systems that govern us. But this cannot be built through one perspective alone. It requires opening ourselves to the full spectrum of points of view, ideas, and perceptions—from the bold and radical to the subtle and _infinitely nuanced_. 
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

    """
    # 
    
Every thought, every lived experience matters in shaping a contract that is truly inclusive and reflective of our shared essence.

As we move through this session, we explore the values that connect us and the dynamics that define our collective future. 
Let's embrace the power of diversity and the richness of each voice in crafting a social contract that speaks to all.
    
    """
    st.markdown(f"# <center>Values and Worldview</center> ", unsafe_allow_html=True)
    # st.markdown("# Values and Worldview")

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")
    
    # authenticate()

    st.markdown("Our worldview shapes the very core of our beliefs, actions, and how we interact with others. "
                "By sharing these values, we build the foundation for any social contract.")
    # authenticate()
    st.markdown("From philosophical, social, and economic perspectives, our worldview creates boundaries and possibilities.")
    st.markdown("### Question")
    st.write("""
### Which values do you embody?
Which values do you see reflected in yourself, and which ones guide your everyday actions?
             
These are core values that guide the construction of a new social contract.""")
    
    st.warning("Sometimes the pills may not display correctly on Chrome browsers. If you encounter this issue, hit the button below that clears the board.")
        # in quali valori ti identifichi e quali valori poni a guida del tuo agire quotidiano
    values = [
        "Equality", "Freedom", "Justice", "Compassion", "Sustainability", "Innovation", "Collaboration", 
        "Responsibility", "Resilience", "Integrity", "Diversity", "Transparency", "Empathy", 
        "Self-determination", "Security", "Community", "Accountability", "Environmental Stewardship", 
        "Growth", "Curiosity", "Wisdom", "Peace", "Respect", "Honesty", "Creativity", "Humility", 
        "Forgiveness", "Gratitude", "Kindness", "Unity", "Trust", "Solidarity", "Patience", "Altruism", 
        "Courage", "Loyalty", "Self-discipline", "Ethical Leadership", "Equality of Opportunity", 
        "Democracy", "Balance", "Mindfulness", "Optimism", "Generosity", "Care", "Joy", "Prudence", 
        "Authenticity", "Fortitude", "Innovation", "Tolerance", "Inclusion", "Health", "Fairness", 
        "Adaptability", "Responsiveness", "Wisdom", "Resourcefulness", "Harmony", "Open-mindedness", 
        "Reconciliation", "Honour", "Duty", "Sacrifice", "Love", "Gratitude", "Purpose", "Hope", 
        "Inclusivity", "Advocacy", "Participation", "Agency", "Human Rights", "Civil Liberties", 
        "Nonviolence", "Volunteerism", "Interconnectedness", "Civic Duty", "Dignity", "Shared Prosperity", 
        "Cultural Heritage", "Justice for All", "Personal Growth", "Vision", "Restorative Justice", 
        "Empowerment", "Innovation", "Lifelong Learning", "Spirituality", "Environmental Justice", 
        "Food Security", "Water Rights", "Public Health", "Economic Fairness", "Climate Action", 
        "Simplicity", "Shared Responsibility", "Peacebuilding", "Human Potential", "Compromise", 
        "Understanding", "Social Cohesion", "Financial Literacy", "Work-Life Balance"
    ]

    icons = [
        "balance_scale", "freedom", "gavel", "favorite", "eco", "lightbulb", "groups", 
        "fact_check", "local_fire_department", "verified", "diversity_3", "visibility", "volunteer_activism", 
        "self_improvement", "security", "public", "how_to_reg", "nature_people", "trending_up", "explore", 
        "school", "spa", "emoji_people", "thumb_up", "brush", "emoji_nature", "healing", "celebration", 
        "emoji_events", "done", "emoji_objects", "hourglass_top", "group_work", "fitness_center", 
        "group_add", "psychology", "leaderboard", "equaliser", "how_to_vote", "scale", "self_care", 
        "wb_sunny", "volunteer_activism", "mood", "science", "auto_awesome", "track_changes", 
        "star", "security_update", "emoji_flags", "public", "favorite_border", "accessibility_new", 
        "recycling", "engineering", "local_activity", "local_see", "emoji_transportation", "gavel", 
        "military_tech", "security", "emoji_nature", "cloud_queue", "support", "all_inclusive", "done_all", 
        "diversity_3", "feedback", "emoji_flags", "rule", "account_balance", "policy", "voice_over_off", 
        "gesture", "share", "family_restroom", "supervised_user_circle", "workspaces", "important_devices", 
        "drive_eta", "language", "auto_fix_normal", "light_mode", "hourglass_empty", "how_to_reg", 
        "shield", "architecture", "bubble_chart", "emoji_transportation", "science", "policy", "bathtub", 
        "settings_brightness", "account_circle", "switch_access_shortcut", "code", "emoji_nature", 
        "settings_system_daydream", "sports_soccer", "watch_later", "emoji_people", "home_work", 
        "emoji_food_beverage", "build_circle",
    ]
    negative_values = [
        "Greed",          # Uncontrolled desire for wealth and power
        "Corruption",     # Dishonesty and unethical behavior for personal gain
        "Exploitation",   # Taking unfair advantage of others
        "Deception",      # Misleading or lying to others
        "Intolerance",    # Lack of respect for others' beliefs or differences
        "Ignorance",      # Willful disregard of knowledge or truth
        "Violence",       # Physical or emotional harm to others
        "Manipulation",   # Controlling or influencing others for selfish purposes
        "Discrimination", # Unfair treatment based on prejudice
        "Indifference"    # Lack of concern or empathy for others
    ]

    negative_icons = [
        "money_off",            # Greed
        "dangerous",            # Corruption
        "pan_tool",             # Exploitation
        "visibility_off",       # Deception
        "block",                # Intolerance
        "report_problem",       # Ignorance
        "gavel",                # Violence
        "psychology_alt",       # Manipulation
        "do_not_disturb_alt",   # Discrimination
        "remove_circle",        # Indifference
    ]

    neutral_values = [
    "Stability",
    "Structure",
    "Efficiency",
    "Balance",
    "Tradition",
    "Consistency",
    "Adaptability",
    "Simplicity",
    "Precision",
    "Neutrality",
    "Order",
    "Pragmatism",
    "Moderation",
    "Routine",
    "Resourcefulness",
    "Predictability",
    "Autonomy",
    "Conformity",
    "Transparency",
    "Objectivity",
    "None",
    "Pride",
	"Greed",
	"Lust",
	"Envy",
	"Gluttony",
	"Rage",
	"Apathy",
    ]

    
    def add_new_value():
        new_value = '🎁 ' + st.session_state.new_value_input
        if new_value and new_value not in st.session_state['custom_values']:
            st.session_state['custom_values'].append(new_value)
            st.toast(f"Added new value: {new_value}")

    values = values + negative_values + neutral_values
    values = values + st.session_state['custom_values']
    icons = icons + negative_icons + icons[0:len(neutral_values)]
    icons = icons + ["new"] * len(st.session_state['custom_values'])

    # if not st.session_state.reshuffled:
    #     _reshuffle(values)
    #     st.session_state.reshuffled = True
        
    
    new_value_input = survey.text_input("Add your unique value to the list", key="new_value_input")
    st.button("Add a new value (clears the board)", on_click=add_new_value, use_container_width=True)
    
    selected_value = pills("Select a handful of the values that you most reflect in your actions", values, icons, multiselect=True, clearable=True, index=None)
    
    """
    # Unerstanding Worldviews
    
Understanding each other's worldviews is crucial for creating a social contract that reflects collective values and fosters cooperation. Each individual's perspective is shaped by culture, experiences, and the environment, and these diverse worldviews influence how we approach issues like justice, governance, and sustainability.

In the context of constructing a social contract, knowing each other's worldviews allows us to:

1.	**Bridge differences**: By recognizing different perspectives, we can build bridges rather than divisions, ensuring that no viewpoint is left unheard.
2.	**Shape inclusive solutions**: Solutions to complex societal challenges must consider varying worldviews, whether rooted in cultural, spiritual, or philosophical beliefs.
3.	**Encourage empathy**: Understanding how others see the world promotes empathy, making space for more nuanced discussions that honor every participant's lived reality.

By exploring and integrating these diverse worldviews, we can create a social contract that reflects our shared humanity and common goals, while also respecting our differences.
    """
    
    """

Different worldviews provide unique insights into how humans relate to the universe, nature, and each other. Would you like to explore how these perspectives could influence the social contract or other aspects of our work?

We've identified **five qualitatively distinct worldviews**, each of which highlights different and complementary traits in the way we approach the world. As products of exchange, dialogue, and experience, we believe your worldview will resonate with many of these perspectives.

But more than that, your personal worldview is likely to be a unique blend of these singular standpoints—a mix of cultural, philosophical, and personal views.

_**Let's play!**_ Together, we'll explore what defines our collective worldview. Through this exercise, we'll discover how our individual perspectives come together to shape the shared vision we'll use to build our social contract.

## We've identified **five qualitatively distinct worldviews**

### 1. **Mechanical**: 
This view sees **the universe and life as a machine**, with components working together in predictable, mechanical ways. It emphasises control, order, and predictability, with humans as parts of a larger "machine" governed by natural laws.

### 2. **Organic**: 
The organic worldview sees life and **the universe as a living, interconnected system**, like a biological organism. It emphasises harmony, interdependence, and growth, where all parts are intimately connected and affect each other.

### 3. **Dramatic**: 
The third worldview is **dramatic or playful**. In this view, life is seen as a cosmic drama or play, where existence is an unfolding, dynamic performance rather than something rigid or predetermined. This perspective celebrates spontaneity, creativity, and the notion that life is to be experienced like a game or theatrical performance, rather than something to be controlled or merely survived.


### 4. **Shamanic or Animistic**
The **Shamanic worldview** is deeply rooted in **animism**, the belief that all living and non-living things—such as animals, plants, rivers, and even rocks—have a spirit. This perspective, often found in indigenous Amazonian cultures, views the world as a complex, interconnected web of relationships between humans, nature, and spiritual forces.


### 5. **Ubuntu**
In many African cultures, the **Ubuntu** philosophy represents a worldview that emphasises **collective humanity**, interdependence, and shared responsibility. The phrase often associated with Ubuntu is: “**I am because we are**,” highlighting the deep connection between individuals and their communities.

    """

    st.divider()

    # Worldview statements for the game

    worldviews = {
        "Mechanical": {
            "in_accord": [
                "The universe operates like a precise clockwork mechanism, following fixed, predictable laws.",
                "Human progress is achieved through mastering and controlling nature via technology.",
                "Success is measured by efficiency and productivity, with everything in its rightful place.",
                "Order and predictability are essential for a stable society, and disruption is to be minimised.",
                "The individual's role is to fit into pre-defined systems, optimising their function within it."
            ],
            "in_disaccord": [
                "Life is spontaneous and cannot be reduced to predictable formulas or systems.",
                "Human beings should focus on emotional and spiritual growth rather than control and efficiency.",
                "The natural world is too complex and interconnected to be treated as a mere machine."
            ]
        },
        
        "Organic": {
            "in_accord": [
                "All beings and elements of nature are interconnected in a web of life.",
                "Growth and evolution occur naturally through balance and adaptation, not control.",
                "Humans are part of a larger living system and must respect nature's cycles and rhythms.",
                "Diversity in ecosystems and societies fosters resilience and strength.",
                "Healing and well-being come from harmony and alignment with natural forces."
            ],
            "in_disaccord": [
                "Nature is something to be mastered, controlled, and manipulated for human benefit.",
                "The world can be fully understood and managed by breaking it down into separate, independent parts.",
                "Human progress is measured only by technological advancements and resource exploitation."
            ]
        },
        
        "Dramatic/Playful": {
            "in_accord": [
                "Life is a creative expression where spontaneity and improvisation are valued.",
                "Every individual plays a unique role in the cosmic drama, contributing to the collective story.",
                "Mistakes and failures are simply part of the playful unfolding of life, not to be feared.",
                "The world is a stage, and human existence is filled with opportunities for personal expression and creativity.",
                "Reality is flexible, open to interpretation, and subject to change based on the play of ideas."
            ],
            "in_disaccord": [
                "Life must follow strict rules, and spontaneity should be suppressed in favor of order and control.",
                "The world is a machine with no room for creativity or improvisation.",
                "Success is about efficiency and productivity, not playfulness and joy."
            ]
        },
        
        "Animistic": {
            "in_accord": [
                "Everything in nature, from animals to rivers, possesses a spiritual essence and is interconnected.",
                "Humans must live in harmony with the natural world and respect its spiritual forces.",
                "Rituals and offerings are vital for maintaining balance between the human and spiritual realms.",
                "The Earth is a living being, and its well-being is inseparable from our own.",
                "Knowledge comes from deep, direct experience with nature and the spirit world, not from abstract reasoning."
            ],
            "in_disaccord": [
                "Nature is devoid of spirit and exists solely for human exploitation and control.",
                "Progress is measured by the extraction of natural resources without regard for environmental consequences.",
                "Humans are superior to other living beings and should dominate the natural world."
            ]
        },
        
        "Ubuntu": {
            "in_accord": [
                '"I am because we are" – Human beings are fundamentally interconnected and interdependent.',
                "Collective well-being is more important than individual success, and compassion guides decision-making.",
                "Shared responsibility and mutual support are key to a thriving community.",
                "Dignity and respect must be afforded to all members of the community, regardless of their differences.",
                "Humanity is enriched through cooperation, generosity, and a sense of belonging to the collective."
            ],
            "in_disaccord": [
                "Individualism and self-interest should guide actions, with little regard for the community.",
                "Success is measured by individual wealth and status, rather than shared prosperity.",
                "The needs of the collective are secondary to personal ambition and competition."
            ]
        }
    }
        # Function to display choices
    def display_choices(worldview):
        st.write(f"\nWorldview: {worldview}\n")
        st.write("In Accord Statements:")
        for i, statement in enumerate(worldviews[worldview]["in_accord"], 1):
            st.write(f"{i}. {statement}")
        
        st.write("\nIn Disaccord Statements:")
        for i, statement in enumerate(worldviews[worldview]["in_disaccord"], 1):
            st.write(f"{i}. {statement}")
            
    # Function to assign unique IDs to statements
    def assign_ids(worldviews):
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
    statement_dict = assign_ids(worldviews)
    
    # if st.button("Display Choices"):
    
    # st.write(st.session_state['current_element'])
    
    if st.session_state['current_element'] == None:
        statement = list(statement_dict.items())[-1]
    else:
        statement = st.session_state['current_element']
    
    
    f"""
    
    # How our worldviews are a unique blend?
    
      
    
    ### _{statement[1]["statement"]}_ 
    """
    

    name = 'there'
    _id = len(st.session_state['choices'])
    """
    
    #### On this scale, how well do you resonate with the statement? Match your feeling and hit the button 'Send vibe'. 
    
    A new sentence will appear, take the time to send a few vibes.
    
    """


    resonance_levels = {
        0.0: {
            "title": "Dissonance",
            "subtitle": "Complete Disagreement",
            "description": "This statement does not resonate with me at all. It feels distant from my beliefs, values, or worldview, and I find myself fundamentally disagreeing with its premise or implications."
        },
        0.25: {
            "title": "Low Resonance",
            "subtitle": "Mild Disagreement",
            "description": "I can see where this statement is coming from, but it doesn't align with my way of thinking. While I acknowledge its perspective, it feels incomplete or flawed to me, and I have reservations about it."
        },
        0.5: {
            "title": "Neutral",
            "subtitle": "Ambivalence",
            "description": "I find myself _somewhere_ in the middle. This statement neither fully resonates with me nor fully disagrees with my beliefs. I understand both sides of the argument and feel somewhat indifferent."
        },
        0.75: {
            "title": "High Resonance",
            "subtitle": "Partial Agreement",
            "description": "This statement resonates with me strongly. I can relate to its message and align with much of what it expresses, though there may be a few aspects where I hesitate or need further clarity."
        },
        1.0: {
            "title": "Full Resonance",
            "subtitle": "Complete Agreement",
            "description": "I completely resonate with this statement. It aligns perfectly with my values, worldview, and understanding of the topic. I fully endorse and support what it stands for."
        }
    }

    def get_resonance_level(user_value, levels):
    # Find the nearest key in resonance_levels to the user's input
        nearest_key = min(levels.keys(), key=lambda x: abs(x - user_value))
        return nearest_key, levels[nearest_key]
    
    # Lambda function to retrieve the corresponding nuanced trust description
    inverse_choice = lambda x: resonance_levels.get(x, {"title": "Invalid", "subtitle": "", "description": "Invalid resonance level."})

    def _display_nuance(trust_level):
    # Check if trust_level has the necessary keys
        if "title" in trust_level and "subtitle" in trust_level and "description" in trust_level:
            # Display the information
            st.markdown(f"## {trust_level['title']}")
            st.markdown(f"### *{trust_level['subtitle']}*")
            st.write(trust_level['description'])
        else:
            st.write("Invalid resonance level data.")


    dicho = my_create_dichotomy(key = f"resonance_statement",
                                id= f"resonance",
                        kwargs={'survey': survey,
                            'label': f'resonance_statement', 
                            'question': 'This is how I resonate',
                            'gradientWidth': 60,
                            'height': 250,
                            'title': '',
                            'name': f'fellows',
                            'messages': ["", "", ""],
                            }
                        )
    
    if dicho is not None:
        _resonance = get_resonance_level(float(dicho), resonance_levels)
        _display_nuance(inverse_choice(_resonance[0]))

    def update_state(value):
        # Append the current element and result to the results list
        st.session_state.results.append({
            "element": statement,
            "result": value
        })
        
        # Pick two new random statements for the next round
        st.session_state.current_element = random.choice(list(statement_dict.items()))

    st.button("Send vibe", use_container_width=True, on_click=update_state, args=(dicho,), type="primary")
    
    st.markdown("## The values you bring into the Contract:")
    if selected_value is not None:
        for value in selected_value:
            st.write(f"🌟 {value}")
    
    st.markdown("## Worldview results:")
    results = st.session_state['results']
    # generate_review(results)
    # resonances = resumes_statements(results)
    
    # st.json(st.session_state.results)
    # st.json(survey.data, expanded=False)
    
    
    """
    # HERE GOES THE VISUALISATION
    """

    extracted_data = [{"hash": item["element"][1]["hash"], "result": item["result"]} for item in results]
    
    serialised_data = {"values": selected_value, "worldview": extracted_data}

    st.session_state['serialised_data'] = serialised_data
    """
    The button below integrates the data into the bigger picture.
    
    """
    
    # _form_submit = lambda: outro()
    
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
        st.markdown(f"#### Sign #`{mask_string(st.session_state['username'])}`.")

    """
    # HERE GOES THE ANSWER // WHAT DOES THIS MEAN
    
    what does it mean for the world that we are driven by ...
    what does it mean that we are driven by ...
    what does somebody driven by do...
    """

    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
