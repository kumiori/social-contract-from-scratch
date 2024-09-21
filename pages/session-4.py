import streamlit as st
import requests
import time
from numpy import around
if st.secrets["runtime"]["STATUS"] == "Production":
    st.set_page_config(
        page_title="The Social Contract from Scratch • Relations, Systems & Healing",
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
from streamlit_timeline import timeline

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


current_year = datetime.now().year

timeline_data = {
    "title": {
        "media": {
          "url": "",
          "caption": " <a target=\"_blank\" href=''>credits</a>",
          "credit": ""
        },
        "text": {
          "headline": "Our Timeline",
          "text": "<p>An integrated collective timeline</p>"
        }
    },
    "events": [
      {
        "media": {
          "url": "https://vimeo.com/1007606689",
          "caption": "How to (<a target=\"_blank\" href='https://'>credits </a>)"
        },
        "start_date": {
          "year": current_year,
          "month":"10"
        },
        "text": {
          "headline": "Athena's Collective<br> participatory timelines.",
          "text": "<p>Athena's Collective is ... </p>"
        }
      },
      {
        "media": {
          "url": "https://vimeo.com/1007188309",
          "caption": "Athena (<a target=\"_blank\" href='https://streamlit.io/'>credits</a>)"
        },
        "start_date": {
          "year": current_year,
          "month":"7",
          "day":"13"
        },
        "text": {
          "headline": "Event<br>version 0.1",
          "text": "Streamlit lets you turn data scripts into sharable web apps in minutes, not weeks. It's all Python, open-source, and free! And once you've created an app you can use our free sharing platform to deploy, manage, and share your app with the world."
        }
      },
    ]
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

    st.markdown("# <center>Consent & Action</center>", unsafe_allow_html=True)
    st.markdown("## <center>What Are We Consenting To?</center>", unsafe_allow_html=True)

    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')} - Session 4", unsafe_allow_html=True)

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
                            'question': 'Are you ready to donate? (White: Yes, Black: No, Nuances: I need time)',
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

    
if __name__ == "__main__":
    
    intro()

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")

    authentifier()

    """
    Our focus shifts to Consent and Action — a critical reflection on the commitments we make through the Social Contract. 
    
    Consent isn't just passive agreement; it's an active choice that shapes how we live, govern, and engage with one another.
    
    As a first step we will engage in a Consent Game—an interactive exercise designed to explore the classical understanding of the social contract. In the traditional framework, the individual consents to surrender certain personal liberties in exchange for protection and governance by a sovereign entity. 
    
    However, crucially, the individual is excluded from participating in the actual decision-making process. This game will allow us to test the implicit assumption that everyone naturally agrees to such a deal.


    After reflecting on this classical model, we will expand the scope to consider a larger, more inclusive modern social contract. Here, we pose a fundamental question:

    ### Does consent to live in society simply mean coexisting, or does it imply deeper responsibilities toward others?

    """
    st.divider()

    """
    # HERE GOES THE CONSENT GAME
    """
    """
    # HERE GOES THE REVIEW
    """
    
    """
    # SECOND PART
    
    ### What commitments are we making to each other and to the broader community?

    This shift invites us to reconsider the nature of consent and action, encouraging us to think critically about the responsibilities and commitments that form the foundation of a truly inclusive and participatory social contract.
    
    In common usage, a commitment is a declaration of intent—a promise or obligation for the future, an agreement to act or uphold certain values. In programming, however, a commit refers to a definitive action where changes to a project are finalized and recorded. This dual meaning can guide us in thinking about commitments in the context of the social contract: both as a future-oriented promise and as a recorded action, solidified within a community structure.
    """    
    equaliser_data = [
            ("Curated Publication", ""),
            ("...", ""),
            ("Arts", ""),
            ("Events", ""),
            ]

    create_equaliser(key = "equaliser", id= "equaliser", kwargs={"survey": survey, "data": equaliser_data})

    
    responsibility_levels = {
    0.0: {
        "title": "Bare Co-Existence",
        "subtitle": "Minimal responsibility",
        "description": "Individuals share the same space but have no obligations toward each other beyond avoiding direct harm."
    },
    0.1: {
        "title": "Tolerance",
        "subtitle": "Accepting differences without interaction",
        "description": "Individuals peacefully tolerate one another's presence and differences without engaging in deeper social responsibilities."
    },
    0.2: {
        "title": "Non-Interference",
        "subtitle": "Avoiding harm or disruption",
        "description": "Individuals avoid actions that could harm or disrupt others’ lives, but without actively engaging or supporting one another."
    },
    0.3: {
        "title": "Basic Respect",
        "subtitle": "Acknowledging dignity",
        "description": "Individuals are responsible for recognizing and respecting each other's dignity in social interactions, maintaining basic societal norms."
    },
    0.4: {
        "title": "Civic Engagement",
        "subtitle": "Active participation in societal duties",
        "description": "Individuals engage in civic responsibilities beyond mere compliance, including contributing to local governance, community decision-making, and advocating for policies that benefit society as a whole."
    },
    0.5: {
        "title": "Community Support",
        "subtitle": "Helping in times of need",
        "description": "Individuals offer support to their community during crises, through volunteering, helping neighbors, or providing mutual aid."
    },
    0.6: {
        "title": "Collaboration",
        "subtitle": "Working together for a common cause",
        "description": "Individuals actively collaborate to solve shared challenges, pooling resources and knowledge for the benefit of the group."
    },
    0.7: {
        "title": "Shared Accountability",
        "subtitle": "Ensuring fairness collectively",
        "description": "Individuals hold themselves and others accountable for upholding community standards, actively ensuring fairness and justice."
    },
    0.8: {
        "title": "Collective Care",
        "subtitle": "Responsibility for well-being",
        "description": "Individuals take responsibility for the well-being of others, contributing to health, education, and overall community welfare."
    },
    0.9: {
        "title": "Deep Interdependence",
        "subtitle": "Mutual reliance for a better future",
        "description": "Individuals understand that their own well-being is tied to that of others, and their actions reflect a deep ethical commitment to the collective."
    },
    1.0: {
        "title": "Interdependent Responsibility",
        "subtitle": "Comprehensive care for the planet and others",
        "description": "The highest level of responsibility, where every action is taken with consideration for its impact on others, future generations, and the planet."
    }
}
    
    
        # Lambda function to retrieve the corresponding nuanced trust description
    inverse_choice = lambda x: responsibility_levels.get(round(x, 1), {"title": "Invalid", "subtitle": "", "description": "Invalid trust level."})

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
                            'question': 'Is this a dichotomy?',
                            'gradientWidth': 100,
                            'height': 250,
                            'title': '',
                            'name': f'there',
                            'messages': ["", "", ""],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )
            
    # st.markdown(f'## {inverse_choice(float(dicho))}')
    if dicho is not None:
        _display_nuance(inverse_choice(float(dicho)))

    
    """
    # HERE GOES THE THIRD PART
    
## New forms of collaboration and systems of transparency.

Do we need transparency?
_Yes!_, transparency is essential to ensure that 
// commitments and responsibilities are upheld. 

Without systems of XXX, mutual responsibilities become merely aspirational, lacking the enforcement needed to ensure fairness, justice, and the well-being of all members of society.

1.	Transparent _Peer_ Review Systems: Individuals or groups regularly review each other’s contributions and adherence to community standards or responsibilities, providing feedback and corrective action if necessary.
2.	Transparent Reporting: A system where actions and decisions are documented and openly shared with all stakeholders, allowing for public scrutiny and ensuring that everyone is held accountable to their commitments.
3.	Collective Decision-Making: Group decisions are made collectively, with individuals being held accountable for their part in the process and for the results of the collective decision.
5.	Restorative Models: When XXX is breached, systems focus on healing and restoring relationships, rather than punishment. Individuals are responsible for making amends through actions that benefit the harmed party and the community.
6.	Automated Tracking & Feedback: Utilising technology, systems can track individual and collective actions against agreed-upon goals, providing real-time feedback on how well individuals or groups are adhering to their responsibilities.
7.	Public Acknowledgment & Reward Systems: A positive reinforcement model where individuals who consistently meet or exceed their responsibilities are publicly acknowledged or rewarded, creating an incentive for others to follow suit.
    """
    
    """
    # HERE GOES THE INTEGRATION
    """
    
    options = {"selectable": True, 
                "multiselect": True, 
                "zoomable": True, 
                "verticalScroll": True, 
                "stack": False,
                "height": 200, 
                "margin": {"axis": 5}, 
                "groupHeightMode": "auto", 
                "orientation": {"axis": "top", "item": "top"}}
    timeline(timeline_data, height=800)
    
    
    
    
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



    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
