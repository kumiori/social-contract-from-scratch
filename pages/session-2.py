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

    st.markdown("# <center>Structure and Participation</center>", unsafe_allow_html=True)

    st.markdown("## <center>Turning a social contract on its head.</center>", unsafe_allow_html=True)

    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')} - Session 2", unsafe_allow_html=True)

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

# def question(): 
#     name = 'there'
#     dicho = my_create_dichotomy(key = "executive", id= "executive",
#                         kwargs={'survey': survey,
#                             'label': 'future_outlook', 
#                             'question': 'Do we exclude? (White: Yes, Black: No, Nuances: We exclude for other reasons)',
#                             'gradientWidth': 20,
#                             'height': 250,
#                             'title': '',
#                             'name': f'{name}',
#                             'messages': ["*Zero,* black!", 
#                                          "*One*. White", 
#                                          "*between* gray"],
#                             # 'inverse_choice': inverse_choice,
#                             'callback': lambda x: ''
#                             }
#                         )
            
#     my_create_dichotomy(key = "outlook", id= "outlook",
#                         kwargs={'survey': survey,
#                             'label': 'future_outlook', 
#                             'question': 'Click to express your viewpoint.',
#                             'gradientWidth': 30,
#                             'height': 250,
#                             'title': '',
#                             'name': 'intuition',
#                             'messages': ["*The future looks* dark like an impending storm", "*The future looks* bright and positive", "*The future looks* gray like an uncertain mix"],
#                             # 'inverse_choice': inverse_choice,
#                             'callback': lambda x: ''
#                             }
#                         )

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
                    'session_2_structure_participation': json.dumps(serialised_data),
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


