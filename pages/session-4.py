import time

import requests
import streamlit as st
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

import pandas as pd
import philoui
import streamlit.components.v1 as components
import streamlit_shadcn_ui as ui
import yaml
from philoui.authentication_v2 import AuthenticateWithKey
from philoui.io import QuestionnaireDatabase as IODatabase
from philoui.io import (conn, create_dichotomy, create_equaliser,
                        create_qualitative, create_quantitative)
from philoui.survey import CustomStreamlitSurvey
from philoui.texts import hash_text, stream_text
from streamlit_elements import elements, mui, nivo
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row
from streamlit_gtag import st_gtag
from streamlit_player import st_player
from streamlit_timeline import timeline
from yaml import SafeLoader

st_gtag(
    key="gtag_app_XXX",
    id="G-Q55XHE2GJB",
    event_name="session4_main_page",
    params={
        "event_category": "session",
        "event_label": "_session4",
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

@st.cache_data    
def fetch_data():
    response = db.fetch_data(kwargs={'verbose': True})
    return response

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
        "end_date": {
          "year": current_year,
          "month":"11"
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
          "month":"9",
          "day":"26"
        },
        "end_date": {
          "year": current_year,
          "month":"9",
          "day":"29"
        },
        "text": {
          "headline": "The Social Contract From Scratch<br>Conference in Athens",
          "text": "Europe in Discourse IV."
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
                    'consent_00': json.dumps(serialised_data)
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
    
    st.markdown("""
    ### This is not a one-time deal. Just like society, consent evolves with new challenges and perspectives. You'll be part of that evolution.
    """)
    name = ''
    role = my_create_dichotomy(key = "socialcontract", id= "socialcontract",
                        kwargs={'survey': survey,
                            'label': 'willingness', 
                            'question': 'How willing are you to give up your freedoms? (Black: Zero, White: Fully, Nuances: Partial & Conditional)',
                            'gradientWidth': 20,
                            'height': 250,
                            'title': '',
                            'name': f'{name}',
                            'messages': ["I am unwilling! *Does not sound like a good deal,* let's question these fundamentals", 
                                         "*Plenty of willingness*. And full trust in the authority", 
                                         "*My willingness is* conditional"],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )
            
    


    """
1.	**Zero Willingness** emphasises individual liberty and distrust in giving up freedoms.
2.	**Conditional Willingness** highlights opennes to negotiation but under specific conditions, prompting reflection on those conditions.
3.	**Full Willingness** shows complete trust in the system and prioritises collective security and stability over personal freedom.
    """


def extract_willingness_and_timestamp(data):
    results = []
    for entry in data:
        # Check for willingness in consent_00 first, fallback on session_4
        consent_data = None
        if entry.get("session_4_consent_action"):
            consent_data = json.loads(entry["session_4_consent_action"])
        elif entry.get("consent_00"):
            consent_data = json.loads(entry["consent_00"])

        if consent_data:
            willingness = consent_data.get("willingness", {}).get("value")
            updated_at = entry.get("updated_at")
            if willingness and updated_at:
                # Convert the updated_at to a more readable format
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                results.append({"willingness": willingness, "updated_at": updated_at})

    return results
    
if __name__ == "__main__":
    
    intro()

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")

    authentifier()

    """
    ## Our focus shifts to Consent and Action 
    
    — a critical reflection on the commitments we make through the Social Contract. 

    This is where the theory meets the ground, where ideas turn into actionable processes.

    Consent isn't just passive agreement; it's an active choice that shapes how we live, govern, and engage with one another.
    
    As a first step we will engage in a Consent Game—an interactive exercise designed to explore the classical understanding of the social contract. In the traditional framework, the individual consents to surrender certain personal liberties in exchange for protection and governance by a sovereign entity. 
    
    However, crucially, the individual is excluded from participating in the actual decision-making process. This game will allow us to test the implicit assumption that everyone naturally agrees to such a deal.


    After reflecting on this classical model, we will expand the scope to consider a larger, more inclusive modern social contract. Here, we pose a fundamental question:

    ### Does consent to live in society simply mean coexisting, or does it imply deeper responsibilities toward others?

    """
    st.divider()

    st.markdown("# <center>On Consent (a Game)</center>", unsafe_allow_html=True)
    
    """
    We choose to live in society because it offers us the benefits of cooperation and connection that we could not achieve in isolation.
    Living together lets us achieve what we can't on our own — sharing resources, knowledge, and building systems that elevate our lives from mere survival to thriving.
    """

    
    
    """
    ## A contract is an agreement, a story between two or more parties. 
    
    As an agreement, it is an understanding.
    When the understanding is shared, it becomes social.
    """
    """
    # But how _should_ a social contract work?
    """
    f"""
Let's take a foundational idea from the 17th century—one that still underpins much of Western and European governance—and put it to the test in today's world. 
It _assumes implicit consent_, meaning people agree without ever explicitly being asked. 
Starting today, {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}, _we challenge that assumption._    """
    """
Here is whre we _cut through_ and ask directly:  **Are you willing to relinquish some of your freedoms in exchange for the benefits of living in a society?** _In other words_, **Do you accept _that_ deal?** 

This is where _you_ come in, casting a real, meaningful preference—_yours_.

Our approach is explicit and participatory, aiming for informed, active consent. 
    Here, participants contribute directly to the construction of our bonds, 
    manifesting a real voice in determining their principles. 
    Stakeholders are real and governing structures are transparent.
    
### We would like clarity. Ready to make your voice count?

This makes _our consent_ both foundational and dynamic, allowing it to evolve as the contract itself grows and responds to new inputs and challenges. 
    
    """
    """
    By participating, you actively shape the foundations of _a new social contract_ experiment. Your consent isn't just a checkbox — 
    it's a voice in the construction of principles we live by.
    """

    """
### This is more than just a game, this is a collective discovery process.

"""
    
    """
    """

    """
    ## So how does _this foundational deal_ look?
    """
    """
    It assumes you respond _fully_ to the following question:
    """
    """
    # _How_ willing are you to give up your freedoms in exchange for protection and stability, relinquishing your participation in decisions that affect you?
    """
    
    
    """
    The deal is a "classic" social contract: the individual surrenders certain liberties in exchange for the protection and decision-making provided by a sovereign or governing entity. But, crucially, the individual doesn't get to participate in the decision-making process—they trust that the sovereign will act in their best interest.
    """
    
    """
    Here's a simple question which still allows for a nuanced response. 
    
    
    
    **Choose between** Not willing to give up freedom (0 given up/black), fully willing to give up freedom (1/white), and all values in between - the greys - representing conditional, small or large, willingness. We will gather detailed insights!
    
    At this clickable interface we arrive at a crossroads where you can choose...
    """
    question()
    
        
    response = fetch_data()
    response = extract_willingness_and_timestamp(response)
    # df = pd.DataFrame(response)
    
    def sum_data(A, B):
        summed_data = []
        for A_item in A:
            # Find corresponding item in result based on 'id'
            for B_item in B:
                if A_item['id'] == B_item['id']:
                    # Sum the 'value' fields
                    new_value = A_item['value'] + B_item['value']
                    summed_data.append({
                        "id": A_item["id"],
                        "label": A_item["label"],
                        "value": new_value
                    })
                    break
        return summed_data

    def map_willingness(data):
        full_willingness = len([i for i in data if i["willingness"] == "1"])
        zero_willingness = len([i for i in data if i["willingness"] == "0"])
        conditional_willingness = len([i for i in data if 0 < float(i["willingness"]) < 1])
        
        st.session_state["consents"] = full_willingness

        return [
            {"id": "Full Willingness", "label": "Full Willingness", "value": full_willingness},
            {"id": "Zero Willingness", "label": "Zero Willingness", "value": zero_willingness},
            {"id": "Conditional", "label": "Conditional", "value": conditional_willingness}
        ]

    # Apply the function to the data
    state = map_willingness(response)

    
    INITIAL_CONDITION = [
  {
    "id": "Full Willingness",
    "label": "Full Willingness",
    "value": 0
  },
  {
    "id": "Zero Willingness",
    "label": "Zero Willingness",
    "value": 4
  },
  {
    "id": "Conditional",
    "label": "Conditional",
    "value": 6
  }
]
    DATA = sum_data(state, INITIAL_CONDITION)
    
    """
    ## The results
    """
    
    """
    Here's some partial data from this living _consent_ survey. Our target is to fill the box with responses from 100 participants.
    """
    
    with elements("nivo_charts"):

        with mui.Box(sx={"height": 600}):
            nivo.Waffle(
                borderRadius=3,
                data=DATA,
                total=100,
                rows=8,
                columns=10,
                # borderWidth=1,
                emptyOpacity=0.15,
                padding=3,
                colors={'scheme': 'accent'},
                legends=[
                    {
                        "anchor": "top",
                        "direction": "row",
                        "justify": False,
                        "translateX": 0,
                        "translateY": 0,
                        "itemsSpacing": 0,
                        "itemWidth": 200,
                        "itemHeight": 18,
                        "itemDirection": "left-to-right",
                        "itemOpacity": 0.85,
                        "itemTextColor": "#777",
                        "symbolSize": 24,
                    }
                ]
            )

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    """
    # HERE GOES THE REVIEW
    """
    
    """
    
    ### What commitments are we making to each other and to the broader community?

    This shift invites us to reconsider the nature of consent and action, encouraging us to think critically about the responsibilities and commitments that form the foundation of a truly inclusive and participatory social contract.
    
    In common usage, a commitment is a declaration of intent—a promise or obligation for the future, an agreement to act or uphold certain values. In programming, however, a commit refers to a definitive action where changes to a project are finalized and recorded. This dual meaning can guide us in thinking about commitments in the context of the social contract: both as a future-oriented promise and as a recorded action, solidified within a community structure.
    
    ## What kind of relationships we wish to foster among ourselves?
    
    These relationships can exist on a continuum, spanning from bare coexistence—where individuals live alongside one another with minimal interaction or mutual influence—to a state of interdependent responsibility, where we actively engage in each other's well-being, decisions, and the health of our shared environments.
    
    """    
    
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
        "description": "Individuals avoid actions that could harm or disrupt others' lives, but without actively engaging or supporting one another."
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
        "subtitle": "Mutual reliance for a better present & future",
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

    dicho = my_create_dichotomy(key = "relations", id= "relations",
                        kwargs={'survey': survey,
                            'label': 'spectrum_relations', 
                            'question': 'What kind of society do we are creating?',
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
    # HERE GOES THE VISUALISATION
    """
    
    """
    
    
    
## New forms of collaboration and systems of transparency.

Do we need transparency?
_Yes!_, transparency is essential, not just as a buzzword, but as the foundation effective collaboration in any collective system. When interactions span physical and digital spaces, and decisions often affect a vast range of people, transparency becomes the glue that holds together our social fabric.

    """
    survey.text_area("Why is Transparency Crucial, in your view?", id="transparency", placeholder="Share your thoughts on the importance of transparency in collective systems.")

# 1.	Building Trust: Transparency creates an environment where individuals and groups can trust the system and each other. When actions, decisions, and processes are made visible, it removes the shadow of doubt and suspicion. People are more willing to collaborate, share resources, and engage when they know what is happening and why.
# 2.	Accountability: With transparency, decision-makers are held accountable for their actions. Whether it's a government, corporation, or community leader, knowing that their choices are visible encourages them to act responsibly, ethically, and in the interest of the broader group. It prevents hidden agendas, misuse of power, and corruption.
# 3.	Empowerment Through Knowledge: Transparency provides access to information, which in turn empowers people. When people understand how systems work, what decisions are being made, and why resources are allocated in certain ways, they can participate more meaningfully. This also promotes equity—ensuring that everyone, regardless of background, has the opportunity to engage and contribute.
# 4.	Collaboration and Innovation: When processes are open and clear, it encourages collaboration. New ideas and innovations are more likely to emerge when everyone has access to the same information. Transparency fosters an environment where knowledge and insights are shared freely, allowing for cross-pollination of ideas and creative problem-solving.

    """
How Can We Implement Effective Transparency?

1.	**Open Decision-Making:** Decisions, especially those affecting large groups, should be made in an open forum or through participatory mechanisms. This allows for the inclusion of diverse voices and ensures that the rationale behind decisions is clear and understood.
    """
    
    survey.radio("How do you feel about Open Decision-Making?", id="open_decision_making", options=["I agree", "I disagree", "I go with the flow"], index=2)
    """
2.	**Clear and Accessible Communication:** Transparency isn't just about making information available, it's about making it accessible and understandable to everyone involved. Whether it's through open-source technology, clear reporting systems, or regular updates, people should be able to easily access and interpret the information they need.
"""
    survey.radio("How do you feel about Clear and Accessible Communication?", id="clear_communication", options=["I agree", "I disagree", "I go with the flow"], index=2)
    """
3.	**Collaborative Technologies**: Leveraging technology can enhance transparency. Blockchain, for example, provides immutable and transparent ledgers for financial transactions and contracts. Collaborative platforms allow for real-time tracking of project progress and decision-making, ensuring everyone stays informed and engaged.
    """
    survey.radio("How do you feel about Collaborative Technologies?", id="collaborative_technologies", options=["I agree", "I disagree", "I go with the flow"], index=2)
    """
4.	**Feedback Loops**: Transparency should also be a two-way street. It's not just about providing information but also creating feedback mechanisms where individuals can voice concerns, offer suggestions, or hold decision-makers accountable. These loops ensure that transparency is dynamic and responsive to the community's needs.

## New Forms of Collaboration

Transparency is the cornerstone of our collaborative systems.
    """
    
    with st.expander("Review your responses"):
        st.json(survey.data)
    
    st.session_state['serialised_data'] = survey.data
    
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
    # After sharing ideas, stretching
thoughtful discussions, and engaging a deeper understanding of each other's perspectives, _time_  moves _us_ forward. 

Now, we shift from dialogue to action. To take our collaboration to the next level, we can focus on just one dimension of the many possibilities: time. Together, we will co-create a shared timeline, where each contribution will shape our collective future. **This open agenda will serve** as a living map, adapting to the flow of events, ideas, and actions _as they unfold_.

Let's sketch out a collaborative, flexible timeline—an open space where each step we take can be recorded, discussed, and adjusted. This is our opportunity to organize, plan, and visualize the actions that will drive change. 

Your input shapes this evolving story.

    """
    

    timeline(timeline_data, height=800)
    


    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
