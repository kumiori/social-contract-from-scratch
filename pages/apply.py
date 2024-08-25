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
from philoui.io import conn, create_dichotomy, create_equaliser, create_qualitative
from philoui.survey import CustomStreamlitSurvey
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row
from streamlit_timeline import timeline
from yaml import SafeLoader
from streamlit_player import st_player

db = IODatabase(conn, "discourse-data")

with open("assets/discourse.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.write(f.read())
    
with open('assets/credentials.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    now = datetime.now()
    # st.markdown(f"`Now is {now.strftime('%s')}-{now.strftime('%f')}~` max is {st.session_state.range if st.session_state.range else ''}")

survey = CustomStreamlitSurvey()

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
    st.session_state.price = 100.01
    
authenticator = AuthenticateWithKey(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
fields_connect = {'Form name':'Have you ever found the key out of the portal?', 'Email':'Email', 'Username':'Username',
            'Password':'Password', 'Repeat password':'Repeat password',
            'Register':' Here • Now ', 'Captcha':'Captcha'}
fields_forge = {'Form name':'Forge access key', 'Email':'Email', 'Username':'Username',
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

@st.dialog('Cast your preferences')
def _submit(serialised_data, signature):
    # st.write('Thanks, expand below to see your data')    
    # signature = st.session_state["username"]
    with st.spinner("Checking your signature..."):
        # time.sleep(2)
        preferences_exists = db.check_existence(signature)
        # st.write(f"Integrating signature preferences `{mask_string(signature)}`")
        st.write(f"Integrating signature preferences ``")
        _response = "Yes!" if preferences_exists else "Not yet"
        st.info(f"Some of your preferences exist...{_response}")
        # serialised_data = st.session_state['serialised_data']

        try:
            data = {
                'signature': signature,
                'philanthropy_01': json.dumps(serialised_data)
            }
            # throw an error if signature is null
            if not signature:
                raise ValueError("Signature cannot be null or empty.")
            
            query = conn.table('discourse-data')                \
                   .upsert(data, on_conflict=['signature'])     \
                   .execute()
            
            if query:
                st.success("🎊 Preferences integrated successfully!")

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
                            SumUpCard.unmount();
                            }},
                        }});
                    </script>
                    """
        # st.write(js_code)
        with st.container():
            components.html(js_code, height=600)

def dataset_to_intro(dataset):
    formatted_text = "#### "
    qualitative_value = dataset["Qualitative"]["value"]
    if qualitative_value == "1":
        qualitative_desc = "supporting"
    elif qualitative_value == "2":
        qualitative_desc = "investing"
    elif qualitative_value == "10":
        qualitative_desc = "donating"
    else:
        qualitative_desc = "participating"

    formatted_text += f"I decide to start this journey `{qualitative_desc}` as a philanthropist"

    if dataset.get("future_outlook", {}).get("value") is not None:
        future_outlook = float(dataset.get("future_outlook", {}).get("value", False))
        
        outlook = "bright horizon" if future_outlook >= 1 else "dark storm" if future_outlook < 0.5 else "grey mist"
        leaning = ", leaning `to the bright`." if future_outlook > 0.5 and future_outlook < 1. else ", leaning `to the dark`." if future_outlook < .5 and future_outlook > 0. else "."

        formatted_text += f", my outlook for the future is a `{outlook}`{leaning}."
    return formatted_text

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
        f"{pronoun.title()} decide to start this journey `{qualitative_desc}` as a philanthropist. In this sense, the idea `{'resonates ' if future_outlook_value is not None else future_outlook_text}`. "
        f"{possessive.title()} current interest levels are `{interest_level}`, `{connector}` `{interest_mixture}` across `{interest_labels}`. "
    )
    # st.write(qualitative_desc)
    # Risk appetite and return rates for investing profile
    if qualitative_desc == "investing":
        risk_appetite = dataset.get("Risk Appetite:", {}).get("value", "unknown")
        expression_return_rates = dataset.get("Select how you want to express return rates:", {}).get("value", "unknown")
        expected_return = dataset.get("Enter your expected return rate (%):", {}).get("value", "unknown")
        dream_return = dataset.get("Enter your dream return rate (%):", {}).get("value", "unknown")

        investment_profile = f"{possessive.title()} investing profile has a `{risk_appetite}` risk appetite. In terms of revenues, {pronoun} prefer to express return rates in terms of `{expression_return_rates}`. Quantitatively, {possessive} investment bracket spans `{expected_return}`% and `{dream_return}`%."

        # print(expected_return , dream_return)
        # print('or', expected_return or dream_return)

        if bool(expected_return and dream_return) is False:
            text = text + ("""
                        However, something looks wrong in the return rates above. Let's check the data again.
                        """)

    else:
        investment_profile = f"{pronoun} {verb} observing the world from a different perspective."
    
    text = text + investment_profile

    return text

def extract_info(data):
    checkouts = st.session_state.custom_donor
    
    # Determine the tier based on the value of Qualitative
    qualitative_value = data.get("Qualitative", {}).get("value", None)

    if qualitative_value is None:
        tier = "00"
    elif int(qualitative_value) == 1:
        tier = "01"
    elif int(qualitative_value) == 2:
        tier = "10"
    elif int(qualitative_value) == 10:
        tier = "11"
    # else:
    # Determine the type based on donation options
    if qualitative_value is not None:
        if data.get("coffee", {}).get("value", False):
            donation_type = "coffee"
            type_value = "00"
        elif data.get("dinner", {}).get("value", False):
            donation_type = "dinner"
            type_value = "01"
        elif data.get("accommodation", {}).get("value", False) or data.get("travel", {}).get("value", False):
            donation_type = "accommodation or travel"
            type_value = "10"
            
        # elif data.get("custom_donation", {}).get("value", False):
            # donation_type = "custom donation"
            # type_value = "11"
        else:
            donation_type = "other"
            type_value = "11"
        
        # if custom_donation:
        #     donation_type = "custom"
        #     type_value = "11"
    else:
        donation_type = "XX"
        type_value = "00"

    
    # if exists data[f"equaliser_{i}"]
    
    if "equaliser_0" not in data:
        interests = [0, 0, 0, 0]
    else:    
        interests = [
            data[f"equaliser_{i}"]["value"] for i in range(4)
        ]
    interest_level = "high" if sum(interests) > 150 else "low"
    interest_marker = "1" if interest_level == "high" else "0"
    
    result_string = tier + type_value + interest_marker + '-' + str(st.session_state['profile'])

    return result_string, (tier, type_value, donation_type), qualitative_value, interest_level

def exp_to_actual(value):
    return 10**value
    return min_actual_value * (max_actual_value / min_actual_value) ** ((value - min_exp_value) / (max_exp_value - min_exp_value))

def convert_string_to_decimal(input_string):
    from decimal import Decimal

    # Split the string into binary part and base-10 part
    binary_part, base10_part = input_string.split('-')
    
    # Convert the binary part to a decimal integer
    binary_decimal = int(binary_part, 2)
    
    # Convert the base-10 part to an integer
    if base10_part == 'None':
        base10_integer = 0
    else:
        base10_integer = int(base10_part)

    # Add the two values
    result = binary_decimal + base10_integer + 1

    if len(str(result)) == 1:
        result = '0' + str(result)
    
    return result

def vote_callback(id):
    st.session_state["profile"] = id

    if "toast" not in st.session_state:
        st.session_state["toast"] = False

    st.session_state["profile"] = id

def show_pathways(pathways, cols=3):
    links_row = row(len(pathways)//cols, vertical_align="center")
    
    st.session_state["current_pathway"] = None
    
    dico_style = """<style> 
        div[data-testid='stVerticalBlockBorderWrapper'] div[data-testid='stVerticalBlock'] [data-testid="baseButton-secondary"]:not(:has(div#profiles_outer)) p  {
            font-size: 4rem;
            padding: 1rem;
        };
        </style>
        """       
# #root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.st-emotion-cache-bm2z3a.ea3mdgi8 > div.block-container.st-emotion-cache-13ln4jf.ea3mdgi5 > div > div > div > div.st-emotion-cache-0.e1f1d6gn0 > div > div > div.st-emotion-cache-ocqkz7.e1f1d6gn5 > div:nth-child(2) > div > div > div > div > div > div > div.st-emotion-cache-1cyexbd.ef3psqc1 > button > div > p
# //*[@id="root"]/div[1]/div[1]/div/div/div/section[2]/div[1]/div/div/div/div[14]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/button/div/p

    script = """<div id = 'profiles_outer'></div>"""
    st.markdown(script, unsafe_allow_html=True)
    st.markdown(dico_style, unsafe_allow_html=True) 

    for id, (pathway, details) in enumerate(pathways.items(), start=1):
        icon = details['icon']
        description = details['description'] 

        button_text = f"{icon}"
        profile_id = links_row.button(button_text, help=description, key=id, 
                        on_click = vote_callback, args = ((id),))
    
    st.write('''<style>
        [data-testid="stVerticalBlock"] [data-testid="baseButton-secondary"] p {
            font-size: 1rem;
            padding: 1rem;
        }
        [data-testid="stVerticalBlock"] [data-testid="baseButton-secondary"][aria-pressed="true"] {
            border: 5px solid #FF5733;
            box-shadow: 0px 0px 10px 2px #FF5733;
        }
    </style>''', unsafe_allow_html=True)

        
def body1():
    st.divider()
    st.markdown("## <center> Step 0:  / Awareness</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        """
    Let's jump on the _action_ side of this philanthropic journey. 
    
    This is a digital platform which we build to stimulate interaction, committment and actionable decisions, gathering your stories and engaging.
    
    Designed to connect with you on multiple levels while ensuring that your preferences, perceptions, and contributions, are integrated in a meaningful and impactful way. 
    
    The combination of reflection, interaction, and emotion-driven engagement sets the stage for new collective experiences.

    """

def body2():
    st.markdown("## <center> Step 1:  / Reflection</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        """ 
    This is a process in several steps which interactively depend on your choices. 
    After you make a decision, take a moment to consider _why_ you made this choice and  _how_ does it align with your personal goals and values.

    This process will take approximately _the time of a good tea_. If you brew one, pause for a minute to think about why you're here.
    """

        """
    For now, our primary goal is to **gather your commitment to philanthropic intentions** and ensure that our objectives align. This process helps us understand your interests and motivations, setting the stage for collaboration. 
    
    Once we have established this connection and confirmed that our paths are in sync, we will reach out to discuss the next steps in more detail, ensuring that your contribution is aligned with action. 
    
    We look forward to exploring this journey together.
    """
    # We are populating the table of our shared elementary values, would you like to play

def engagement():
    st.markdown("## <center> Step 2: Engagement</center>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 9, 1])

    with col2:
        """
        We're offering three different ways to engage with our initiative: **Support**, **Invest**, or **Donate**.
        
        """
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        """
            **Support**, for us means that you are willing to back our initiative, but not necessarily with financial resources.
            """
    with col2:
        """            
        **Invest**, means that you are interested in contributing financially to our initiative, with the expectation of a return. Introduces an element of risk, allowing to get more creative.
        """
        
    with col3:
        """
        **Donate**, means that you are willing to contribute financially to our initiative, without expectation of financial gains. 
        """
    st.divider()
        
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        """
        **Remark:** in the long run, these options are not mutually exclusive.
        
        """
        
    st.markdown("## <center> Your choice</center>", unsafe_allow_html=True)
        
    engage_categories= {'1': 'Support', '2': 'Invest', '10': 'Donate'}
    engage = create_qualitative('trifurcation',
                        kwargs={"survey": survey, 
                                'label': 'categorical', 
                                "name": "we are at a crossing point.",
                                "question" : "Support (1, dark grey), Invest (2, light grey), or Donate (10, black)?",
                                "categories": engage_categories
                        })
    
    feedback_messages = {
        '1': "## I have chosen to **`Support`** this initiative. \n ### _Thank you,_ your backing is essential in helping us move forward.",
        '2': "## I have chosen to **`Invest`** in a shared vision. \n ### _Thank you,_ your interest in investment will help us consolidate and expand our activity.",
        '10': "## I have chosen to **`Donate`** to our cause. \n ### _Thank you,_ your generosity makes a significant difference."
    }
    
    if engage is not None:
        st.markdown(feedback_messages.get(str(engage), "Thank you for your dedication so far!"))
    else:
        st.write("Take your time to get used to this strange button, it's new _to us_ as well.")
        
        
    # if st.button("Reset the choice"):
    #     survey.data["Qualitative"]["value"] = None
    #     engage = None

def question():
    st.markdown("## <center> Step 3</center>", unsafe_allow_html=True)
    st.markdown("# <center> How do you _feel_ about the future?</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        """
        Is it a source of hope, a shadow of challenges, or a fog of uncertainty? 
        
        Imagine standing at the edge of tomorrow — do you see a bright horizon filled with light, a dark impending storm, or a grey mist that obscures all but the nearest steps? 
        
        Share your perception, whether it's a bright outlook, a dark foreboding, or an uncertain mix of both. 
        
        Your perspective helps us map the collective vision of what lies ahead.
        """
    my_create_dichotomy(key = "executive", id= "executive",
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
    
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """
We are populating the table of our shared elementary values. This is more than just a game, this is a collective discovery process.

"""
        )

def access():
    st.markdown("## <center> Step 3: Open your access</center>", unsafe_allow_html=True)
    """
    We've collected some insight so far...
    """
    # st.write(survey.data)
    col1, col2, col3 = st.columns([1, 9, 1])

    with col2:
        st.write('### You ' + dataset_to_intro(survey.data)[7::] + '!')
    """
    ### _We are looking forward._"""
    

    if st.session_state['authentication_status'] is None:
        # authenticator.login('Connect', 'main', fields = fields_connect)
        # st.warning('Please use your access key')
        """
        Let us forge an access key for you to proceed.
        """
        try:
            match = True
            success, access_key, response = authenticator.register_user(data = match, captcha=True, pre_authorization=False, fields = fields_forge)
            if success:
                st.success('Key successfully forged')
                st.toast(f'Access key: {access_key}')
                st.session_state['username'] = access_key
                # st.write(response)
                st.markdown(f"### My access key is `{access_key}`. Keep it safe: it will allow you to access the next steps.")
        except Exception as e:
            st.error(e)
    else:
        st.markdown(f"### My access key is already forged, its signature is `{mask_string(st.session_state['username'])}`.")

def authentication():
    
    st.markdown("## <center> Step X: Communication is key</center>", unsafe_allow_html=True)
    if st.session_state['authentication_status'] is None:
        """### Towards our conference in Athens _Europe in Discourse_"""
        col1, col2, col3 = st.columns([1, 9, 1])
        with col2:
            """
            Our primary objective is covering expenses for travel, accommodation, conference fees, and meals. Any extra funds will support current development projects in decision-making, scientific research, and artistic endeavors.
            """

    if st.session_state['authentication_status']:
        st.toast(f'Authenticated successfully {mask_string(st.session_state["username"])}')
        col1, col2, col3 = st.columns([1, 9, 1])
        with col2:
            from email_validator import EmailNotValidError, validate_email
                    
            st.markdown("""
        ### We're excited that you are interested in joining our initiative. 
        
        As we consolidate a focused and passionate community, sharing your email facilitates communication and collaboration.
                    """)
            email = survey.text_input("Your email address", id="Email")
            if email:
                try:
                    valid = validate_email(email)
                    email = valid.email
                except EmailNotValidError as e:
                    st.error(str(e))
                name = survey.text_input("Your name", id="given-name")
                if name:
                    st.write(f"Thank you `{name}` for your interest. We will get back to you shortly.")

        st.write(f'`Your signature is {mask_string(st.session_state["username"])}`')
    elif st.session_state['authentication_status'] is False:
        st.error('Access key does not open')
    elif st.session_state['authentication_status'] is None:
        authenticator.login('Connect', 'main', fields = fields_connect)
        st.warning('Please use your access key')

def datacollection():

    st.markdown("## <center> Step 3: Changing perspectives</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """
Two aspects are key for us:
"""
        )
        """
        1. **Transparency:** Regularly update donors, contributors, and investors on how their resources are being used.

2. **Acknowledgements:** Recognising and thanking donors for their support, detailing the outcomes and benefits of the donations.
        """
        
        """
        **Remark:** 
As we proceed, we will store your information in two separate databases: a 'trusted' one for verified data and an 'untrusted' one for data that needs further validation. This helps us ensure accuracy and transparency in our actions, while exploring the dynamics of trust and value in a digital environment.
        One of the two databases of choice is a simple **_relational_ database**, the other is a **banking ledger**.
        """
    st.toast(
        """Side Note:
Why should the banking ledger be _trusted_? The information we seek will be encoded in a transaction, ensuring transparency and integrity."""
    )
    
def story():
    # st.write(st.session_state)
    st.markdown("## <center> Step 4: Personal Story</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """
We're curious to learn more about the individuals behind these decisions. Your story matters and contributes to the richness of this journey, as a collective.
What is your story?
"""
        )
    col1, col2, col3 = st.columns([2, 6, 1], vertical_alignment="center")
    custom_profile = False
    
    with col2:
        if st.toggle("Custom profile", key="custom_profile"):
            """(Feel free to share as much or as little as you like.)"""
            custom_profile = True
            profile_text = survey.text_area("Enter your custom profile:", key="custom_profile_text")
            st.session_state["profile"] = None         

    if not custom_profile: 
        show_pathways(philanthropic_profiles, cols=1)

    col1, col2, col3 = st.columns([2, 6, 1], vertical_alignment="center")
    # if st.session_state["profile"] is not None:
    if st.session_state["profile"] is not None and not custom_profile:
        with col2:
            st.write(list(philanthropic_profiles.items())[st.session_state['profile']-1][1]["description"])    
        
        with col3:  
            st.markdown('# ' + f"{list(philanthropic_profiles.items())[st.session_state['profile']-1][1]['icon']}") 

        st.markdown('### #' + f'{list(philanthropic_profiles.items())[st.session_state["profile"]-1][0]}') 
        
def preferences():
    st.markdown("## <center> Step 5: Participation and Expression</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """

If philanthropy is your choice to connect and engage, join us at the upcoming _Europe in Discourse_ conference. It's the perfect opportunity to further our engagement and see how your actions translate into real-world impact.
        """
        )
        """
        
        To gauge your interests and align our efforts, we invite you to participate in a brief interactive exercise. 
        
        The sliders represent different areas of our project, such as decision-making, science, arts, and events. 
        
        By adjusting the sliders, express your level of interest or engagement in each category.
        
        """
        
        # st.write(engage)
        equaliser_data = [
            ("Decision Making", ""),
            ("Science", ""),
            ("Arts", ""),
            ("Events", ""),
            ]

        create_equaliser(key = "equaliser", id= "equaliser", kwargs={"survey": survey, "data": equaliser_data})
        """
        Your input helps us better understand which aspects of our initiative resonate with you and ensure that your philanthropic contributions are directed towards areas that are most meaningful to you.
                """

def donation():
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:

        st.markdown("## <center> Step X: Access / IF DONATION</center>", unsafe_allow_html=True)
        """
        ### **Donation Options:**
        - **Custom Donation:** Allows you to pick your preferred number.
        - **:material/coffee: :** "Sponsor a Coffee for the collective" – 17 EUR
        - **:material/restaurant: :** "Cover a Light Lunch or Part of Dinner" – 100 EUR
        - **:material/hotel::** "Support Our Accommodation" – 1000 EUR
        - **:material/jump_to_element: :** "Support Our Travels" – 1111 EUR


        """
        # Define the icons and labels for the buttons
        options = {
            'A Coffee': {'amount': '17', 'icon': ':material/coffee:'},
            'Partial Dinner': {'amount': '100', 'icon': ':material/restaurant:'},
            'Partial Accommodation': {'amount': '1000', 'icon': ':material/hotel:'},
            'Partial Travel': {'amount': '0', 'icon': ':material/jump_to_element:'}
        }

        # Create three columns

        # if st.button("Custom Donation", type="primary", help="Click to enter a custom donation amount", 
        #              use_container_width=True, on_click=lambda: st.session_state.update(custom_donation=True)):
        custom_donation = st.toggle("Custom Donation", key="custom_donation",)
        if not custom_donation:
                    #  on_change=lambda: st.session_state.update(custom_donation=True)):
            col1, col2, col3, col4 = st.columns(4)

            # Add buttons in each column
            with col1:
                if survey.button(label = f"{options['A Coffee']['icon']} •", id="coffee"):
                    st.write("Thank you for supporting us with a coffee!")
                    
            with col2:
                if survey.button(label = f"{options['Partial Dinner']['icon']} •", id="dinner"):
                    st.write("Thank you for covering part of the dinner!")

            with col3:
                if survey.button(label = f"{options['Partial Accommodation']['icon']} •", id="accommodation"):
                    st.write("Thank you for supporting our accommodation!")
            with col4:
                if survey.button(label = f"{options['Partial Travel']['icon']} •", id="travel"):
                    st.write("Thank you for supporting our travels!")
        
        else:
            st.session_state.custom_donor = True

            st.write("Thank you for your generous intention!")
            
            # Exponential slider
        if st.session_state.custom_donor:
            min_exp_value = 0
            max_exp_value = 5
            min_actual_value = 1
            max_actual_value = 100000-0.1

            exp_value = survey.slider(label = "Sensitive Slider",
                                      id = "custom_donation_slider", 
                                      min_value=float(min_exp_value), max_value=float(max_exp_value), value=float(min_exp_value),
                                    step = 0.01,
                                    format="%d")

            # Convert exponential value to actual value
            actual_value = exp_to_actual(exp_value)+0.1

            # Display the actual type: exp_value if actual value < 3000, otherwise -1
            donation_type = lambda x, t: int(x)+10 if t < 3000 else -1
            # st.write(f"Donation Value: {actual_value:.1f} EUR, Donation type: {int(exp_value)}")
            st.write(f"Donation Value: {actual_value:.1f} EUR, Donation type: {donation_type(exp_value, actual_value)}")

def investment(survey):
    st.title("Investment Opportunity Overview")
    
    with st.expander("Investment Opportunity Introduction", expanded=False):
        st.markdown("## Introduction")
        st.write("Explore a unique investment opportunity designed to redefine your approach to returns. "
                "Our investment protocol allows you to set both an 'expected' and a 'dream' return rate, "
                "offering a personalized and attainable financial goal.")

        st.markdown("## Key Features")
        st.subheader("Expected Return Rate")
        st.write("- **Definition:** Baseline return on investment over a fixed time span.")
        st.write("- **Purpose:** Conservative estimate of return without active involvement.")
        st.write("- **Your Role:** State your desired expected return rate.")

        st.subheader("Dream Return Rate")
        st.write("- **Definition:** Ambitious return rate aligned with personal wishes.")
        st.write("- **Purpose:** Express your ideal financial outcome.")
        st.write("- **Your Role:** Share your dream return rate.")

        st.subheader("Intermediate Value")
        st.write("- **Proposal:** Bridge between expected and dream return rates.")
        st.write("- **Strategy:** Carefully planned investments for balance.")
        st.write("- **Risk Management:** Approach includes risk management.")

        st.markdown("## Process")
        st.write("1. **Set Rates:** Clearly define expected and dream return rates.")
        st.write("2. **Receive Proposal:** Analysis for an attainable intermediate value.")
        st.write("3. **Investments:** Benefit from a curated investment plan.")
        st.write("4. **Review:** Regular reviews for adapting to changes.")

        st.markdown("## Why Us")
        st.write("- **Innovation:** Tailored and flexible investment experience.")
        st.write("- **Transparency:** Clear understanding of the investment process.")
        st.write("- **Expertise:** Backed by a team of financial experts.")

        st.markdown("## Next Steps")
        st.write("Seize this investment opportunity tailored to your financial aspirations. "
                "Set your expected and dream return rates today to embark on a journey towards financial success.")
        st.write("Contact us for more details and personalized assistance.")
        st.title("Investment Opportunity Overview")

    st.markdown("## First Steps")
    st.write("Seize this investment opportunity tailored to your financial aspirations. "
            "Set your expected and dream return rates today to embark on a journey towards financial success.")
    st.write("Contact us for more details and personalized assistance.")

    option = survey.radio("Select how you want to express return rates:",
                            options = ("Percentage", "Leverage Factor", "Mixed mode"), horizontal=True)

    col1, _spacer, col2= st.columns([3,1,3], vertical_alignment="center")
    _spacer.markdown("# vs.")
    if option == "Percentage":
        col1.markdown("## Expected Return Rate (Percentage)")
        expected_return_rate = survey.number_input("Enter your expected return rate (%):", min_value=0.0, step=1.)
        col2.markdown("## Dream Return Rate (Percentage)")
        dream_return_rate = survey.number_input("Enter your dream return rate (%):", min_value=0.0, step=1.)
    elif option == "Leverage Factor":
        col1.markdown("## Expected Return Rate (Leverage Factor)")
        expected_return_rate = col1.number_input("Enter your expected leverage factor:", min_value=0, step=1)
        col2.markdown("## Dream Return Rate (Leverage Factor)")
        dream_return_rate = col2.number_input("Enter your dream leverage factor:", min_value=1, step=1)
    else:
        col1.markdown("## Expected Return Rate (Percentage)")
        expected_return_rate = col1.number_input("Enter your expected return rate (%):", min_value=0.0, step=1.)
        col2.markdown("## Dream Return Rate (Leverage Factor)")
        dream_return_rate = col2.number_input("Enter your dream leverage factor:", min_value=1, step=1)
    
    with st.expander("Investment Opportunity Overview", expanded=False):

        st.divider()

        st.markdown("## Introduction")
        st.write("Explore a unique investment opportunity designed to redefine your approach to returns. "
                "Our investment protocol allows you to set both an 'expected' and a 'dream' return rate, "
                "offering a personalized and attainable financial goal.")

        st.markdown("## Key Features")
        st.subheader("Expected Return Rate")
        st.write("- **Definition:** Baseline return on investment over a fixed time span.")
        st.write("- **Purpose:** Conservative estimate of return without active involvement.")
        st.write("- **Your Role:** State your desired expected return rate.")

        st.subheader("Dream Return Rate")
        st.write("- **Definition:** Ambitious return rate aligned with personal wishes.")
        st.write("- **Purpose:** Express your ideal financial outcome.")
        st.write("- **Your Role:** Share your dream return rate.")

        st.subheader("Intermediate Value")
        st.write("- **Proposal:** Bridge between expected and dream return rates.")
        st.write("- **Strategy:** Carefully planned investments for balance.")
        st.write("- **Risk Management:** Approach includes risk management.")

        st.markdown("## Process")
        st.write("1. **Set Rates:** Clearly define expected and dream return rates.")
        st.write("2. **Receive Proposal:** Analysis for an attainable intermediate value.")
        st.write("3. **Investments:** Benefit from a curated investment plan.")
        st.write("4. **Review:** Regular reviews for adapting to changes.")

        st.markdown("## Why Us")
        st.write("- **Innovation:** Tailored and flexible investment experience.")
        st.write("- **Transparency:** Clear understanding of the investment process.")
        st.write("- **Expertise:** Backed by a team of financial experts.")


        st.markdown("## Summary")
        if option == "Percentage":
            st.write("Your expected return rate:", expected_return_rate, "%")
            st.write("Your dream return rate:", dream_return_rate, "%")
        elif option == "Leverage Factor":
            st.write("Your expected leverage factor:", expected_return_rate)
            st.write("Your dream leverage factor:", dream_return_rate)
        else:
            st.markdown("## Expected Return Rate (Percentage)")
            st.write("Your expected return rate:", expected_return_rate, "%")
            st.write("Your dream leverage factor:", dream_return_rate)

def offer():
    st.markdown("## <center> Step X: Investment horizon</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """

"""
        )
        risk_tolerance = survey.radio("Risk Appetite:", options=["Low", "Medium", "High"], horizontal=True, key="risk_appetite", captions=["Play it safe in maze", "Play like an adventure", "Play like a pro"])
    investment(survey)

def contribution():
    st.markdown("## <center> Step X:  / IF SUPPORT</center>", unsafe_allow_html=True)
    """
    In Kind or Economic Contribution
    """
    
    """For example, I have a restaurant, come eat at my venue
    I'm happy to feed your ideas
    
    I'm happy to offer a room in my hotel
    
    a disposizione asset e non solo denaro"""
    # col1, col2, col3 = st.columns([1, 9, 1])
    
def reading():
    # with col2:
    st.markdown("## <center> Step X: Did we get it?</center>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.write(dataset_to_text(survey.data, perspective='third'))


    if st.session_state['profile'] is not None and not st.session_state.toast:
        id = st.session_state['profile']
        st.toast("#"+ list(philanthropic_profiles.keys())[id-1])
        st.toast(list(philanthropic_profiles.items())[id-1][1]['description'])
        st.session_state.toast = True
        # profile = survey.button("This is my profile", 
        #             type="primary",
        #             key=f"profile_button", 
        #             help="Click to pick this profile", 
        #             use_container_width=True)       


    st.markdown("## <center> Connect and Commit</center>", unsafe_allow_html=True)
    st.markdown(
"""
We aim at _covering expenses_, however - in case of any surplus funds, _we invite_ donors to participate in a future initiative, following the project's progress."""
    )
    

    """
    To encode meaningful information, we use short code that make it easy for us to perform automated accounting,
    sophisticated data analysis, and pattern recognition - in a transparent way.
    
    This is to encode the key details of this session in a compact and meaningful way.
    """
    tx_tag, (tier, type_value, donation_type), qualitative_value, _ = extract_info(survey.data)
    st.markdown(f"# <center>Short code: `SCFS{tx_tag}`</center>", unsafe_allow_html=True)
    # " + '•' + '<code>' + str(st.session_state["username"]) + "</code>
    # st.write(st.session_state["username"])
    # st.write(extract_info(survey.data))
    with st.expander("What does this code mean?", expanded=False):
        """
        We format codes as follows:
        """
        st.markdown("# <center> SCFS XX YY Z - P</center>", unsafe_allow_html=True)
        """
        where:

            •	SCFS stands for Social Contract From Scratch.
            •	XX represents the engagement type: whether you chose 
                        to support, invest, or donate.
            •	YY indicates the tier: options include coffee, food, 
                        accommodation/travel, or custom.
            •	Z reflects the interest level: either high or low.
            •	P corresponds to your philanthropic profile.

        Do you have any suggestions for improvement or questions about the code?
        Drop us a message, we are happy to hear from you.
        
        <social.from.scratch@proton.me>
    """
    
    st.session_state["tx_tag"] = f"SCFS{tx_tag}"
    
    return f"SCFS{tx_tag}"

def price():
    tx_tag, (tier, type_value, donation_type), qualitative_value, _ = extract_info(survey.data)
    
    base = 10 if qualitative_value == "2" else 1 if qualitative_value == "1" else 11 if qualitative_value == "10" else 100
    # base = qualitative_value
    # base = 1

    price = float(f"{base}.{convert_string_to_decimal(tx_tag)}")
    st.session_state["price"] = price
    st.markdown(f" # _Price_, commitment, or _value_?") 
    """
    We not only store your data securely in our database, but we also encode it into numbers that are recorded on a bank ledger. 
    
    This dual method ensures both transparency and accountability, while safeguarding your information. 
    
    This is the number we came up with, for you:
    """
    st.markdown(f"# <center> {price}<center>", 
                unsafe_allow_html=True)
    """
    Encoding the data on the bank ledger, in EUR currency, serves as a _relatively_ secure, _almost_ immutable record of your engagement, offering an additional layer of verification and trust.
    
    To this end, we use the smallest possible units of currency to encode the type of commitment you have made, and the decimal digits to capture other relevant information.
    """
    st.toast(f"When price conceals value, what is money, anyways? ")
    
    with st.expander("What does this number mean?", expanded=False):
        f"""
        We use numbers to encode information about your commitment. This number is then used to create a transaction that reflects your parameters.
        To make a step forward, these simple but key informations are encoded numerically into a two-digits number `xx`, where `xx` in this case equals **{convert_string_to_decimal(tx_tag)}**.
        """

        f"""
        
        This number (`xx`) is appended to another number to form a transaction code of the type **1.**`xx` EUR if SUPPORT, **10.**`xx` if INVESTMENT, **11**.`xx` if DONATION, **100.**`xx` OTHERWISE. 
        
        This serves to securely link the data _within_ the transaction itself. By embedding this information in the transaction amount, it creates a verifiable record on the ledger, ensuring that the encoded data remains tamper-proof and directly tied to your intention. 
        
        This method not only protects the integrity of the data but also provides transparency, allowing anyone to attempt tracing the encoded details back to the transaction.
        
        In this way, we can perform very sophisticated data analysis and pattern recognition, _transparently_, while ensuring the privacy and security of the data.
        """

def checkout():
    st.markdown("## <center> Step X: Create digital trace</center>", unsafe_allow_html=True)
    st.markdown(
"""
    For this, we need your signature
""")
    if st.session_state['sumup'] is not None:
        st.info("Authorisation successful!")
    else:
        authenticator.login('Connect', 'main', fields = fields_connect)
        st.warning("We are integrating _money_ into the game. This requires your authorisation.")

    if st.session_state['authentication_status']:
        st.write(f'Authenticated: {st.session_state["authentication_status"]}')
    
    if st.session_state["username"] is not None:
        signature = mask_string(st.session_state["username"])
    else: 
        """
        It looks like you haven't signed in yet.
        We haven't been able to find your key signature. Please, connect using the form above or  enter your access key below.
        """
        # if st.button("Connect", type='primary', key="connect", help="Connect to the platform", use_container_width=True):
            # pages.current = "Connect"
        _signature = st.text_input("Enter your access key:", key="signature")
        signature = mask_string(_signature)
        
    st.markdown(f"### <center> My signature is `{signature}`</center>", unsafe_allow_html=True)
    
    # st.markdown("Confirm with a glance.")
    import streamlit.components.v1 as components
    from requests.exceptions import RequestException
    from sumup_oauthsession import OAuth2Session

    base_url = "https://api.sumup.com/"
    redirect_uri = "https://individual-choice.streamlit.app/"

    # st.markdown("## We connect to payment channels")
    # print authorisation status

    st.write("Click the link below to authorise _payments_. Your authorisation is key to proceed. If everything is in order, you will read above a message of success, or a unique ID below.")
    if st.button("It is OK to bring money into the game", type='primary', key="authorise", use_container_width=True, disabled=not bool(st.session_state['authentication_status'])):
        try:
            sumup = OAuth2Session(
                base_url=base_url,
                client_id=st.secrets["sumup"]["CLIENT_ID"],
                client_secret=st.secrets["sumup"]["CLIENT_SECRET"],
                redirect_uri=redirect_uri,
            )

            st.write('Authorisation #' + sumup.state)
            st.session_state['sumup'] = sumup
        except RequestException as e:
            st.error(f"An error occurred during authorization: {e}")
        except KeyError as e:
            st.error(f"Missing configuration for {e}. Please check your secrets.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    # st.markdown("Click the expand button below to know more about the payment mechanics.")
    with st.expander("Payments and ledger", expanded=False):
        st.write("The payment data is stored in your session's _state_ and can be accessed by your end for further processing. On _this_ end, we use the SumUp API (sumup.com) to create checkouts and process payments. Finally, we rely on CCF bank, a French commercial bank founded in 1894 and acquired by HSBC in 2000, as the (_untrusted_) ledger.")
    
    
def checkout2():

    description = "Social Contract from Scratch•"
    signature = st.session_state["username"] 
    reference = st.session_state["tx_tag"]
       
    # _signature = "77868affa87ca77cdeb146c89593bac64ec6dd2ee7265dfeec61941d87529845"

    @st.dialog("Full Signature")
    def _show_sig():
        st.write(st.session_state["username"])
    # if st.button('Show full signature', type='primary', on_click=lambda: _show_sig):
        # st.write(f'Full signature {_signature}')
        
        
    st.markdown(f'# <center> Commit # {st.session_state["price"]}</center>', unsafe_allow_html=True)
    st.markdown(f"### Commit reference: {reference}", unsafe_allow_html=True)
    st.markdown(f"### Commit signature: {signature}", unsafe_allow_html=True)
    """
    The button below will create a record to be verified on the ledger. This entry will be a trace of your commitment, a digital footprint of your intention and action.
    """
    if st.button("Create record", type='primary', key="checkout", help="Record a trace on the ledger", use_container_width=True, disabled=not bool(st.session_state['sumup'])):
        with st.spinner("Creating record..."):
            st.write(reference)
            reference = reference+f"-{int(now.strftime('%S'))}"
            time.sleep(1)
            st.write(f"Full reference {reference}. (computed as a function of the current time)")
        checkout = create_commit_checkout(reference, st.session_state["price"], description + signature)
        # if checkout:
            # st.json(checkout)

    st.write("Commits:")
    if st.button("List commits", key="list_checkouts", use_container_width=True):
        if len(st.session_state['checkouts']) == 0:
            st.warning("There is nothing to commit, yet.")
            
        else:
            st.json(st.session_state['checkouts'])    

    for checkout in st.session_state['checkouts']:
        if st.button(f"Get Commit Info for {mask_string(checkout)}", key=f"checkout_info_{checkout}", type='primary', use_container_width=True):
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                checkout_info = get_checkout_info(checkout)
                # st.json(checkout_info)
                st.write(f"**Amount:** {checkout_info['amount']} {checkout_info['currency']}")
                st.write(f"**Checkout Reference:** {checkout_info['checkout_reference']}")
                st.write(f"**Date:** {checkout_info['date']}")
                st.write(f"**Description:** {checkout_info['description']}")
                st.write(f"**Transaction ID:** {checkout_info['id']}")
                st.write(f"**Merchant Country:** {checkout_info['merchant_country']}")
                st.write(f"**Merchant Name:** {checkout_info['merchant_name']}")
                st.write(f"**Status:** {checkout_info['status']}")


    """
    Let's save essential data (e.g., preferences, ideas, initial information) before the payment to ensure nothing is lost if the payment fails (some will _indeed_ fail!). 
    
    """
    return

def integrate():
    reference = st.session_state["tx_tag"]
    _signature = st.session_state["username"]
    
    st.markdown("## <center> Step X: Integrate the data</center>", unsafe_allow_html=True)
    
    csv_filename = f"my_philanthropic_question_map_1_{reference}.data"
    with st.expander("Show the data", expanded=False):
        st.json(survey.data)


    if st.download_button(label=f"Download datafile", use_container_width=True, data=json.dumps(survey.data), file_name=csv_filename, mime='text/csv', type='primary'):
        st.success(f"Saved {csv_filename}")
    """
    ### How do we store the data? 
    """
    st.markdown(
    """
    The data you provide is stored in two databases. These two sources provide a complementary snapshot of your intention and action, like _two halves_ of a digital trace of your session.
    """
    )
    """
    Each of the buttons below (if any) correspond to a specific commitment. Clicking on a button will integrate yours into our lightweight database.
    """
    if st.button(f":material/sunny:", key=f"commit", help=f"Commit", use_container_width=True):
        _submit(survey.data, _signature)
        
    """
    After successful _ledger_ commitment, we shall update and refine our sources with confirmation details and additional secure information.
    """
    st.title("Signal the ledger")
    
    # st.write(f"Full signature: {_signature}")
    # st.write(f"Full username: {st.session_state['username']}")
    # st.markdown("# :material/barefoot:, :material/rainy_snow:, :material/online_prediction:, :material/alarm_off:, :material/award_star:, :material/draw:,  :material/step_out:")
    st.markdown(dataset_to_intro(survey.data))
    """
    Each of the buttons below (if any) correspond to a specific commitment. Clicking on a button will integrate yours, writing into the ledger's _records_.
    """
    for checkout in st.session_state['checkouts']:
        if st.button(f":material/rainy_snow:", key=f"pay-{checkout}", help=f"{checkout}", use_container_width=True):
            sumup_widget(checkout)
            
    # st.write(survey.data)
    
    if st.button(f"Clear all and restart", key=f"restart", type='primary', use_container_width=True):
        st.session_state.clear()
        st.rerun()

def application_pages():
    pages_total = 16
    pages = survey.pages(pages_total, 
            on_submit=lambda: _submit(),
            )
    st.progress(float((pages.current + 1) / pages_total))
    
    with pages:
        if pages.current == 0:
            body1()

        if pages.current == 1:
            body2()

        if pages.current == 2:
            engagement()

        if pages.current == 3:
            question()
        if pages.current == 4:
            access()
        if pages.current == 5:
            authentication()
        if pages.current == 6:
            datacollection()
        if pages.current == 7:
            story()
        if pages.current == 8:
            preferences()
        if pages.current == 9:
            if survey.data["Qualitative"]["value"] == "10":
                donation()
            elif survey.data["Qualitative"]["value"] == "2":
                offer()
            elif survey.data["Qualitative"]["value"] == "1":
                contribution()       
            else:
                st.write("Please select an philanthropy option that suits to you.")     
                with st.spinner("Loading..."):
                    import time
                    time.sleep(3)
                    pages.current = 2
                    st.rerun()
        if pages.current == 10:
            reading()

        if pages.current == 11:
            price()
            
        if pages.current == 12:
            checkout()

        if pages.current == 13:
            checkout2()

        if pages.current == 14:
            integrate()
                

if __name__ == "__main__":
    
    st.markdown("# <center>The Social Contract from Scratch</center>", unsafe_allow_html=True)
    st.markdown("## <center>The intersection of Human and Natural Sciences, Philosophy, and Arts.</center>", unsafe_allow_html=True)
    # st.markdown('<center>`wait a minute`</center>', unsafe_allow_html=True)
    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}")
    st.divider()
    st.markdown(f"# <center>Philanthropy Application</center> ", unsafe_allow_html=True)

    if st.session_state['authentication_status']:
        event = st_player("https://vimeo.com/1002366658", key='vimeo_player')
    else:
        st.markdown("### <center>_Log in to preview._</center>", unsafe_allow_html=True)
    
    application_pages()