if __name__ == "__main__":
    
    intro()

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")

    authentifier()

    """
    
    How do different parties share understanding and tools for communication?

## Who is in the Social Contract?
 
 Think of the participants of the democratic process in ancient Greece, particularly in the city-state of Athens. While Athenian democracy is hailed as the birthplace of democracy, its scope of participation was limited to a relatively small portion of the population.

Only free adult men who were citizens of Athens could participate in the democratic process.

The Athenian democracy was a direct democracy, meaning eligible citizens participated in making laws and important decisions. 
Unlike modern representative democracies, where citizens elect officials to make decisions on their behalf, Athenian _themselves_ voted on every important issue.

Nowadays, the social contract has been a pact between the individual and the state in exchange for protection (of property, order, etc.).
    
Tomorrow, the Social Contract is an agreement that fulfills needs, and maybe instead of citizens we will feel like _planetizens_$^1$.

____

Remarks and References: 
•	Citizenship was inherited, meaning you needed to be born to Athenian parents to qualify.
•	These citizens had the right to vote, hold office, and participate in the Ekklesia (the assembly) and other democratic institutions like the Boule (the council).
$^1$: Learning Planetizen Manifesto, https://www.learning-planet.org/learning-planetizen-manifesto/
 
    """
    
    
    st.markdown(f"# <center>Who are the Parties?</center> ", unsafe_allow_html=True)


    """
    
    ### Should we exclude individuals from the Social Contract based on specific criteria, such as age, gender, nationality, or lineage?
    
    
    For example, allowing only women aged 15 and above, only French citizens, only people born in a certain place, or only individuals descended from a particular group.
    

    Think of your experience, have individuals been excluded from participating in or benefiting from _the goods of society_ due to specific criteria, such as race, gender, nationality, social class, or other _non_-defining factors?
    
    Should such exclusion mechanisms be part of the Social Contract?
    
    """
    dicho = my_create_dichotomy(key = "exclude", id= "exclude",
                        kwargs={'survey': survey,
                            'label': 'exclude_criteria', 
                            'question': 'Do we exclude based on criteria? (White: Yes, Black: No, Nuances: We exclude for other reasons)',
                            'gradientWidth': 20,
                            'height': 250,
                            'title': '',
                            'name': f'humanity',
                            'messages': ["*Nope,* we don't exclude", 
                                         "*Yes*. We exclude based on external criteria", 
                                         "*maybe* we exclude for other reasons"],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )

    """
    # What is a Strategic Choice?
    
    """
    """
    
    An alternative to an exclusionary approach is an inclusive approach, where broader criteria can be envisioned. This is where reasoning by abstraction becomes essential, allowing us to picture a wide perspective on the entire ecosystem of relations.
    
    """
    
    strategy = survey.radio("What is a _strategic_ choice?", options=["Inclusion", "Exclusion", "I don't know"], index = 2)
    
    if strategy == "Inclusion":
        """
        Sounds like a good idea. Let's explore some criteria for inclusion.
        """
        quanti_3 = create_quantitative("inclusive_criteria", 
                                    kwargs={"survey": survey, 
                                            "label": "inclusive_criteria", 
                                            'name': 'Hello,',
                                            "question": 'What do you include in your consideration for the Social Contract?',
                                            "key": "inclusive_criteria", 
                                            "data_values": [0, 10, 30, 50]})
        
        
        inclusion_categories= {'0': 'All natural elements', 
                            #    '1': 'All sentient beings', 
                            '2': 'Animals', 
                            '10': 'All animals, plants, mushrooms, and bacteria', '30': 'All humans', '50': 'All of us'}
        
        feedback_messages = {
            '0': f"## I include **`{inclusion_categories['0']}`** this initiative. \n ### _Thank you,_ .",
            # '1': f"## I include **`{inclusion_categories['1']}`** this initiative. \n ### _Thank you,_ .",
            '10': f"## I include **`{inclusion_categories['10']}`** in a shared vision. \n ### _Thank you,_ .",
            '30': f"## I include **`{inclusion_categories['30']}`** to our cause. \n ### _Thank you,_.",
            '50': f"## I include **`{inclusion_categories['50']}`** to our cause. \n ### _Thank you,_."
        }
        
        st.markdown(feedback_messages.get(quanti_3, ''))
    
    elif strategy == "Exclusion":
        exclusion_categories = survey.text_area("We are happy to hear. What are criteria for exclusion?", id="exclude_criteria_ext")
    else:
        st.warning("Strategy is key. Make a choice to proceed.")
    
    """
    ### Fair for Humans, but Beneath and Beyond?
    """
    """
    This is a wild ask (but we are the _Athena_ Collective). Some cultures give symbolic representation to natural elements—ghosts, spirits, gods.
    How can we integrate these symbolic elements into the social contract?

    """
    societal_issues = survey.text_area("Share your thoughts:", placeholder="E.g., inequality, climate change, governance...", key="symbolic_elements")





    st.divider()
    st.markdown("# Perceptions: Subjective Points of View, an Observatory")
    st.markdown("Does perception shape reality? This observatory platform captures subjective points of view, providing a space where different perspectives on social, political, and economic issues are shared.")
    
    """
    As we shape the boundaries of the Social Contract, we recognise that any collective agreement first begins with an understanding of individual perspectives. 
    
    By exploring each person's beliefs, values, and interactions, we gain insight into how they relate to their community and the broader world. 
    
    This series of questions is designed to gradually expand from personal perception to interpersonal, societal, and global outlooks, allowing us to reveal how we view our role within the ecosystem of relations. 
    
    Through this process, we aim to construct an inclusive Social Contract that reflects both the diversity of human experience and the shared responsibilities we hold.
    """
      
    """
    
    # What is your outlook of the future?
    
    """

    my_create_dichotomy(key = "future", id= "future",
                        kwargs={'survey': survey,
                            'label': 'future_outlook', 
                            'question': 'Click to express your viewpoint.',
                            'gradientWidth': 30,
                            'height': 250,
                            'title': '',
                            'name': 'intuition',
                            'messages': ["*The future looks* dark like an impending storm", "*The future looks* bright and positive", "*The future looks* gray like an uncertain mix"],
                            'callback': lambda x: ''
                            }
                        )



    """
    
    # Do you envision social transitions, fast or slow?
    
    """

    my_create_dichotomy(key = "transitions", id= "executive",
                        kwargs={'survey': survey,
                            'label': 'transition_rate', 
                            'question': 'Click to express your viewpoint.',
                            'gradientWidth': 10,
                            'height': 250,
                            'title': '',
                            'name': 'intuition',
                            'messages': ["*Fast transition* rapid and transformative", "*Slow* gradual and long", "*A mix of the two* with the implications of both"],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )


    """
    # HERE GOES THE VISUALISATION
    """

    # """
    # # Do you trust your neighbour?
    # """

    # """
    
    # # Do you enjoy collaborative work?
    
    # """
    """
    
    # How do you prefer to engage with us?
    
    """
    options = ['Read', 'Write', 'Speak', 'Listen', 'Watch', 'Play', 'Give', 'Take']

    # Create the multiselect widget
    selected_options = st.multiselect('I would like to:', options)
    survey.data['preferred_mode'] = selected_options

    """
    
    # What is your approach to conflict resolution?
    
    """
    
    from streamlit_pills_multiselect import pills as multiselect_pills
    
    conflict_resolution_elements_split = {
        "Dialogue": "Prioritizing open discussions.",
        "Communication": "Ensuring honest communication between parties.",
        "Empathy": "Putting yourself in others' shoes to find common ground.",
        "Understanding": "Striving to comprehend different perspectives and experiences.",
        "Compromise": "Willingness to meet halfway to resolve issues.",
        "Flexibility": "Being open to adjusting one’s position to reach an agreement.",
        "Patience": "Allowing time for emotions to cool and for reflection.",
        "Time": "Recognizing that conflict resolution may take time.",
        "Authority": "Resolving conflicts through established rules or authority figures.",
        "Structure": "Creating frameworks or systems to ensure orderly conflict resolution.",
        "Innovation": "Thinking outside the box to come up with novel solutions.",
        "Creativity": "Using imaginative approaches to overcome obstacles.",
        "Collaboration": "Working together to find solutions.",
        "Teamwork": "Collectively solving problems as a group.",
        "Mediation": "Involving a neutral mediator to assist in resolving the conflict.",
        "Third-Party Intervention": "Bringing in an external party to facilitate a resolution.",
        "Transparency": "Being open about intentions and issues to foster trust.",
        "Honesty": "Maintaining truthful communication throughout the process.",
        "Respect": "Treating all parties with consideration and care.",
        "Dignity": "Ensuring that all participants maintain a sense of worth and integrity.",
        "Violence": "Resorting to physical force to impose a solution.",
        "Exploitation": "Taking advantage of weaker parties for personal gain.",
        "Power Imbalance": "Using unequal power to dominate or oppress one side.",
        "Coercion": "Forcing a resolution through fear or threats.",
        "Threats": "Intimidating others into submission.",
        "Deception": "Using lies or manipulation to win at the expense of truth.",
        "Escalation": "Allowing the conflict to intensify rather than seeking resolution.",
        "Avoidance": "Refusing to address the conflict and letting it fester.",
        "Denial": "Ignoring the existence or severity of the conflict.",
        "Blame-Shifting": "Avoiding responsibility and placing all blame on others.",
        "Sabotage": "Deliberately undermining efforts to resolve the conflict.",
        "Suppression": "Silencing dissent or ignoring the needs of one party."
    }
    
    selected_ingredients = multiselect_pills("Conflict Resolution Elements",
                      list(conflict_resolution_elements_split.keys()), key="conflict_resolution_elements", multiselect=True, 
                      clearable=True, index=None)

    if selected_ingredients:
        st.markdown("### " + selected_ingredients[-1]+ "💭")
        # ✨
        st.info("📣 " + conflict_resolution_elements_split.get(selected_ingredients[-1], ''))
    
    survey.data['conflict_resolution_elements'] = selected_ingredients
    
    # clear the multiselect
    # st.button("Clear", on_click=lambda: st.session_state.pop("conflict_resolution_elements", None))
    
    """
    
    # Are we progressing toward a fair deal?
    
    """
    from philoui.io import create_yesno_row
    
    create_yesno_row("demo_yesno_row", kwargs={"survey": survey})
    
    """
    
    # What are your thoughts on global cooperation?
    
    Two members of our collective argue that the need for cooperation has never been greater, and the equilibrium between cooperation, economic progress, and development is questioned by global challenges. 
    
    In a short article, they discuss cooperation as a historical product and explore triangular and polygonal cooperation schemes, following a trend from Japan. Furthermore, delving into the case where polygonal cooperation evolves into _circular_ cooperation, drawing a metaphorical connection and analogy to the dynamics of multi-body celestial systems, we aim to build a foundation for new models of direct collaboration.
    
    The article draft is available for review. Would you like to read it?
    
    """
    
    survey.button("I Wish To Read and Maybe Share Feedback", key="readpaper", help="", type='primary', use_container_width=True)
    
    """
    
    # How do you see your role in the ecosystem?
    
    """
    survey.text_area("Share your thoughts:", placeholder="Describe how you see yourself contributing to the balance and growth of the ecosystem. What actions, responsibilities, or roles do you take on in relation to the world and others around you?", key="ecosystem_role")

 

    st.divider()

    with st.expander("Review your answers"):
        st.json(survey.data)

    st.session_state['serialised_data'] = survey.data
    """
    The button below integrates the data into the bigger picture.
    
    """

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
    # HERE GOES THE ANSWER // WHAT DOES THIS MEAN // what do you mean for the sc?
    
    what does it mean for the world that we are driven by ...
    what does it mean that we are driven by ...
    what does somebody driven by do...
    """



    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()
