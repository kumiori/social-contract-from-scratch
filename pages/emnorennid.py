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
from streamlit_lottie import st_lottie

import pandas as pd
import philoui
import streamlit.components.v1 as components
import streamlit_shadcn_ui as ui
import yaml
from philoui.authentication_v2 import AuthenticateWithKey
from philoui.io import QuestionnaireDatabase as IODatabase
from philoui.io import conn, create_dichotomy, create_equaliser, create_qualitative, create_quantitative
from philoui.survey import CustomStreamlitSurvey
from philoui.texts import hash_text, stream_text, stream_once_then_write
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row
from streamlit_timeline import timeline
from yaml import SafeLoader
from streamlit_player import st_player
from streamlit_gtag import st_gtag
import gettext
import locale

from philoui.texts import stream_text


st_gtag(
    key="gtag_app_splash",
    id="G-Q55XHE2GJB",
    event_name="splash_main_page",
    params={
        "event_category": "apply_splash",
        "event_label": "test_splash",
        "value": 99,
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

if 'intro_done' not in st.session_state:
    st.session_state.intro_done = False


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
                    'remote_05': json.dumps(serialised_data)
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


def stream_function(text):
    import string
    
    # Define sleep lengths for different punctuation symbols
    sleep_lengths = {'.': 2.2, ',': 0.3, '!': 1.7, '?': 2.5, ';': 1.4, ':': .8}
    
    for i, word in enumerate(text.split()):
        # Check if the last character is a punctuation symbol
        last_char = word[-1] if word[-1] in string.punctuation else None

        # Yield the word or handle the line break
        if word == '|':
            yield " \n \n "  # Insert a line break (two new lines for readability)
        
        # Yield the word with appropriate sleep length
        if last_char == '.' or last_char == '?':
            yield word + " \n "
        else:
            yield word + " "
        
        # if word == '|':  # No sleep for line breaks
            # continue
                    
        if last_char and last_char in sleep_lengths:
            time.sleep(sleep_lengths[last_char])
        else:
            time.sleep(0.3)



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

def next_step():

    location = survey.text_input("Where are you connecting from?", id="location")

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
    
    # intro()
    st.markdown(f"# <center>Dinner on _me_?</center> ", unsafe_allow_html=True)

    # event_2 = st_player("https://vimeo.com/1007606689", key='vimeo_player_2')
    # name = survey.text_input("We may have already met", id="given-name")

    if st.session_state['intro_done'] is False:
        with st.spinner('Think about it...'):
            time.sleep(5)

        text = """"""
        
        # stream_once_then_write(text)

        frame = st.empty()

        abstract = ["""

Our entire emotional history 
.
plays itself out
.
in the physicality of eating.


Personal experiences knit in the present, reveal invisible bar- riers which disappear in the blink of an eye.


And the more we trust, the farther we are able to venture.
—
In this space, instead of the pulling from the past of our mem- ories, or pushing to the future of our fears, expectations, and struggles within a busy life, we have a chance to share and deeply sink on the same floating grounds, of the turning mo- ment
-now-
connecting to the present vibrant flow of everything that is energy.



Think again, think from the side (of the Food).
Food wants to know your hunger,
Food wants to meet you to release all tasty nutrients, Food wants to taste the delicate flavours of your cravings, and to see it as a match for her own.



Forget passivity, is irritating, and your considerateness is the opposite of the food’s fantasy of unrestrained rapture.
Your lustiness: an open endorsement for our long journey.


Our extravagant dinner is an experience of profound em- powerment and self-affirmation for the body and the soul.

We bring to an hedonistic dinner a lifetime of injunctions against selfishness, in the context of relationships:
I am here to share
...our behaviour and inclinations which encode the details of our personal journey.
Cultural legacies still weigh subconsciously, socialised to con- trol ourselves, to restrain impulses, to tame the animal within.
But why?
This entire emotional history plays itself out in the physicality of eating.

Suggestions for the senses, is what makes everything alive
a minimal setting dim light, some spots, otherwise smooth. Enticing food and deep grooves. Culinary experiments not confined to the tongue, it is surfing that all boundaries invite, from, to, and across your universe of vibes.

To declare the service finished there is only one thing to do. Served in a riddle, for you to reflect, the closure token is served, at the end of this text.



    """
        ]

        extra = ["""$^0$: This is a game, fill the blanks. https://social-contract-from-scratch.streamlit.app/game-1

    $^1$: https://www.weforum.org/agenda/2022/01/a-new-social-contract-for-21st-century/

    $^2$: From the General Debate, 72nd session, https://www.youtube.com/watch?v=t-oHFzwQAo0

    $^3$: https://www.un.org/sites/un2.un.org/files/sg_remarks_on_covid_and_inequality.pdf



    **What is a social contract, anyway?**  
    How do we build one that works, and changes for *everyone*, across time?

    **Your voice matters.**  
    **Be part of the conversation.**  
    **Help shape the future.**

    - Are we truly ready for a **renewed relationship** among people?
    - Will **leaders' summits** ensure a positive shift in human dynamics, or are they just more of the same?
    - How do we **close the loopholes** that fuel economic dependence and political decay?
    - Is the **international financial system** serving the welfare of the many—or the few?
    - Who shapes the **narratives and strategies** to handle the increasing complexity of our time?


    """]
        _sleep= 5
        with frame:
            abstract[0]
            # stream_once_then_write(abstract[0], stream_function=stream_function)
        # with st.spinner('Thinking about it...'):
            # time.sleep(_sleep)

        
        # frame.empty()

        # with frame:
        #     stream_once_then_write(abstract[1], stream_function=stream_function)
        #     # st.markdown(abstract[1])
        # with st.spinner('Think about it...'):
        #     time.sleep(_sleep)

        # frame.empty()

        # with frame:
        #     stream_once_then_write(abstract[2], stream_function=stream_function)        
        # with st.spinner('Do you feel it?'):
        #     time.sleep(_sleep)
        
        # frame.empty()
    
        # st.session_state['intro_done'] = True
    
    
    from philoui.texts import corrupt_string
    survey = CustomStreamlitSurvey()
    question = survey.text_input("Time to Question:", id="question")
    if st.button("Submit this task", key="submit_question", type='primary', use_container_width=True):
        st_lottie("https://lottie.host/91efca67-fa13-43db-8302-f5c182af8152/ufDyVWvWdR.json")
        # time.sleep(1)
        # st.write(corrupt_string(question, damage_parameter=0.1)[0])
        st.write_stream(stream_function('Did we understand well?'))
        st.write_stream(stream_function(corrupt_string(question, damage_parameter=0.1)[0]))
        st.info("We are trying to gather insight from your question. Thank you for sharing.")


### **We will be in Athens** |

    """Join us for a session where **you** are part of the conversation, shaping and reflecting, sharing and rethinking what governs our society. 
    This is **new** collective building experience is taking place during the **Europe in Discourse Conference IV** in Athens.

### Will you be in town or you prefer  remote access?

Whether you're in town or prefer to participate remotely, we've designed a seamless digital experience to ensure everyone can join the conversation. 

From wherever you are, your voice matters.
"""
# , and we invite you to contribute to this conversation, rethinking social structures and exploring radically new ideas./
    import random
    # """
    # # HERE GOES THE REVIEW
    # """

    # """
    # # HERE GOES THE INTEGRATION
    # """

    # """
    # # HERE GOES THE VISUALISATION
    # """
    
    # stream_once_then_write("### Would you like remote access?", stream_function=stream_function)        
    
    # Display the HTML code in Streamlit app
        
    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.session_state['read_texts'] = set()
        st.session_state['intro_done'] = False
        st.rerun()

    text = """
    ### Save this page in your bookmarks. Check here again the in a few days. We will have more for you.
    
    """
    
    st.write_stream(stream_function(text))
    
    
#     authentifier()
    
#     st.session_state['serialised_data'] = survey.data
#     """
#     The button below integrates the data into the bigger picture.
    
#     """
    
#     if st.button("Integrate the Bigger Picture", key="integrate", help="Integrate your data", 
#               disabled=not bool(st.session_state['authentication_status']), 
#               type='primary',
#               use_container_width=True,
#               on_click=lambda: _form_submit()):
#         """
#         Congratulations!

# Save this page in your bookmarks and check again in a few days. Otherwise, reach out to us by email. 

# social.from.scratch@proton.me

# How you feel about the results?"""
        
