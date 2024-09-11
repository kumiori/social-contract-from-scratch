import streamlit as st
import requests
import time

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
from datetime import datetime

st_gtag(
    key="gtag_consent",
    id="G-Q55XHE2GJB",
    event_name="apply_consent",
    params={
        "event_category": "apply_games",
        "event_label": "consent",
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
    # st.markdown(f"`Now is {now.strftime('%s')}-{now.strftime('%f')}~` max is {st.session_state.range if st.session_state.range else ''}")

survey = CustomStreamlitSurvey()

if 'read_texts' not in st.session_state:
    st.session_state.read_texts = set()
else:
    st.session_state.read_texts = set(st.session_state.read_texts)
    
if 'donation' not in st.session_state:
    st.session_state.donation = 0

if 'page' not in st.session_state:
    st.session_state.page = "Cover"

if 'investment_input' not in st.session_state:
    st.session_state.investment_input = 0

if 'alerted' not in st.session_state:
    st.session_state.alerted = False

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

authenticator = AuthenticateWithKey(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
fields_connect = {'Form name':'Open with your access key', 'Email':'Email', 'Username':'Username',
            'Password':'Password', 'Repeat password':'Repeat password',
            'Register':' Retrieve access key ', 'Captcha':'Captcha'}
fields_forge = {'Form name':'Where is my access key?', 'Email':'Email', 'Username':'Username',
            'Password':'Password', 'Repeat password':'Repeat password',
            'Register':' Here • Now ', 'Captcha':'Captcha'}
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


@st.dialog("Join the whitelist")
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
    st.markdown("## <center>Integrate the data</center>", unsafe_allow_html=True)
    st.markdown(
"""
    For this, we need your signature:
""")
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
    st.write("Click the link below to authorise this. Your authorisation is key to proceed. If everything is in order, you will read above a message of success, or a unique ID below.")
    if st.button("It is OK to bring money into the game", type='primary', key="authorise", use_container_width=True, disabled=not bool(st.session_state['authentication_status'])):
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
    As soon as our payments channels open, we will be able to share the timeline.
    
    """
    # st.markdown("Click the expand button below to know more about the payment mechanics.")
    with st.expander("Payments and ledger, further details", expanded=False):
        st.write("The payment data is stored in your session's _state_ and can be accessed by your end for further processing. This app uses the SumUp API (sumup.com) to create checkouts and process payments. Finally, we rely on CCF bank, a French commercial bank founded in 1894 and acquired by HSBC in 2000, as the (_untrusted_) ledger.")
    
def checkout2():

    description = "Social Contract from Scratch•"
    # signature = st.session_state["username"]
    tier = "11"
    donation_type = "other"
    type_value = "11"
    interest_marker = "1"
    result_string = tier + type_value + interest_marker + '-' + 'S'
    
    st.session_state["tx_tag"] = f"SCFS{result_string}"

    reference = st.session_state["tx_tag"]
       
    # _signature = "77868affa87ca77cdeb146c89593bac64ec6dd2ee7265dfeec61941d87529845"

    @st.dialog("Full Signature")
    def _show_sig():
        st.write(st.session_state["username"])
        
    donation = float(st.session_state["donation"])
    investment_input = st.session_state["investment_input"]
    
    price = st.session_state["price"]    
    st.markdown(f'# <center> Commit # {st.session_state["price"]}</center>', unsafe_allow_html=True)
    st.markdown(f"""
    ## <center> $$ \\underbrace{{{donation:.2f} \\text{{~EUR}}}}_{{\\text{{Donation}}}}~+\\underbrace{{{price}}}_{{\\text{{Commit \\#}}}}$$ </center>
    """, unsafe_allow_html=True)
    # st.markdown(f"""# <center> = </center>""", unsafe_allow_html=True)
   
    total_amount = donation + price + investment_input
    st.markdown(f"""
                # <center>========= {total_amount:.2f} =========</center>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### Short code: {reference}", unsafe_allow_html=True)
    # st.markdown(f"### Commit signature: {signature}", unsafe_allow_html=True)
    """
    The button below will create a record to be etched on the ledger. This entry will be a trace of your philanthropic commitment, a digital footprint of your philanthropic intention.
    
    
    """
    # REMOVE STEP
    # if st.button("Create record", type='primary', key="checkout", help="Record a trace on the ledger", use_container_width=True, disabled=not bool(st.session_state['sumup'])):
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
    
    st.write("Commits:")
    if st.button("Philanthropic committment", key="list_checkouts", use_container_width=True):
        if len(st.session_state['checkouts']) == 0:
            st.warning("There is nothing to commit, yet.")
            
        else:
            st.json(st.session_state['checkouts'])    
    # st.write(st.session_state['checkouts'])
    
    # if st.button("Clear commits", key="clear_checkouts", use_container_width=True):
    #     st.session_state['checkouts'] = []
    #     st.success("Commits cleared.")
    
    checkout = st.session_state['checkouts']
    if st.session_state['checkouts']:
        if st.button(f"Debrief (double check)", key=f"checkout_info_{checkout}", type='primary', use_container_width=True):
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

    """
    Let's save essential data (e.g., preferences, ideas, initial information) before the payment to ensure nothing is lost if the payment fails (some will _indeed_ fail!) 
    
    """
    return

@st.dialog("This is the development of a dialogue")
def sumup_widget(checkout_id):
        # st.markdown("""
        #     <script src="https://gateway.sumup.com/gateway/ecom/card/v2/sdk.js"></script>
        #     <script>
        #         function initSumUpWidget() {
        #             // Check if SumUpCard is available
        #             console.log('initialising SumUpCard.');
        #             if (window.SumUpCard) {
        #                 // Example of mounting the payment widget
        #                 const sumUpCard = window.SumUpCard;
        #                 console.log('SumUpCard is available.');
        #                 console.log('SumUpCard:', sumUpCard);                        
        #             } else {
        #                 console.error('SumUpCard is not available.');
        #             }
        #         }

        #         // Initialize SumUp Widget after the script is loaded
        #         document.addEventListener('DOMContentLoaded', function() {
        #             initSumUpWidget();
        #         });
        #     </script>
        # """, unsafe_allow_html=True)
        
        js_code = f"""
                    <div id="sumup-card"></div>
                    <script type="text/javascript" src="https://gateway.sumup.com/gateway/ecom/card/v2/sdk.js"></script>
                    <script type="text/javascript">
                        SumUpCard.mount({{
                            id: 'sumup-card',
                            checkoutId: '{checkout_id}',
                            donateSubmitButton: false,
                            showInstallments: true,
                            onResponse: function (type, body) {{
                            console.log('Type', type);
                            console.log('Body', body);
                            }},
                        }});
                    </script>
                    """
        # st.write(js_code)
        with st.container():
            components.html(js_code, height=600)

def dataset_to_outro(dataset):
    # 
    # st.write(dataset)
    
    formatted_text = "#### "
    qualitative_value = float(dataset["willingness"]["value"]) if dataset["willingness"]["value"] else 1
    if qualitative_value > .99:
        qualitative_desc = "fully willing"
    elif qualitative_value < .01 :
        qualitative_desc = "unwilling"
    else:
        qualitative_desc = "willing, depending upon conditions,"
    ext = '' if qualitative_value > .9 else ' do not '
    formatted_text += f"I commit to start this journey `{qualitative_desc}` to give up my freedom in exchange for protection and stability from an authority or central entity."
    name = dataset["name"]["value"] if dataset["name"]["value"] else 'Anonymous'
    
    # if dataset.get("future_outlook", {}).get("value") is not None:
    #     future_outlook = float(dataset.get("future_outlook", {}).get("value", False))
        
    #     outlook = "bright horizon" if future_outlook >= 1 else "dark storm" if future_outlook < 0.5 else "grey mist"
    #     leaning = ", leaning `to the bright`." if future_outlook > 0.5 and future_outlook < 1. else ", leaning `to the dark`." if future_outlook < .5 and future_outlook > 0. else "."

    #     formatted_text += f", my outlook for the future is a `{outlook}`{leaning}"
            
    return formatted_text, name, ext

def dataset_to_text(dataset, perspective='first'):
    text = ""
    # Start with the qualitative decision
    qualitative_value = dataset["Qualitative"]["value"]
    if qualitative_value == "1":
        qualitative_desc = "supporting"
    elif qualitative_value == "2":
        qualitative_desc = "investing"
    elif qualitative_value == "10":
        qualitative_desc = "donating"
    else:
        qualitative_desc = "participating"

    # Map the future_outlook
    
    if perspective == "first":
        pronoun = "I"
        possessive = "my"
        verb = "am"
    elif perspective == "third":
        pronoun = "You"
        possessive = "your"
        verb = "are"
    else:
        raise ValueError("Perspective must be either 'first' or 'third'.")

    future_outlook_value = dataset.get("future_outlook", {}).get("value", False)
    future_outlook_text = "has't been considered yet." if bool(future_outlook_value) is False else "a lot" if float(future_outlook_value) >= .7 else "very little" if float(future_outlook_value) <= .3 else "moderately"
    # Determine interest mix
    if "equaliser_0" not in dataset:
        interests = [0, 0, 0, 0]
        interest_labels = "the surface"
    else:    
        interests = [
            dataset[f"equaliser_{i}"]["value"] for i in range(4)
        ]
        interest_labels = ", ".join(
                [dataset[f"equaliser_{i}"]["label"] for i in range(4)]
            )
            
    interest_mixture = "mix well" if len(set(interests)) == 1 else "vary a lot"
    # st.write(interests)
    interest_level = "high" if sum(interests) > 150 else "low"
    
    connector = "and" if interest_level == 'high' else "yet"
    # Create the text output
    text = (
        f"{pronoun.title()} decide to start this journey `{qualitative_desc}` as a philanthropist. In this sense, the future `{'looks ' if future_outlook_value is not None else future_outlook_text}`. "
        f"{possessive.title()} current interest levels are `{interest_level}`, `{connector}` `{interest_mixture}` across `{interest_labels}`. "
    )

    if qualitative_desc == "investing":
        risk_appetite = dataset.get("Risk Appetite:", {}).get("value", "unknown")
        expression_return_rates = dataset.get("Select how you want to express return rates:", {}).get("value", "unknown")
        expected_return = dataset.get("This is my expected return rate (%):", {}).get("value", "unknown")
        st.write(dataset)
        dream_return = dataset.get("This is my dream return rate (%):", {}).get("value", "unknown")

        investment_profile = f"{possessive.title()} investing profile has a `{risk_appetite}` risk appetite. Quantitatively, {possessive} investment bracket (_expected_ vs. _dream_) spans `{expected_return}`% and `{dream_return}`%."

        if bool(expected_return and dream_return) is False:
            text = text + ("""
                        However, something looks wrong in the return rates. Let's check the data again.
                        """)

    else:
        investment_profile = f""
    
    text = text + investment_profile

    return text

def donation():
    
    st.markdown("## <center> Donation</center>", unsafe_allow_html=True)
    """
    ### **Donation Options:**
    
    You can choose a Custom Donation, allowing you to select any amount that feels good. 
    
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
            
    - **Custom Donation:** Allows you to pick your preferred number.
    - **:material/coffee: :** "Sponsor a Coffee for the collective" – 17 EUR
    - **:material/restaurant: :** "Cover a Light Lunch or Part of Dinner" – 100 EUR
    - **:material/hotel::** "Support Our Accommodation" – 1000 EUR
    - **:material/jump_to_element: :** "Support Our Travels" – 1111 EUR
    """

import pandas as pd
import numpy as np

import plotly.express as px

def create_scatter_plot(color='rgba(30, 144, 255, {})'):
    # Generate random data
    np.random.seed(42)
    n_points = 100
    x = np.random.randn(n_points)
    y = np.random.randn(n_points)
    transparency = np.random.rand(n_points)
    marker_size = np.random.randint(10, 100, n_points)

    # Create a DataFrame
    df = pd.DataFrame({
        'x': x,
        'y': y,
        'transparency': transparency,
        'size': marker_size
    })

    # Create the scatter plot
    fig = px.scatter(df, x='x', y='y', size='size', size_max=20)

    # Update markers with varying transparency and random sizes
    fig.update_traces(marker=dict(
        color=[color.format(op) for op in transparency],
        line=dict(width=1)
    ))

    # Customize layout to remove grids, ticks, and labels, and make the plot square
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=600,
        height=600
    )

    return fig

def outro():
    st.markdown("## <center> Step X: _Chapter One_</center>", unsafe_allow_html=True)
    formatted_text, name, ext = dataset_to_outro(survey.data)
    st.markdown(formatted_text)
    
    _submit = st.button(f'I {ext} submit, _{name}_')
    # st.write(st.session_state['tx_tag'])
    # st.write(st.session_state['checkouts']['id'])
    
    dashboard_data = {**st.session_state['serialised_data'], 'checkout': st.session_state['checkouts'], 'checkout_tag': st.session_state['tx_tag']}
    
    
    st.session_state['serialised_data'] = dashboard_data
    
    if _submit:
        stream_once_then_write(
            """
            Congrats! 
            
            Thank you for your interest. We will get back to you by email.
        
            """
"""
_In the meantime_:"""
"""
Here is a snapshot of current activities and developments. Any insight to share?
"""
# This includes updates on ongoing projects, conceptual ideas in the pipeline, and longer-term ventures that are now yielding positive results. 
"""
	1. Health Systems and their pervasive collapse under sectarian influences.
	2. Monetisation: Pressing cyanotypes from experimental human campaigns, 
            economic photography and scientific reflection.
	3. Scientific Projects: Energy transitions, jumps, and the stability of 
            the cryosphere, did we understand evolution?
	4. Philosophical Dinners: Gastronomic events where ideas are served as meals, 
            connecting within experience.
    5. Artistic Endeavours: all the Arts, with a focus on music, the natural world, 
            ceramics, and illustration.
    6. Literature: Communication within the Urban Jungle | the vertical scheme. 
""")
    with st.spinner("Thinking?"):
        time.sleep(1)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        text = """
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
        `No need to "Submit", your dashboard is saved.`
        """)


@st.cache_data    
def fetch_data():
    response = db.fetch_data(kwargs={'verbose': True})
    return response

# Function to extract willingness and updated_at
def extract_willingness_and_updated_at(data):
    results = []
    for entry in data:
        if entry.get("consent_00"):
            consent_data = json.loads(entry["consent_00"])
            willingness = consent_data.get("willingness", {}).get("value")
            updated_at = entry.get("updated_at")
            if willingness and updated_at:
                # Convert the updated_at to a more readable format
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                results.append({"willingness": willingness, "updated_at": updated_at})
    return results

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
    st.markdown(f"# <center>Testing Basic Assumptions</center> ", unsafe_allow_html=True)
    

    # philoui.io
    
def question():
    
    st.markdown("""
    ### This is not a one-time deal. Just like society, consent evolves with new challenges and perspectives. You’ll be part of that evolution.
    """)
    
    role = my_create_dichotomy(key = "executive", id= "executive",
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
1.	Zero Willingness emphasises individual liberty and distrust in giving up freedoms.
2.	Conditional Willingness highlights opennes to negotiation but under specific conditions, prompting reflection on those conditions.
3.	Full Willingness shows complete trust in the system and prioritises collective security and stability over personal freedom.
    """
 

def exp_to_actual(value):
    return 10**value

if __name__ == "__main__":
    
    intro()
    
    """
    Welcome to the Social Contract from Scratch — a live experiment in testing society's foundations. 
    """
    """
    ### Let's strike a deal that shows how we live and thrive together.


    # We need 100 participants to unlock the next stage. 
    ###  What happens at the next stage? _Find a teaser below._
    """
    """
    We choose to live in society because it offers us the benefits of cooperation and connection that we could not achieve in isolation.
    Living together lets us achieve what we can't on our own — sharing resources, knowledge, and building systems that elevate our lives from mere survival to thriving.
    """

    """
    ### Are you relinquishing freedoms or are you among the ones managing collective welfare?
    """
    

    event_2 = st_player("https://vimeo.com/1007188309", key='vimeo_player_2')
    
    
    """
    A contract is an agreement, a story between two or more parties. As an agreement, it is an understanding.
    When the understanding is shared, it becomes social.
    """
    """
    # But how should a social contract work?
    """
    f"""
Let’s take a foundational idea from the 17th century—one that still underpins much of Western and European governance—and put it to the test in today's world. 
It often assumes implicit consent, meaning people agree without ever explicitly being asked. 
Starting today, {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}, _we challenge that assumption._    """
    """
Here, we _cut through_ and ask directly:  **Are you willing to relinquish some of your freedoms in exchange for the benefits of living in a society?** _In other words_, **Do you accept this deal?** 

This is where _you_ come in, casting a real, meaningful preference—_yours_.

Our approach is explicit and participatory, aiming for informed, active consent. 
    Here, participants contribute directly to the construction of our bonds, 
    manifesting a real voice in determining their principles. 
    Stakeholders are real and governing structures are transparent.
    
### We would like clarity. 
    
This makes _our consent_ both foundational and dynamic, allowing it to evolve as the contract itself grows and responds to new inputs and challenges. 
    
By interacting, we question basic assumptions and actively engage in shaping consent dynamics, making it an active, ongoing construction rather than a passive agreement.
    """
    """
    By participating, you actively shape the foundations of _a new social contract_ experiment. Your consent isn't just a checkbox — 
    it's a voice in the construction of principles we live by.
    """

    """
### This is more than just a game, this is a collective discovery process.

"""
    """
    ### Ready to make your voice count?
    """
    name = survey.text_input("Let's start with your name — we may have already crossed paths.", id="name")
    
    st.divider()
    """
    ## So how does _this foundational deal_ look?
    """
    """
    It assumes you respond _fully_ to the following question:
    """
    """
    # How willing are you to give up your freedoms in exchange for protection and stability, relinquishing your participation in decisions that affect you?
    """
    
    
    """
    The deal is a "classic" social contract: the individual surrenders certain liberties in exchange for the protection and decision-making provided by a sovereign or governing entity. But, crucially, the individual doesn't get to participate in the decision-making process—they trust that the sovereign will act in their best interest.
    """
    
    """
    Here's a simple question which still allows for a nuanced response. 
    
    
    
    **Choose between** 0/black (not willing to give up freedom), 1/white (fully willing to give up freedom), 
    and all values in between - greys - (representing conditional, small or large, willingness). We will gather detailed insights!
    
    At this clickable interface we arrive at a crossroads where you can choose...
    """
    # https://lottie.host/embed/45438b97-2912-4a45-97b1-7a6e300abc99/xVtk48wj6I.json
    # https://lottie.host/embed/2785afba-d09a-4268-9c5e-e343d6f6079a/IKh7NP1UTT.json

    question()


 
    from streamlit_elements import elements, mui, nivo
    
    response = fetch_data()
    response = extract_willingness_and_updated_at(response)
    # df = pd.DataFrame(response)
    # st.table(df)


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
    "value": 19
  },
  {
    "id": "Conditional",
    "label": "Conditional",
    "value": 10
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

    f"""
    Based on the partial data from the survey, we can make a few key observations and offer some initial reflections:

    ### Preliminary Analysis (last updated, a while ago):

    1. **Strong preference for preserving freedom**: 
    The most striking takeaway is that **19 out of the 29 participants** (roughly **65%**) have shown **zero willingness** to give up any personal freedoms. This indicates a significant collective inclination towards the preservation of individual liberties. It suggests that participants place high value on personal autonomy and may have deep concerns about relinquishing their freedoms, even in exchange for protection or stability.

    2. **Conditional willingness for compromise**:
    While the majority prefer not to give up any freedoms, we also see a notable minority — **10 individuals** (about **35%**) — who express **conditional willingness**. This group may be more open to compromise but under specific conditions. It suggests that they might entertain the idea of sacrificing certain freedoms if they perceive the offered stability or protection as sufficiently beneficial or necessary.

    3. **Complete rejection of full willingness**:
    **None** of the participants (0%) have shown **full willingness** to give up their freedoms entirely. This unanimous refusal to completely surrender personal liberties could reflect a broader skepticism or distrust in authority or systems that demand total submission in exchange for security.

    ### Any insights to share?

    - **Cautious approach to authority**: 
    The overwhelming number of participants unwilling to give up any freedom, combined with the lack of full willingness, suggests a collective wariness towards systems or contracts that require giving up personal liberties. This could imply a broader concern about the concentration of power or authority, and an aversion to hierarchical systems where individuals lose agency.

    - **Nuanced willingness to compromise**: 
    The presence of a group expressing **conditional willingness** hints at a more nuanced view. These individuals may be open to negotiation or compromise if the right conditions are met. It points to a potential avenue for dialogue, where the specific circumstances that would justify relinquishing freedoms can be explored.

    - **Challenges ahead for consensus**: 
    Given that no one is fully willing to give up their freedoms, and a majority are entirely against the idea, reaching consensus on a **social contract** that involves any sacrifice of liberties might prove challenging. However, the conditional willingness group could offer a middle ground, suggesting that dialogue and clear, well-defined terms could sway some participants.

    ### Comment
    "The preliminary results from the survey highlight a strong collective inclination to preserve individual freedoms, with 65% of participants expressing zero willingness to give up any personal liberties. While 35% are conditionally open to compromise, none of the respondents are fully willing to surrender their freedoms. This suggests that while there is some room for negotiation, any proposal to restrict freedoms in exchange for protection or stability would likely face significant resistance, especially without clear guarantees or carefully defined conditions. As we move forward, engaging with the conditional group could help identify the terms under which compromise is possible, while further exploring the concerns of those firmly against giving up freedoms."

    Are these key findings? Highlighting both the resistance and the potential pathways for further discussion...

    """
    """
    # Integrate your preferences and expand our picture
    
    If yes, you can review the data you've contributed before proceeding.
    
    """
    
    with st.expander("Review your data", expanded=False):
        st.json(survey.data)

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
    

    if st.session_state['authentication_status']:
        authenticator.logout()

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
        
    
    st.divider()
    
    
    
    
    from streamlit_lottie import st_lottie
    
    st_lottie("https://lottie.host/e83269bc-3342-4d2c-a4d9-9b8cabd8d7f9/JKz0q1LqzR.json")
    
    
    """
    ## The next stage is _Building_.
    """
    
    """
    The next stage, once we hit our 100 participants, we shift from **individual willingness** to **collective design**. 
    Now that we've understood the direction of our personal freedoms, we will **co-create the pillars** of our exchange — unfolding together **what systems, values, and protections** will emerge from a shared understanding.
    
    In this stage, each of us will contribute to shaping the **levels of engagement**, 
    identifying what is **common and of value** that will hold our society together. 
    It's no longer about _giving up_; it's about building up—**crafting the foundation** 
    of something wider, something shared. 
    
    Together, we draw blueprints for new social bonds. 
    """
    
    outro()
    

# who's the players: we have them on stage
# what is the venue: we have an idea.
# how about setting up a timeline: we have a plan.
# what about the audience: we have a list.
# what about the cooks: we have a duo.