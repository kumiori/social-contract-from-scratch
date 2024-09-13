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
from philoui.texts import hash_text, stream_text
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row
from streamlit_timeline import timeline
from yaml import SafeLoader
from streamlit_player import st_player
from streamlit_gtag import st_gtag

st_gtag(
    key="gtag_app_donation",
    id="G-Q55XHE2GJB",
    event_name="donation_main_page",
    params={
        "event_category": "apply_philantrhopy",
        "event_label": "test_donation",
        "value": 97,
    },
)

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
    
if 'donation' not in st.session_state:
    st.session_state.donation = 0


if 'profile' not in st.session_state:
    st.session_state.profile = None

if 'custom_donor' not in st.session_state:
    st.session_state.custom_donor = False

if 'checkouts' not in st.session_state:
    st.session_state.checkouts = []

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


# @st.dialog("Join the whitelist")
def join_waitlist():
    from email_validator import EmailNotValidError, validate_email
    st.markdown("**Welcome aboard**")
    st.markdown("""
We're excited that you are interested in joining our initiative. As we consolidate a focused and passionate community, your interest is a great step, and we'd love to learn more about you and your views. 

Joining the whitelist is our way of creating a supportive environment where individuals can collaborate and contribute meaningfully.
             """)
    email = st.text_input("Your email address")
    if email:
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            st.error(str(e))
        name = st.text_input("Your name")
        if name:
            st.write(f"Thank you `{name}` for your interest. We will get back to you by email.")
    st.write("Please check back here in a few days. We may have crafted your dashboard by then.") 

def get_checkout_info(checkout_id):
    url = f'{API_BASE_URL}/checkouts/{checkout_id}'

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    # Define the payload for the API request
    payload = {}

    # Make an HTTP POST request to the SumUp checkout endpoint
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful (status code 200)
    if response.status_code in [200, 201, 202, 204]:
        # Extract the checkout ID from the response
        checkout_id = response.json().get('id')
        st.success(f'Success! Commit info retrieved')
        
        return response.json()
    else:
        # Display an error message if the request failed
        st.write(response)
        st.warning(f'Error: {response.text}')
        return None

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

def stream_once_then_write(text):
    text_hash = hash_text(text)
    if text_hash not in st.session_state["read_texts"]:
        stream_text(text)
        st.session_state["read_texts"].add(text_hash)
    else:
        st.markdown(text)
        
def create_commit_checkout(reference, amount, description):
    # Define the SumUp checkout endpoint URL
    checkout_url = f'{API_BASE_URL}/checkouts'

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    # Define the payload for the API request
    payload = {
        'checkout_reference': reference,
        'amount': amount,
        'currency': 'EUR',
        'pay_to_email': 'social.from.scratch@proton.me',
        'description': description,
        'merchant_code': st.secrets["sumup"]["MERCHANT_ID"],

    }

    # Make an HTTP POST request to the SumUp checkout endpoint
    response = requests.post(checkout_url, headers=headers, json=payload)

    # Check if the request was successful (status code 200)
    if response.status_code in [200, 201, 202, 204]:
        # Extract the checkout ID from the response
        checkout_id = response.json().get('id')
        st.success(f'Success! Commit ID: {checkout_id}')
        st.session_state['checkouts'].append(checkout_id)
        
        return response.json()
    else:
        # Display an error message if the request failed
        st.write(response)
        st.warning(f'Error: {response.text}')
        return None

