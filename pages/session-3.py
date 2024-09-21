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

    st.markdown("# <center>Relations, Systems & Healing</center>", unsafe_allow_html=True)

    st.markdown("## <center>Governance and decision-making.</center>", unsafe_allow_html=True)

    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')} - Session 3", unsafe_allow_html=True)

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

def question_trust():
    inverse_choice = lambda x: x
    name = 'there'
    # Dictionary containing trust levels and their nuanced descriptions
    trust_levels = {
        0.0: {
            "title": "Zero Trust",
            "subtitle": "Complete distrust",
            "description": "I do not believe the financial system is fair, reliable, or trustworthy. I expect corruption, manipulation, or collapse at every level."
        },
        0.1: {
            "title": "Extremely Low Trust",
            "subtitle": "Skeptical and deeply distrustful",
            "description": "I have serious doubts about the system's integrity and suspect that it primarily serves the interests of a few at the expense of many."
        },
        0.2: {
            "title": "Very Low Trust",
            "subtitle": "Barely any trust",
            "description": "I perceive the system as fundamentally flawed but acknowledge that it might work in certain situations, although rarely in my favor."
        },
        0.3: {
            "title": "Low Trust",
            "subtitle": "Cautious and wary",
            "description": "While acknowledging some potential benefits of the system, I remain highly cautious. I believe that the risks outweigh any possible advantages."
        },
        0.4: {
            "title": "Hesitant Trust",
            "subtitle": "Reluctant to trust",
            "description": "I am hesitant to engage with the financial system unless necessary, often choosing alternatives or self-reliance. Trust is reserved and given only reluctantly."
        },
        0.5: {
            "title": "Neutral",
            "subtitle": "A balance of skepticism and hope",
            "description": "My trust in the system is neither high nor low. I see both its potential and its flaws and are willing to engage, but I remain watchful for any signs of manipulation or inefficiency."
        },
        0.6: {
            "title": "Moderate Trust",
            "subtitle": "Leaning towards trust",
            "description": "I believe the system can be beneficial in certain contexts, but I maintain some skepticism. I see the potential for positive outcomes but remain cautious."
        },
        0.7: {
            "title": "Considerable Trust",
            "subtitle": "Generally trusting",
            "description": "I trust the system to work in my favor most of the time. Though I am aware of its imperfections, I believe it generally functions as intended."
        },
        0.8: {
            "title": "Strong Trust",
            "subtitle": "Confident in the system",
            "description": "I have strong confidence that the financial system operates fairly and transparently. I expect it to provide stability and security in most cases."
        },
        0.9: {
            "title": "Very Strong Trust",
            "subtitle": "Almost complete trust",
            "description": "I believe that the system is reliable and dependable, providing fairness and opportunity. I engage with it confidently, trusting it to work as intended."
        },
        1.0: {
            "title": "Full Trust",
            "subtitle": "Complete and unwavering trust",
            "description": "I have absolute faith in the financial system's integrity, believing it to be just, stable, and efficient in all aspects. I have no reservations about its function."
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
                            'messages': ["", "", ""],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )
            
    # st.markdown(f'## {inverse_choice(float(dicho))}')
    if dicho is not None:
        _display_nuance(inverse_choice(float(dicho)))
    
  
  
if __name__ == "__main__":
    
    intro()

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")

    authentifier()

    """
    
At the core of any effective social contract lies the essential question of governance and decision-making. If we agree to ground our social contract in mutual respect and cooperation, we must ask: What processes and mechanisms do we want to establish to ensure smooth governance, effective conflict resolution, and dispute settlement?

### How do we collectively make decisions? 
What is the governance process, as opposed to merely the structure of governance? Importantly, how do we pool and manage decisions that affect us all?

This line of inquiry naturally leads to the question of _trust_. Why do we trust one another to make sound decisions or judgments? Historically, we've relied on human empathy, shared experiences, and moral frameworks to guide decision-making. But as technology evolves, new questions arise: Can we trust automated systems—so-called artificial systems—to make decisions on our behalf? Can a judge be replaced by computer code?

As we delve into this session, we will explore the interplay between trust and governance, reflecting on whether we can—or should—trust machines in decision-making processes. How do we define and build trust in systems, whether human or artificial, and what implications does this have for the future of governance within the social contract?
    
    """
    
    
    
    st.markdown(f"# <center>Start With Trust</center> ", unsafe_allow_html=True)
    st.markdown("## <center>Not A Simple Yes/No $\mathcal Q$uestion</center>", unsafe_allow_html=True)

    st.write("Click the link below to authorise this. Your authorisation is key to proceed. If everything is in order, you will read above a message of success, or a unique ID below.")
    
    if st.button("It is OK to bring money into the game", type='primary', key="authorise", use_container_width=True, disabled=not bool(st.session_state['authentication_status'])):
        st.info("We are authorised to proceed.")
    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")

    # Sample page for "Game 1: Financial Trust Game"
    st.markdown("# Part I: Can financial institutions be trusted?")
    st.markdown("### Introduction")
    st.markdown("The Financial Trust Game simulates the balance of trust and risk in power relations, "
                "mirroring real-world interactions between individuals,  the public, and corporations.")
    st.markdown("### Context")
    
    """
    In the urgency of now and the broader global conversation, we are living in a moment of profound uncertainty, where the financial systems that once were believed solid are now being called into question. _May they crack?_ The world is facing stark inequalities, environmental degradation, and global migration as well as health crises. 
    
    During a recent meeting at UNESCO headquarters in Paris$^1$, in a conversation addressing migration, social inequalities, and systemic crises, the Chair issued a compelling challenge: _"It is time to challenge financial institutions."_
    
    ### Do you trust the current financial institutions?
    
    This game is not just about individual responses but about collective sentiment. 
    We can no longer passively accept the status quo. The structures that govern our economies, dictate investment policies, and manage global crises need to be scrutinised. 
    
    The Game gives us the space to confront these issues directly and, practically, using new models of _trust_ and governance. Whether we continue to rely on the existing systems or take the first steps toward creating something new is up to us.
    
    """
    # to deliver a fair and equitable future? 
    
    st.markdown("### Question")
    
    # st.write("How would you behave as an individual investor or the Trustee in this scenario? What factors would influence your decision?")
    
    """
    # _How_ you trust the Financial System?
    """
    
    question_trust()
    
    """
    # HERE GOES VIS
    
    """
    
    st.divider()
    
    
    """
    # A Game, Revisited
    
    """
    
    """
    The pervasive influence and power that financial institutions, particularly banks, wield in shaping not only the economy but the very trajectory of companies, industries, and even global issues like climate change, makes them non-neutral actors.
    
    Their need is centralised, consolidated information on companies to extend their control, ensuring that they are not only investors but active overseers of the _health_ and _direction_ of businesses.
    
    Banks _have been_ key players in the long-term investment game, making decisions that have influenced not only the present-day state but also future projections.
    """
    
    """
    ### Case in Point:
A major financial group boldly claims its commitment to climate action. But is this a genuine promise or just a marketing tactic? They say: _climate change is the
greatest challenge facing us all this century. Its economic, social and environmental consequences
require action in which everyone, *** included, has a role to play. *** has been playing this role for many years, notably by applying strict control_ - as it goes...


To find out, we'll revisit a classic trust game, testing not only their words but the real actions backing up these claims. 

### _Can you guess who is ***, the corporation is under scrutiny?_

    """
    from streamlit_pills import pills
    
    financial_groups_info = {
    "Goldman Sachs": {
        "description": "Known for global financial influence, claims sustainability leadership but faces scrutiny for actual impact.",
        "icon": "💼"
    },
    "JPMorgan Chase": {
        "description": "Largest bank in the U.S., criticised for major fossil fuel investments despite climate goals.",
        "icon": "🏦"
    },
    "HSBC": {
        "description": "Prominent in sustainable finance, but funding environmentally harmful projects raises questions.",
        "icon": "🌱"
    },
    "Barclays": {
        "description": "Pledged net-zero emissions, but ongoing support for oil and gas sectors sparks concerns.",
        "icon": "💳"
    },
    "Deutsche Bank": {
        "description": "Supporter of low-carbon economy transition, yet its record on climate action is mixed.",
        "icon": "💶"
    },
    "Citigroup": {
        "description": "Bold climate goals, but significant fossil fuel investments undermine credibility.",
        "icon": "🌍"
    },
    "Bank of America": {
        "description": "Ambitious environmental targets, but questions remain about its real progress.",
        "icon": "🇺🇸"
    },
    "Wells Fargo": {
        "description": "Involved in climate pledges, yet still heavily invested in environmentally harmful industries.",
        "icon": "🏇"
    },
    "Credit Suisse": {
        "description": "Promotes green finance, yet criticized for financing destructive environmental projects.",
        "icon": "📈"
    },
    "Morgan Stanley": {
        "description": "Pledged net-zero by 2050, but continues to invest in fossil fuels despite climate goals.",
        "icon": "📊"
    }
}
    # get the list of financial groups
    financial_groups = list(financial_groups_info.keys())
    # get the icons for each financial group
    icons = [financial_groups_info[group]["icon"] for group in financial_groups]
    
    selected_value = pills("Select values", financial_groups, icons, clearable=True, index=None)
    if selected_value:
        st.markdown("### " + selected_value)
        st.markdown(financial_groups_info.get(selected_value).get("description"))
        st.markdown("Link to Social Responsibility Statement: [Link](https://www.google.com)")
    
    
    
    """
    # HERE GOES VIS
    
    """
    
    
    
    
    st.divider()

    """
    # PART II: Collective Decision-Making and Automation
    """
    
    """
    AI systems are increasingly being framed as moral agents, designed to align with human values. These large language models (LLMs), trained on vast amounts of scraped data and fine-tuned by Silicon Valley engineers, bring with them a biased worldview. As we step into the democratic arena, how do we address the inherent biases they carry?

### It's not merely a question of capacity, 
where cost functions are key metrics matter. Governance is a societal issue — how do we find true alignment and avoid apocalyptic scenarios driven by tech elites?

For this event, we've developed transparent, open interfaces from scratch, shared as _Free software_. Unlike platforms from tech giants, which come at a cost, our approach is built on openness. The question is, does everyone need to learn to code, or should we focus on more open, collaborative efforts to shape the tools that govern our interactions?

"""
    """
    # HERE GOES THE REVIEW
    """
    
    """
    As we shape our social contract, it's essential to test how our governance models function in real-world scenarios. Two practical cases will help us evaluate and refine these models:

1.	**Deciding the Outputs of the Workshop**: Together, we will determine the conclusions, next steps, and key takeaways, ensuring every voice is heard and consensus is reached.
2.	**Next Event**: We'll use our governance processes to collectively organise and structure future events, highlighting how decisions can be made inclusively and efficiently.

By testing these models, we explore how collective decision-making and governance within the social contract can translate to practical outcomes, allowing us to collaboratively create sustainable, transparent processes for the future.
"""
    
    
    equaliser_data = [
            ("Curated Publication", ""),
            ("...", ""),
            ("Working groups", ""),
            ("Policy proposals", ""),
            ("Games", ""),
            ("Observatory of Perceptions", ""),
            ]

    create_equaliser(key = "equaliser", id= "equaliser", kwargs={"survey": survey, "data": equaliser_data})

    """
    ## Where is your current base or location? 
    #### For events and remote workshops that are accessible to you.

    """
    survey.text_input("This will help us coordinate", id="location")
    
    import random
    
    cities = [
    {"name": "New York", "lat": 40.7128, "lng": -74.0060, "size": random.random()},
    {"name": "London", "lat": 51.5099, "lng": -0.1180, "size": random.random()},
    {"name": "Paris", "lat": 48.8566, "lng": 2.3522, "size": random.random()},
]    
    cities = [
    {"name": "New York", "lat": 40.7128, "lng": -74.0060,
        "maxR": random.random()*20+3,
        "propagationSpeed": (random.random()-.5)*20+1,
        "repeatPeriod": random.random() * 2000 + 200,
        "size": random.random()},
    {"name": "London",
        "lat": 51.5099,
        "lng": -0.1180,
        "maxR": random.random()*20+3,
        "propagationSpeed": (random.random()-.5)*20+1,
        "repeatPeriod": random.random() * 2000 + 200,
        "size": random.random()},
    {"name": "Paris",
        "lat": 48.8566,
        "lng": 2.3522,
        "maxR": random.random()*20+3,
        "propagationSpeed": (random.random()-.5)*20+1,
        "repeatPeriod": random.random() * 2000 + 200, "size": random.random()},
]
    # Generate JavaScript code with city data
    javascript_code = f"""
    // Gen city data
    const cityData = { cities };
    const N = 10;

    console.log(cityData);

    const map = Globe()
    (document.getElementById('globeViz'))
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .pointsData(cityData)
    .backgroundColor('rgb(255, 255, 255)')
    .pointAltitude('size')

    // Add auto-rotation
    map.controls().autoRotate = true;
    map.controls().autoRotateSpeed = 1.6;
    """

    javascript_code = f"""
    import * as THREE from '//unpkg.com/three/build/three.module.js';
    const VELOCITY = 2; // minutes per frame

    const sunPosAt = dt => {{
      const day = new Date(+dt).setUTCHours(0, 0, 0, 0);
      const t = solar.century(dt);
      const longitude = (day - dt) / 864e5 * 360 - 180;
      return [longitude - solar.equationOfTime(t) / 4, solar.declination(t)];
    }};

    let dt = +new Date();
    const solarTile = {{ pos: sunPosAt(dt) }};
    const timeEl = document.getElementById('time');


    // Gen city data
    const cityData = { cities };
    const N = 10;

    console.log(cityData);

    const map = Globe()
    (document.getElementById('globeViz'))
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .ringsData(cityData)
    .ringMaxRadius('maxR')
    .ringPropagationSpeed('propagationSpeed')
    .ringRepeatPeriod('repeatPeriod')
    .backgroundColor('rgb(255, 255, 255)')
      .tilesData([solarTile])
      .tileLng(d => d.pos[0])
      .tileLat(d => d.pos[1])
      .tileAltitude(0.01)
      .tileWidth(180)
      .tileHeight(180)
    .tileMaterial(() => new THREE.MeshLambertMaterial({{ color: '#ffff00', opacity: 0.3, transparent: true }}))
      .tilesTransitionDuration(0);

    // animate time of day
    requestAnimationFrame(() =>
      (function animate() {{
        dt += VELOCITY * 60 * 1000;
        solarTile.pos = sunPosAt(dt);
        map.tilesData([solarTile]);
        timeEl.textContent = new Date(dt).toLocaleString();
        requestAnimationFrame(animate);
      }})()
    );

    // Add auto-rotation
    map.controls().autoRotate = true;
    map.controls().autoRotateSpeed = 4.6;
    """

    # HTML code with embedded JavaScript
    html_code = f"""
    <head>
    <style> body {{ margin: 0em; }} </style>
    <script src="//unpkg.com/globe.gl"></script>
    <script src="//unpkg.com/three"></script>
    <script src="//unpkg.com/solar-calculator"></script>
    </head>

    <body>
    <div id="globeViz"></div>
    <div id="time"></div>
    
    <script type="module">
        { javascript_code }
    </script>
    </body>
    """
    col1, col2 = st.columns(2)
    with col1:
        st.components.v1.html(html_code, height=700, width=700)

    
    
    
    
    
    
    
    st.divider()
    
    """
    
We are framing the beginning of a shared journey, leaving space for future collaboration and deeper exploration. 

Many topics still require our attention, and the journey is far from over. As we move forward to organising either a gastronomic event - one that is metaphor for spiritual nourishment, or a new workshop — one that centers on gathering your feedback, insights, and renewed motivation.
    
# For our next event, 
### would you prefer a hands-on workshop or a gastronomic experience?
_or reading-discussion-to-creation-action, dance, theatre play, music, movie/documentary, brainstorming) and curated publications.XXX_
    


What lies ahead will take us deeper into pressing issues: from understanding and resolving conflicts to navigating the technical complexities that underpin them. The challenge remains, and with your continued participation, we can shape a collective vision for solutions.

    
**A philosophical dinner** is more than just a meal—it's an ART space where deep conversations and critical thinking are nourished alongside the food. Bringing together minds from diverse backgrounds, the dinner encourages reflection and sharing of experience, exploring ethics and existence as well as society and art. In this setting, the act of eating becomes a metaphor for intellectual nourishment, where ideas are embodied on a table, shared, challenged, and expanded upon in a relaxed, communal environment. 

The philosophical dinner fosters connection, dialogue, and introspection, allowing participants to explore abstract concepts in a tangible way, guided by both the flow of conversation and the flavors of the evening.
    
    """
            
    my_create_dichotomy(key = "event", id= "event",
                        kwargs={'survey': survey,
                            'label': 'future_event', 
                            'question': 'Click to express your viewpoint.',
                            'gradientWidth': 10,
                            'height': 250,
                            'title': '',
                            'name': 'intuition',
                            'messages': ["*Workshop*", "*Philo Dinner* bright and positive", 
                                         "*Work•Dinner* gray like an uncertain mix"],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )
    
        
    """
    # HERE GOES THE VISUALISATION
    """

    """
    what does it mean and what have you brought to the table? 
    """


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

    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
