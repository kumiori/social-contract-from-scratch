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

st_gtag(
    key="gtag_app_XXX",
    id="G-Q55XHE2GJB",
    event_name="s&p_main_page",
    params={
        "event_category": "apply_s&p",
        "event_label": "test_s&p",
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
       
if 'price' not in st.session_state:
    st.session_state.price = .01

philanthropic_profiles = {
'Communitarian': {
    'description': '## _**Doing good** makes sense for the community._ My contributions create ripple effects that strengthen social bonds and uplift all those around.',
    'icon': ':material/group:'
},
'Devout': {
    'description': '## _**Doing good** is the will of a higher power_. My philanthropy is a sacred duty, a way to serve and fulfill my spiritual inspiration.',
    'icon': ':material/auto_awesome:'
},
'Investor': {
    'description': '## _**Doing good** is good business._ I see philanthropy as an investment, generating returns not just for society, but for the world at large.',
    'icon': ':material/monetization_on:'
},
'Socialite': {
    'description': '## _**Doing good** is sexy._ My generosity is a symbol of commitment and influence, making waves in social circles while benefiting the greater good.',
    'icon': ':material/party_mode:'
},
'Repayer': {
    'description': '## _**Time to give back**._ I have received much from society, and now it\'s my turn to return the favor and support the what\'s coming.',
    'icon': ':material/replay:'
},
'Dynast': {
    'description': '## _**Following family tradition**._ Philanthropy is in my blood, a legacy passed down through generations, and I proudly carry the torch.',
    'icon': ':material/family_restroom:'
},
'Altruist': {
    'description': '## _**Giving from the heart**._ My generosity expands my boundaries; I give selflessly and with deep compassion, driven by a love for humanity.',
    'icon': ':material/favorite:'
},
'Indifferent': {
    'description': '## _**I don\'t give a shit about philanthropy**_ or social causes. I believe that everyone should fend for themselves, and I see no reason to contribute.',
    'icon': ':material/block:'
},
'Deflector': {
    'description': '## _**Social questions are somebody else\'s problem**._ I believe that social issues and philanthropy are for others to worry about, not my concern or responsibility.',
    'icon': ':material/warning:'
}
}  

# Replace with your SumUp API credentials
API_BASE_URL = 'https://api.sumup.com/v0.1'
ACCESS_TOKEN = st.secrets["sumup"]["CLIENT_API_SECRET"]

mask_string = lambda s: f"{s[0:4]}***{s[-4:]}"

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

def outro():
    st.markdown("## <center> Step X: _Chapter One_</center>", unsafe_allow_html=True)
    
    # st.write(st.session_state['tx_tag'])
    # st.write(st.session_state['checkouts']['id'])
    
    dashboard_data = {**st.session_state['serialised_data'], 'checkout': st.session_state['checkouts'], 'checkout_tag': st.session_state['tx_tag']}
    
    
    st.session_state['serialised_data'] = dashboard_data
    
    st.markdown(
        """
        Congrats! It was cool to navigate through the process of engaging in our philanthropic initiative. Hit the Submit button below to initiate your dashboard.
        
We look forward to seeing how this commitment will unfold.
    
        Thank you for your interest. We will get back to you by email.
    
        """
"""
_In the meantime_:"""
"""
Here is a snapshot of current activities and developments. Any insight to share?
"""
# This includes updates on ongoing projects, conceptual ideas in the pipeline, and longer-term ventures that are now yielding positive results. 
"""
	1. Health Systems: Addressing the pervasive collapse of health systems, exacerbated by the pandemic and sectarian influences.
	2. Monetisation: Pressing cyanotypes from experimental human campaigns, economic photography and scientific reflection.
	3. Scientific Projects: Energy jumps and the stability of the cryosphere, contributing to our understanding of the impact of ice fracture on climate dynamics.
	4. Philosophical Dinners: Hosting gastronomic events where ideas are served through meals, connecting intellectual and cultural exchange within experience.
    5. Artistic Endeavours: Exploring the arts, with a focus on music, the natural world, ceramics, and illustration.
    6. Literature: Communication within the Urban Jungle: the vertical scenario. 
""")
    with st.spinner("Thinking?"):
        time.sleep(1)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        text = """
            Any preference or strong inclination? To your taste of insights and ideas - a question - we submit to your attention:
        _“how to share?”_

        Your insight could provide the next key piece in this collaborative puzzle. 

        Reach out by email, _submit_ your thoughts — each is a step that brings ideas closer to reality.

        <social.from.scratch@proton.me>

            """
        stream_once_then_write(text)
        # st.markdown(text)
        if st.session_state['authentication_status']:
            st.toast(f'Authenticated successfully {mask_string(st.session_state["username"])}')
            col1, col2, col3 = st.columns([1, 1, 1])
            # with col2:
                # authenticator.logout()
        st.markdown("""
        `Click "Submit" to save your dashboard.`
        """)

@st.cache_data
def _reshuffle(values):
    import random
    random.shuffle(values)


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

    st.markdown("## <center>XX.</center>", unsafe_allow_html=True)

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
        st.write(element)

        statement = element[1]["statement"]
        worldview = element[1]["worldview"]
        category = element[1]["category"]
        
        # Interpret result
        if result["result"] == "1":
            choice = f"I fully resonated with the 1st statement from the {worldview} worldview."
        elif result["result"] == "0":
            # choice = f"I fully resonated with the statement: '{statement_1}' from the {worldview_1} worldview."
            choice = f"I fully resonated with the 2nd statement from the {worldview} worldview."
        else:
            choice = f"Your resonance was divided, showing agreement or disagreement with both statements."

        # Format the review
        # st.write(f"### Review of Interaction {idx + 1}:")
        # st.write(f"**Statement 1** ({worldview_1} - {category_1}): {statement_1}")
        # st.write(f"**Statement 2** ({worldview_2} - {category_2}): {statement_2}")
        st.write(f"**Result**: {choice}")
    st.write("---")    


if __name__ == "__main__":
    
    intro()

    authentifier()

    """
    # FIRST SESSION
    
    """
    st.markdown(f"# <center>Values and Worldview</center> ", unsafe_allow_html=True)
    # st.markdown("# Values and Worldview")

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")
    
    # authenticate()

    # Sample page for "Values and Worldview"
    st.markdown("### Introduction")
    
    st.markdown("Our worldview shapes the very core of our beliefs, actions, and how we interact with others. "
                "By sharing these values, we build the foundation for any social contract.")
    # authenticate()
    st.markdown("From philosophical, social, and economic perspectives, our worldview creates boundaries and possibilities.")
    st.markdown("### Question")
    st.write("""
             Which values do you embody?
Which values do you see reflected in yourself, and which ones guide your everyday actions?
             
These are core values that guide the construction of a new social contract.""")
    
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

    neutral_values = neutral_values = [
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
    "None"
    ]

    
    def add_new_value():
        new_value = '🎁 ' + st.session_state.new_value_input
        if new_value and new_value not in st.session_state['custom_values']:
            st.session_state['custom_values'].append(new_value)
            st.toast(f"Added new value: {new_value}")
            

    values = values + negative_values + neutral_values
    values = values + st.session_state['custom_values']
    icons = icons + negative_icons + ["new"] * len(neutral_values)
    icons = icons + ["new"] * len(st.session_state['custom_values'])

    _reshuffle(values)
    
    # num_values = st.slider("Select the number of neutral values to display", 1, len(values), 5)

    # Example usage in a Streamlit app:
    
    selected_value = pills("Select values", values, icons, multiselect=True, clearable=True, index=None)
    
    new_value_input = survey.text_input("Add a new value", key="new_value_input")
    
    """
    # HERE GOES THE CONTEXT/INTRO
    """
    
    """

Each of these worldviews provides unique insights into how humans relate to the universe, nature, and each other. Would you like to explore how these perspectives could influence the social contract or other aspects of your work?


### 1. **Mechanical**: 
This view sees the universe and life as a machine, with components working together in predictable, mechanical ways. It emphasises control, order, and predictability, with humans as parts of a larger "machine" governed by natural laws.

### 2. **Organic**: 
The organic worldview sees life and the universe as a living, interconnected system, like a biological organism. It emphasises harmony, interdependence, and growth, where all parts are intimately connected and affect each other.

### 3. **Dramatic**: 
The third worldview is **dramatic or playful**. In this view, life is seen as a cosmic drama or play, where existence is an unfolding, dynamic performance rather than something rigid or predetermined. This perspective celebrates spontaneity, creativity, and the notion that life is to be experienced like a game or theatrical performance, rather than something to be controlled or merely survived.


### 4. **Shamanic or Animistic Worldview**
The **Shamanic worldview** is deeply rooted in **animism**, the belief that all living and non-living things—such as animals, plants, rivers, and even rocks—have a spirit. This perspective, often found in indigenous Amazonian cultures, views the world as a complex, interconnected web of relationships between humans, nature, and spiritual forces.


### 5. **Ubuntu Worldview**
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
            
    import hashlib
    import random
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
        
    # st.subheader(f"Statement (ID {statement[0][1]})")
    f"""
    ### {statement[0][1]["statement"]}
    # """
    

    name = 'there'
    _id = len(st.session_state['choices'])
    """
    
    ## On this scale, how well do you resonate with the statement?
    
    """
    
    _msg_labels = ["*Not at all* I resonate with the statement!", 
                                         "*I do resonate* with statement!",
                                         "*Intermediate*...", 
                                         ],
    dicho = my_create_dichotomy(key = f"choice",
                                id= f"choice",
                        kwargs={'survey': survey,
                            'label': f'choice', 
                            'question': 'This is how I resonate',
                            'gradientWidth': 60,
                            'height': 250,
                            'title': '',
                            'name': f'{name}',
                            'messages': ["", "", ""],
                            }
                        )

    def update_state(value):
        # Append the current element and result to the results list
        st.session_state.results.append({
            "element": statement,
            "result": value
        })
        
        # Pick two new random statements for the next round
        st.session_state.current_element = random.sample(list(statement_dict.items()), 2)

    st.button("Submit", use_container_width=True, on_click=update_state, args=(dicho,), type="primary")
    
    st.write("Retrieved values:")
    if selected_value is not None:
        for value in selected_value:
            st.write(f"🌟 {value}")
        
    results = st.session_state['results']
    generate_review(results)
    resonated, both = resumes_statements(results)
    
    st.write(f"Resonated statements: {resonated}")
    st.write(f"Both statements: {both}")

    
    st.json(st.session_state.results)
    st.json(survey.data, expanded=False)
    
    
    """
    # HERE GOES THE INTEGRATION
    """
    st.session_state['serialised_data'] = survey.data
    """
    The button below integrates the data into our database.
    
    """
    _form_submit = lambda: outro()
    if st.button("Integrate the Bigger Picture", key="integrate", help="Integrate your data", 
              disabled=not bool(st.session_state['authentication_status']), 
              type='primary',
              use_container_width=True,
              on_click=lambda: _form_submit()):
        """
        Congratulations!

Check back in a few days or reach out to us by email. 

social.from.scratch@proton.me

How you feel about the results?"""
        
    if st.session_state['authentication_status']:
        st.markdown(f"#### Sign #`{mask_string(st.session_state['username'])}`.")
    
    """
    # HERE GOES THE VISUALISATION
    """


    """
    # HERE GOES THE ANSWER // WHAT DOES THIS MEAN
    
    what does it mean for the world that we are driven by ...
    what does it mean that we are driven by ...
    what does somebody driven by do...
    """


    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