def checkout():
    st.markdown("## <center>Integrate your contribution</center>", unsafe_allow_html=True)

    st.warning("We are integrating _money_ into the game. This requires your authorisation.")

    from requests.exceptions import RequestException
    from sumup_oauthsession import OAuth2Session

    base_url = "https://api.sumup.com/"
    redirect_uri = "https://individual-choice.streamlit.app/"

    # st.markdown("## We connect to payment channels")
    # print authorisation status
    
    """
    Bringing money _into the game_ allows us to convert abstract ideas into concrete actions, facilitating the implementation of our first initiative: **hosting a panel discussion at the _Europe in Discourse_ Conference** in Athens.
    
    """
    st.write("Click the link below to authorise this. Your authorisation is key to proceed. If everything is in order, you will read a message of success and a unique ID, below. Isn't this cool?")
    if st.button("It is OK to bring money into the game", type='primary', key="authorise", use_container_width=True, disabled=False):
        try:
            sumup = OAuth2Session(
                base_url=base_url,
                client_id=st.secrets["sumup"]["CLIENT_ID"],
                client_secret=st.secrets["sumup"]["CLIENT_SECRET"],
                redirect_uri=redirect_uri,
            )

            st.markdown('Authorisation granted! #' + '`' + mask_string(sumup.state) + '`')
            st.session_state['sumup'] = sumup
        except RequestException as e:
            st.error(f"An error occurred during authorization: {e}")
        except KeyError as e:
            st.error(f"Missing configuration for {e}. Please check your secrets.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    """
    As soon as our payments channels open, we will be able to share our timeline.
    
    """
    # st.markdown("Click the expand button below to know more about the payment mechanics.")
    with st.expander("Payments and ledger, further details", expanded=False):
        st.write("This app uses the SumUp API (sumup.com) to create checkouts and process payments. We rely on CCF bank, a French commercial bank founded in 1894 and acquired by HSBC in 2000, as a piggy-bank.")
    
def checkout2(name=''):

    description = "Social Contract from Scratch•"
    # signature = st.session_state["username"]
    tier = "11"
    donation_type = "other"
    type_value = "11"
    interest_marker = "1"
    result_string = tier + type_value + interest_marker + '-' + 'S' + f'-{name}'
    
    st.session_state["tx_tag"] = f"SCFS{result_string}"

    reference = st.session_state["tx_tag"]
       
    # _signature = "77868affa87ca77cdeb146c89593bac64ec6dd2ee7265dfeec61941d87529845"

    @st.dialog("Full Signature")
    def _show_sig():
        st.write(st.session_state["username"])
        
    donation = float(st.session_state["donation"])
    investment_input = 0
    
    price = st.session_state["price"]    
    st.markdown(f'# <center> Commit # {st.session_state["price"]}</center>', unsafe_allow_html=True)
    st.markdown(f"""
    ## <center> $$ \\underbrace{{{donation:.2f} \\text{{~EUR}}}}_{{\\text{{Donation}}}}~+\\underbrace{{{price}}}_{{\\text{{Commit \\#}}}}$$ </center>
    """, unsafe_allow_html=True)
    # st.markdown(f"""# <center> = </center>""", unsafe_allow_html=True)
   
    total_amount = around(donation + price + investment_input, 2)
    st.markdown(f"""
                # <center>========= {total_amount:.2f} =========</center>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### Short code: {reference}", unsafe_allow_html=True)
    # st.markdown(f"### Commit signature: {signature}", unsafe_allow_html=True)
    """
    The button below will create a record and initialise your dashboard. This donation will be a trace of your philanthropic commitment.
    
    
    """
    if not bool(st.session_state['sumup']):
        st.warning('Authorise money, first.')
    if st.button(f"Validation:  {total_amount} _is the right number!_", type='primary', key="checkout", help="Record a trace on the ledger", use_container_width=True, disabled=not bool(st.session_state['sumup'])):
        with st.spinner("Creating record..."):
            reference = reference+f"-{int(now.strftime('%S'))}"
            time.sleep(1)
            st.write(f"The full reference is {reference} (computed as a function of the current time)")
        signature = ''
        if len(st.session_state['checkouts']) == 0:              
            checkout = create_commit_checkout(reference, total_amount, description + reference + '•' + mask_string(signature))

            st.session_state['checkouts'] = checkout
            
        else:
            st.warning("There already is a record of this session. You can list it below.")
    
    checkout = st.session_state['checkouts']
    if st.session_state['checkouts']:
        if st.button(f"Debrief details (double check)", key=f"checkout_info_{checkout}", type='primary', use_container_width=True):
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                with st.container():
                    checkout_info = get_checkout_info(checkout['id'])
                    # st.json(checkout_info)
                    st.write(f"**Amount:** {checkout_info['amount']} {checkout_info['currency']}")
                    st.write(f"**Checkout Reference:** {checkout_info['checkout_reference']}")
                    st.write(f"**Date:** {checkout_info['date']}")
                    st.write(f"**Description:** {checkout_info['description']}")
                    st.write(f"**Transaction ID:** {checkout_info['id']}")
                    st.write(f"**Merchant Country:** {checkout_info['merchant_country']}")
                    st.write(f"**Merchant Name:** {checkout_info['merchant_name']}")
                    st.write(f"**Status:** {checkout_info['status']}")

        if st.button(f"Remove", key=f"remove_checkout_{checkout['id']}", type='secondary', use_container_width=True):
            st.session_state['checkouts'] = []

    # """
    # Let's save essential data (e.g., preferences, ideas, initial information) before the payment to ensure nothing is lost if the payment fails (some will _indeed_ fail!) 
    
    # """
    return total_amount


# @st.dialog("This is a dialogue")
def sumup_widget(checkout_id):
                            # showInstallments: true,

        js_code = f"""
                    <div id="sumup-card"></div>
                    <script type="text/javascript" src="https://gateway.sumup.com/gateway/ecom/card/v2/sdk.js"></script>
                    <script type="text/javascript">
                        SumUpCard.mount({{
                            id: 'sumup-card',
                            checkoutId: '{checkout_id}',
                            donateSubmitButton: false,
                            onResponse: function (type, body) {{
                            console.log('Type', type);
                            console.log('Body', body);
                            }},
                        }});
                    </script>
                    """
        # st.write(js_code)
        with st.container():
            components.html(js_code, height=700)

def donation():
    
    st.markdown("## <center> Donation</center>", unsafe_allow_html=True)
    """
    ### **Donation Options:**
    
    This is your Custom Donation, allowing you to select any amount that feels good. 
    
    Each donation helps us move forward to our Athens meeting.

    """
    # Define the icons and labels for the buttons
    options = {
        'A Coffee': {'amount': '17', 'icon': ':material/coffee:'},
        'Partial Dinner': {'amount': '100', 'icon': ':material/restaurant:'},
        'Partial Accommodation': {'amount': '1000', 'icon': ':material/hotel:'},
        'Partial Travel': {'amount': '0', 'icon': ':material/jump_to_element:'}
    }

    custom_donation = True
    
    if custom_donation:
        min_exp_value = 0
        max_exp_value = 5
        min_actual_value = 1
        max_actual_value = 100000-0.1

        exp_value = survey.slider(label = "This is a Sensitive Slider",
                                    id = "custom_donation_slider", 
                                    min_value=float(min_exp_value), max_value=float(max_exp_value), value=float(min_exp_value),
                                step = 0.01,
                                format="%d")

        # Convert exponential value to actual value
        actual_value = exp_to_actual(exp_value)+0.1

        # Display the actual type: exp_value if actual value < 3000, otherwise -1
        donation_type = lambda x, t: int(x)+10 if t < 3000 else -1
        # st.write(f"Donation Value: {actual_value:.1f} EUR, Donation type: {int(exp_value)}")
        st.markdown(f"### Donation: {actual_value:.1f} EUR")
        st.session_state["donation"] = actual_value

    if custom_donation:
        st.divider()
    
    """
    #### Approximate references:
            
    - **Custom Donation:** You to pick your preferred number.
    - **:material/coffee: :** "Sponsor a Coffee for the collective" – 17 EUR
    - **:material/restaurant: :** "Cover a Light Lunch or Part of Dinner" – 100 EUR
    - **:material/hotel::** "Support Our Accommodation" – 1000 EUR
    - **:material/jump_to_element: :** "Support Our Travels" – 1111 EUR
    """

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
        # switch_value = ui.switch(default_checked=True, label="Enable economic", key="switch1")
        whitelist = ui.button(text="Join the whitelist", url="", key="link_btn")
        if whitelist:
            # st.toast("Whitelist")
            join_waitlist()

    st.markdown("# <center>The Social Contract from Scratch</center>", unsafe_allow_html=True)

    st.markdown("## <center>A meeting of Social and Natural Sciences, Philosophy, and Arts.</center>", unsafe_allow_html=True)
    # st.markdown('<center>`wait a minute`</center>', unsafe_allow_html=True)
    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}")

    st.divider()
    st.markdown(f"# <center>Start With a Donation</center> ", unsafe_allow_html=True)
    
    # st_lottie("https://lottie.host/d8addf11-2974-4c28-80be-df3d9d7273c5/9FuMagA41S.json")
    # st_lottie("https://lottie.host/ec578eca-0d54-4173-b4a4-9bd5eadf577c/bIR9lUB6Sk.json")
    # st_lottie("https://lottie.host/8d0158ec-6eaf-4867-a96c-4774fd2890e2/wFLLXK2Tmj.json")

def exp_to_actual(value):
    return 10**value

def question():
            
    role = my_create_dichotomy(key = "executive", id= "executive",
                        kwargs={'survey': survey,
                            'label': 'future_outlook', 
                            'question': 'Are you ready to donate? (White: Yes, Black: No, Nuances: I need time)',
                            'gradientWidth': 20,
                            'height': 250,
                            'title': '',
                            'name': f'{name}',
                            'messages': ["*Does not sound like a good deal,* let's question the fundamentals!", 
                                         "*Full willingness*. And full trust in the authority", 
                                         "*My willingness is* conditional"],
                            # 'inverse_choice': inverse_choice,
                            'callback': lambda x: ''
                            }
                        )
            

if __name__ == "__main__":
    
    intro()

    """
    
You've arrived on this page because you're considering donating to a project that aims to refresh the way we think about society, governance, and human connection. By supporting us, you're not just contributing to an idea—you're helping build a platform for real exchange. Our mission, with your help, is to challenge the status quo and reimagine the social contract _from scratch_.

Your donation will go directly towards covering the essential costs for our 17-member team, attending the upcoming conference in Athens. We're bringing together scholars, thinkers, and innovators to engage in participatory dialogue, technology development, and creative exploration of new societal models.
"""
    st_lottie("https://lottie.host/91efca67-fa13-43db-8302-f5c182af8152/ufDyVWvWdR.json")

    """
But this donation is only the beginning of a wider journey. As a supporter, you'll be directly connected to the progress of our work and the positive outcomes that will spring from this initiative. Thank you for considering this contribution—we're excited for the possibility of collaborating with you!
"""
### **Support Our Mission at the Social Contract from Scratch Conference**
    st_lottie("https://lottie.host/fc486c68-4574-4593-b9fb-d504f1f9c980/Nvrgg8KGLA.json")
    
    """
We are the **Athena Collective**, we'll be participating in a key panel discussion at the **Europe in Discourse Conference in Athens**, where we'll present our collaborative work, blending philosophy, technology, and social innovation.

Our goal? To build a **Social Contract from Scratch**: an _understanding_ or an agreement that underscores the urgent challenges of our time 
— ranging from environmental crises to social inequality— and encourages participatory governance and collective decision-making.


The  **Athena Collective** is Ariane Ahmadi, Nils Andersen, Bianca Apollonio, Alessandra Carosi, Gabrielle Dyson, flcalb, Giorgio Funaro, Hugues Genevois, Laurence White-Bouckaert, Claire Glanois, Amir Issaa, Andrés León Baldelli, Graziano Mazza, Roger Niyigena Karera, Francesco Raneri, Antonia Taddei, and Sophie Wahnich.
"""
    st.markdown("## <center>Our Initiative at a Glance</center>", unsafe_allow_html=True)

    event_2 = st_player("https://vimeo.com/1007188309", key='vimeo_player_2')
    """
    ### Ready to support?
    """
    name = survey.text_input("Let's start with your name — we may have already crossed paths.", id="name")
    
    donation()
    checkout()
    
    donation_amount = checkout2(name)

    _checkout = st.session_state['checkouts']
    if _checkout:
        if st.button(f":material/rainy_snow: I Am Happy to  Donate :material/rainy_snow: ", type='primary', key=f"pay-{_checkout['id']}", help=f"Click to open a dialogue, {mask_string(_checkout['id'])} / {mask_string('')}", use_container_width=True):
            sumup_widget(_checkout['id'])
            
    st.markdown(
        """
        Due to the heartfelt nature of the donation, processing might _feel_ it takes _a moment_*.
        Please remain on the processing page while the spinner runs. If the process takes longer than expected, feel free to take a few breaths.
        
        *: _Our experience is that the transaction is usually completed within a few seconds, but the dialogue window does not provide a visual feedback: the final outcome is only written to the developers' console._ 
        
        Don't worry, we shall be able to retrieve the verification at a later stage.
        """
    )
    
    if st.button(f"Clear all and restart",type='secondary', key=f"restart", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st_lottie("https://lottie.host/e83269bc-3342-4d2c-a4d9-9b8cabd8d7f9/JKz0q1LqzR.json")
