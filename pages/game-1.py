import streamlit as st
import requests
import time
from numpy import around
if st.secrets["runtime"]["STATUS"] == "Production":
    st.set_page_config(
        page_title="The Social Contract from Scratch",
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
    event_name="XXX_main_page",
    params={
        "event_category": "apply_XXX",
        "event_label": "test_XXX",
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
                    'game-1': json.dumps(serialised_data)
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

    st.markdown("# <center>The Social Contract from Scratch</center>", unsafe_allow_html=True)

    st.markdown("## <center>A meeting of Social and Natural Sciences, Philosophy, and Arts.</center>", unsafe_allow_html=True)

    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}")

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


def exp_to_actual(value):
    return 10**value

def question():
    inverse_choice = lambda x: x
    name = 'there'
    # Dictionary containing trust levels and their nuanced descriptions
    trust_levels = {
        0.0: {
            "title": "Zero Trust",
            "subtitle": "Complete distrust",
            "description": "You do not believe the financial system is fair, reliable, or trustworthy. You expect corruption, manipulation, or collapse at every level."
        },
        0.1: {
            "title": "Extremely Low Trust",
            "subtitle": "Skeptical and deeply distrustful",
            "description": "You have serious doubts about the system’s integrity and suspect that it primarily serves the interests of a few at the expense of many."
        },
        0.2: {
            "title": "Very Low Trust",
            "subtitle": "Barely any trust",
            "description": "You perceive the system as fundamentally flawed but acknowledge that it might work in certain situations, although rarely in your favor."
        },
        0.3: {
            "title": "Low Trust",
            "subtitle": "Cautious and wary",
            "description": "While acknowledging some potential benefits of the system, you remain highly cautious. You believe that the risks outweigh any possible advantages."
        },
        0.4: {
            "title": "Hesitant Trust",
            "subtitle": "Reluctant to trust",
            "description": "You are hesitant to engage with the financial system unless necessary, often choosing alternatives or self-reliance. Trust is reserved and given only reluctantly."
        },
        0.5: {
            "title": "Neutral",
            "subtitle": "A balance of skepticism and hope",
            "description": "Your trust in the system is neither high nor low. You see both its potential and its flaws and are willing to engage, but you remain watchful for any signs of manipulation or inefficiency."
        },
        0.6: {
            "title": "Moderate Trust",
            "subtitle": "Leaning towards trust",
            "description": "You believe the system can be beneficial in certain contexts, but you maintain some skepticism. You see the potential for positive outcomes but remain cautious."
        },
        0.7: {
            "title": "Considerable Trust",
            "subtitle": "Generally trusting",
            "description": "You trust the system to work in your favor most of the time. Though you're aware of its imperfections, you believe it generally functions as intended."
        },
        0.8: {
            "title": "Strong Trust",
            "subtitle": "Confident in the system",
            "description": "You have strong confidence that the financial system operates fairly and transparently. You expect it to provide stability and security in most cases."
        },
        0.9: {
            "title": "Very Strong Trust",
            "subtitle": "Almost complete trust",
            "description": "You believe that the system is reliable and dependable, providing fairness and opportunity. You engage with it confidently, trusting it to work as intended."
        },
        1.0: {
            "title": "Full Trust",
            "subtitle": "Complete and unwavering trust",
            "description": "You have absolute faith in the financial system's integrity, believing it to be just, stable, and efficient in all aspects. You have no reservations about its function."
        }
    }

    # Lambda function to retrieve the corresponding nuanced trust description
    inverse_choice = lambda x: trust_levels.get(round(x, 1), {"title": "Invalid", "subtitle": "", "description": "Invalid trust level."})

    # Example usage of the function
    test_value = 0.5
    result = inverse_choice(test_value)

    # Output the result
    # st.write(result)
    def _display_nuance(trust_level):
    # Check if trust_level has the necessary keys
        if "title" in trust_level and "subtitle" in trust_level and "description" in trust_level:
            # Display the information
            st.markdown(f"## {trust_level['title']}")
            st.markdown(f"### *{trust_level['subtitle']}*")
            st.write(trust_level['description'])
        else:
            st.write("Invalid trust level data.")

    dicho = my_create_dichotomy(key = "executive", id= "executive",
                        kwargs={'survey': survey,
                            'label': 'future_outlook', 
                            'question': 'Are you ready to express your trust?',
                            'gradientWidth': 100,
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
            
    # st.markdown(f'## {inverse_choice(float(dicho))}')
    if dicho is not None:
        _display_nuance(inverse_choice(float(dicho)))
    
if __name__ == "__main__":
    
    intro()
    st.markdown(f"# <center>Start With Game 1</center> ", unsafe_allow_html=True)

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")

    authentifier()
    # Sample page for "Game 1: Financial Trust Game"
    st.markdown("# Game 1: Financial Trust Game")
    st.markdown("### Introduction")
    st.markdown("The Financial Trust Game simulates the balance of trust and risk in economic transactions, "
                "mirroring real-world interactions between individuals, corporations, and the public.")
    st.markdown("### Context")
    st.markdown("This game helps us understand the level of trust participants have in financial transactions and systems. How it changes over time, how it stretches or breaks. Can be rebuilt?")
    st.markdown("### Question")
    st.write("How would you behave as an individual investor or the Trustee in this scenario? What factors would influence your decision?")
    trust_game_choice = st.radio("Select your role:", ["Investor", "the Bank"])
    st.write(f"You chose: {trust_game_choice}")

    if trust_game_choice == "Investor":
        # investment = st.slider("How much would you invest?", 0, 100)
        st.write(trust_game_choice)
        min_exp_value = 0
        max_exp_value = 5
        min_actual_value = 1
        max_actual_value = 100000-0.1

        exp_value = survey.slider(label = "How much would you invest?",
                                    id = "investment_slider", 
                                    min_value=float(min_exp_value), max_value=float(max_exp_value), value=float(min_exp_value),
                                step = 0.01,
                                format="%d")

        # Convert exponential value to actual value
        actual_value = exp_to_actual(exp_value)+0.1

        # Display the actual type: exp_value if actual value < 3000, otherwise -1
        donation_type = lambda x, t: int(x)+10 if t < 3000 else -1
        # st.write(f"Donation Value: {actual_value:.1f} EUR, Donation type: {int(exp_value)}")
        st.markdown(f"### You chose to invest: {actual_value:.1f} EUR")
        st.session_state["investment"] = actual_value
    elif trust_game_choice == "the Bank":
        return_percentage = st.slider("How much would you return to the investor?", 0, 1000)
        st.write(f"You chose to return: {return_percentage/10}%")
        st.warning("If you think this interface is inappropriate, please let us know how to improve.")
        
    """
    # HERE GOES THE FIRST QUESTION
    """
    st.divider()
    st.write("Game Trust is an experimental game designed to explore trust dynamics between investors and financial corporations.")
    """
We explore questions of trust, trustworthiness, and cooperation in social interactions. It's particularly interesting because it involves sequential decision-making, where one player's decision influences the other's subsequent decision. 

Trusting behavior often depends on many factors and it is difficult to estimate. The perceived trustworthiness of the partner plays a role, likewise perceived risks and rewards as well as social norms regarding cooperation and reciprocity. Transparency, clarity, how many other factors? This game allows us, researchers and players, to study how these factors influence decision-making and how trust and cooperation can emerge or break down in different situations.
And, more importantly, to foresee what are the outcomes.    
    """

    st.header("Disclaimer:")
    st.write("""
             `This game is a not a simulation and does reflect real-world financial transactions.
             Please play consciously.
             This game involves money, and the outcomes are real. Please play responsibly.
             What money really is, is a question that has been asked for centuries.
             This time, we ask you to play with it. Using it as a tool, to understand trust,
             to send encoded signals.
             `
    """)
    st.write('`A matter of trust, coded fast.`')
    st.write('`In an infinite-dimensional space of energy there are two players: player I and player B...`')
    st.header("Instructions:")
    st.write("In this game, you will act as an investor deciding how much trust to invest in the Bank, or as the Bank, or on behalf of the Bank.")
    st.write("XXX Your task is to choose a level of trust, represented by a value between 0 and 1.")
    st.write("XXX You will also have an initial capital to allocate to the bank, for you to gauge.")
    st.write("The bank has received a challenge: to XXX repay the investor's trust allocating a small part of its financial assets to the investor, to allow the investor XXX.")
    st.write("Will the Trustee accept the challenge and move the funds, or will it betray the investor's trust?")
    st.write("Based on your the investor's perceptions and the Bank's response, both players receive certain payoffs.")
    st.write("Remember, your level of trust can change and this is of utmost importance.")
    
    st.header("Gameplay:")
    st.write("0. Are you happy to pay? Save your preferences.")
    st.write("1. How do you Q-trust the Bank? (α) between 0 and 1 using the slider.")
    # st.write("2. Allocate an initial capital (C) to the bank.")
    st.write("2. The bank, or someone on their behalf, will decide whether to 'move' or 'betray'.")
    st.write("3. Based on the Bank's decision(s) and your trust level, things will unfold...")
    st.write("4. Rember: you can adjust your trust level at any time, increase is free - decrease leaves a small yet irreversible trace in logs of the Bank.")

    """
    # HERE GOES THE CONTEXT
    """
    """### Steps:
1. **Players**: The game involves two players: the investor and the bank (X). The investor is a collective player, each of its elements decides how much trust to invest in the Trustee, while the bank determines its response on their cost-opportunity.

2. **Trust Variable**: The investor's decision is represented by a trust variable (α), ranging from zero (no trust) to one (full trust), reflecting the level of trust invested in HSBC.

3. **Impact of Investment**: The investor's trust investment (α) is multiplied by their capital (C), determining the resources allocated to HSBC.

4. **Trustee's Decision**: the Trustee (or an entity on their behalf) chooses to "move" or "betray." Moving implies positive action towards allocating funds to transparently address challenges such as climate change, while betraying maintains the status quo, the bank gains - business as usual - at the investor's expense.

5. **Reciprocation**: If the Trustee moves, it allocates a portion of resources (β, a percentage of the Trustee's assets) to the investor. If it betrays, the resources are kept by the bank, business as usual.

6. **Outcome**: The payoffs for both players depend on the Trustee's decision and the investor's level of trust. Positive action by the Trustee and increased trust lead to mutual gains, betrayal results in systematic losses for the investor, and progressive erosion of the trust variable may shed new light on the bank's trustworthiness.

    """    
    
    st.divider()

    """
    # HERE GOES THE INTERACTION
    """
    question()
    """
    # HERE GOES THE REVIEW
    """

    """
    # HERE GOES THE AI INTEGRATION
    """

    """
    # Integrate your preferences and expand our picture
    
    If yes, you can review the data you've contributed before proceeding.
    
    """
    
    with st.expander("Review your data", expanded=False):
        st.json(survey.data)

    st.session_state['serialised_data'] = survey.data
    """
    The button below integrates the data into our database.
    
    """
    
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
        
        

    """
    # HERE GOES THE VISUALISATION
    """



    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
