import streamlit as st

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

from streamlit_extras.row import row

import yaml
from yaml import SafeLoader
import philoui
from datetime import datetime
from philoui.io import conn, QuestionnaireDatabase as IODatabase
from philoui.io import create_qualitative, create_dichotomy, create_equaliser
from philoui.survey import CustomStreamlitSurvey
import streamlit_shadcn_ui as ui
import pandas as pd
from streamlit_extras.add_vertical_space import add_vertical_space 
from streamlit_extras.row import row


with open("assets/discourse.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.write(f.read())
    
with open('assets/credentials.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    now = datetime.now()
    # st.markdown(f"`Now is {now.strftime('%s')}-{now.strftime('%f')}~` max is {st.session_state.range if st.session_state.range else ''}")

if 'alerted' not in st.session_state:
    st.session_state.alerted = False

if 'profile' not in st.session_state:
    st.session_state.profile = None

# @st.dialog("What is your story?", width="small")

def handle_callback(id):
    st.session_state["current_pathway"] = id

    if "profile" not in st.session_state:
        st.session_state["profile"] = None

    st.toast(f"profile {st.session_state['profile']}")


def vote_callback(id):
    st.write(list(philanthropic_profiles.keys())[id-1])
    st.write(list(philanthropic_profiles.items())[id-1][1]['description'])
    st.session_state["profile"] = id
    st.markdown(id)

    if "profile" not in st.session_state:
        st.session_state["profile"] = None

    if "toast" not in st.session_state:
        st.session_state["toast"] = False

    st.toast(f"profile {st.session_state['profile']}")

    if st.button("This is my profile", 
                 type="primary",
                key=f"vote_button_{id}", 
                help="Click to vote for this pathway", 
                use_container_width=True):

        st.session_state["profile"] = id
        st.toast(f"Your profile id {id}")
        st.toast(f"Your session profile id {st.session_state["profile"]}")
        
philanthropic_profiles = {
'Communitarian': {
    'description': '## **Doing good** makes sense for the community. Your contributions create ripple effects that strengthen social bonds and uplift those around you.',
    'icon': ':material/group:'
},
'Devout': {
    'description': '## **Doing good** is the will of a higher power. Your philanthropy is a sacred duty, a way to serve and fulfill your spiritual obligations.',
    'icon': ':material/auto_awesome:'
},
'Investor': {
    'description': '## **Doing good** is good business. You see philanthropy as an investment, generating returns not just for society, but for the world at large.',
    'icon': ':material/monetization_on:'
},
'Socialite': {
    'description': '## **Doing good** is sexy. Your generosity is a symbol of status and influence, making waves in social circles while benefiting the greater good.',
    'icon': ':material/party_mode:'
},
'Repayer': {
    'description': '## **Time to give back**. You have received much from society, and now it’s your turn to return the favor and support the next generation.',
    'icon': ':material/replay:'
},
'Dynast': {
    'description': '## **Following family tradition**. Philanthropy is in your blood, a legacy passed down through generations, and you proudly carry the torch.',
    'icon': ':material/family_restroom:'
},
'Altruist': {
    'description': '## **Giving from the heart**. Your generosity knows no bounds; you give selflessly and with deep compassion, driven by a love for humanity.',
    'icon': ':material/favorite:'
},
'Indifferent': {
    'description': '## **I don\'t give a shit about** philanthropy or social causes. You believe that everyone should fend for themselves, and you see no reason to contribute.',
    'icon': ':material/block:'
},
'Deflector': {
    'description': '## **It\'s somebody else\'s problem**. You believe that social issues and philanthropy are for others to worry about, not your concern or responsibility.',
    'icon': ':material/warning:'
}
}  
def show_pathways(list, cols=3):
    links_row = row(len(list)//cols, vertical_align="center")
    
    st.session_state["current_pathway"] = None
    
    # st.write(f"current_pathway {st.session_state["current_pathway"]}")

    for id, (pathway, details) in enumerate(list.items(), start=1):
        icon = details['icon']
        description = details['description'] 

        button_text = f"{icon}"
        links_row.button(button_text, help=description, key=id, 
                         on_click = vote_callback, args = ((id),))
    
    st.write('''<style>
        [data-testid="stVerticalBlock"] [data-testid="baseButton-secondary"] p {
            font-size: 4rem;
            padding: 1rem;
        }
        [data-testid="stVerticalBlock"] [data-testid="baseButton-secondary"][aria-pressed="true"] {
            border: 5px solid #FF5733;
            box-shadow: 0px 0px 10px 2px #FF5733;
        }
    </style>''', unsafe_allow_html=True)
        
    # write current profile
    st.write(f"profile {st.session_state['profile']}")


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

    with st.expander("Investment Opportunity Overview", expanded=False):
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

def body():
    st.divider()
    st.markdown("# <center> Step 0:  / Awareness</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        """
    Let’s jump on the auction side of this philanthropic journey. This will be a digital application which we build on top of our streamlet framework. It is intended to stimulate an action, commit a decision, populate a database, engage and interact.

    """
    
        """ 
    It's a process in several steps.

First question is served after a pause. This process will take approximately 10 minutes take at moment take a moment one minute to reflect on your motivation.
    """
    st.markdown("# <center> Step 1:  / Reflection</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])

    with col2:
        st.markdown("""
        Take a moment, approximately one minute, to reflect on your motivation for participating in this journey. This process will guide your actions and decisions over the next 10 minutes.
    """)

    st.markdown("# <center> Step 2: Engagement</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    
    with col2:
        st.markdown(
        """
        Have you ever found the key out of the portal?
        """
        )
        """
        
        We are populating the table of our shared elementary values, would you like to play
?   """

    st.markdown("# <center> Step 2: Engagement</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """
we are populating the table of our shared elementary values. This is more than just a GAME. It is a collective discovery process.
Would you like to play?
"""
        )

    st.markdown("# <center> Step 3: Data Collection</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """
As we proceed, your decisions and actions will be stored in two different databases—one trusted and one untrusted. This distinction allows us to explore the dynamics of trust and value in a digital environment.
"""
        )
    st.toast(
        """Side Note:
Why is the banking ledger trusted? The information we seek will be encoded in a transaction, ensuring transparency and integrity."""
    )

    st.markdown("# <center> Step 4: Step 4: Personal Story / profile</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """
We’re curious to learn more about the individuals behind these decisions. Your story matters and contributes to the richness of this collective journey.
What is your story?
(Feel free to share as much or as little as you like.)
"""
        )
    st.markdown("# <center> Step 5: Invitation / xxx</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """

If philanthropy is your choice to connect and engage, we invite you to join us at our next event, the European Discourse Conference. It’s the perfect opportunity to further your engagement and see how your actions translate into real-world impact.
This structured journey is designed to engage participants on multiple levels—emotionally, intellectually, and socially—while ensuring that their contributions are meaningful and impactful. The combination of reflection, interaction, and data-driven engagement sets the stage for a unique and transformative experience.
"""
        )
        survey = CustomStreamlitSurvey()
        engage_categories= {'1': 'Support', '2': 'Invest', '10': 'Donate'}
        engage = create_qualitative('trifurcation',
                           kwargs={"survey": survey, 
                                   'label': 'categorical', 
                                    "name": "we are at a crossing point.",
                                    "question" : "Support, Invest, or Donate?",
                                    
                            })
        feedback_messages = {
            '1': "I have chosen to **Support** our initiative. Your backing is essential in helping us move forward.",
            '2': "I have chosen to **Invest** in our vision. Your investment will help us consolidate and expand our impact.",
            '10': "I have chosen to **Donate** to our cause. Your generosity makes a significant difference."
}
        if engage is not None:
            st.write(feedback_messages.get(str(engage), "Thank you for your dedication so far!"))

        # st.write(engage)
        create_dichotomy(key = "executive", id= "executive",
                                            kwargs={'survey': survey,
                                                'label': 'resonance', 
                                                'question': 'Click to express your viewpoint: the gray area represents uncertainty, the extremes: clarity.',
                                                'gradientWidth': 20,
                                                'height': 250,
                                                'title': '',
                                                'name': 'intuition',
                                                'messages': ["Yes, it's a good idea", "No, it's not a good idea", "I'm not sure"],
                                                # 'inverse_choice': inverse_choice,
                                                'callback': lambda x: ''})
        equaliser_data = [
            ("Decision Making", ""),
            ("Science", ""),
            ("Arts", ""),
            ("Events", ""),
            ]

        create_equaliser(key = "equaliser", id= "equaliser", kwargs={"survey": survey, "data": equaliser_data})
    
        st.markdown("# <center> Step X: Access / IF DONATION</center>", unsafe_allow_html=True)
        """
        ### **Donation Options:**
        - **Button 1:** "Offer a Coffee" – 17 EUR
        - **Button 2:** "Cover a Light Lunch or Part of Dinner" – 100 EUR
        - **Button 3:** "Support Our Accommodation" – 1000 EUR
        - **Button 4:** "Support Our Travels" – 1111 EUR
        - **Custom Donation:** Allows you to pick your preferred number.


        """
        # Define the icons and labels for the buttons
        options = {
            'A Coffee': {'amount': '17', 'icon': ':material/coffee:'},
            'Partial Dinner': {'amount': '100', 'icon': ':material/restaurant:'},
            'Partial Accommodation': {'amount': '1000', 'icon': ':material/hotel:'},
            'Partial Travel': {'amount': '0', 'icon': ':material/flight_takeoff:'}
        }

        # Create three columns
        col1, col2, col3, col4 = st.columns(4)

        # Add buttons in each column
        with col1:
            if st.button(f"{options['A Coffee']['icon']} •"):
                st.write("Thank you for supporting us with a coffee!")
                
        with col2:
            if st.button(f"{options['Partial Dinner']['icon']} •"):
                st.write("Thank you for covering part of the dinner!")

        with col3:
            if st.button(f"{options['Partial Accommodation']['icon']} •"):
                st.write("Thank you for supporting our accommodation!")
        with col4:
            if st.button(f"{options['Partial Travel']['icon']} •"):
                st.write("Thank you for supporting our accommodation!")
        
        if st.button("Custom Donation",type="primary", help="Click to enter a custom donation amount", use_container_width=True):
            st.write("Thank you for your generous donation!")
        
        # Define the range of values for the exponential slider
        
        min_exp_value = 0
        max_exp_value = 5
        min_actual_value = 1
        max_actual_value = 100000

        # Convert exponential value to actual value
        def exp_to_actual(value):
            return 10**value
            return min_actual_value * (max_actual_value / min_actual_value) ** ((value - min_exp_value) / (max_exp_value - min_exp_value))

        # Exponential slider
        exp_value = survey.slider("Exponential Slider", min_value=float(min_exp_value), max_value=float(max_exp_value), value=float(min_exp_value),
                                  step = 0.01,
                                  format="%d")

        # Convert exponential value to actual value
        actual_value = exp_to_actual(exp_value)

        # Display the actual type: exp_value if actual value < 3000, otherwise -1
        _display = lambda x, t: int(x)+10 if t < 3000 else -1
        st.write(f"Donation Value: {actual_value:.1f} EUR, Donation type: {int(exp_value)}")
        st.write(f"Donation Value: {actual_value:.1f} EUR, Donation type: {_display(exp_value, actual_value)}")

    
    st.markdown("# <center> Step X: Access / IF INVESTMENT</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown(
        """

"""
        )
        risk_tolerance = survey.radio("Risk Appetite:", options=["Low", "Medium", "High"], horizontal=True, key="risk_appetite", captions=["Play it safe through the maze", "Play like adventure", "Play like a pro"])
    investment(survey)

    st.markdown("# <center> Step X: Example reading / xxx</center>", unsafe_allow_html=True)
    st.json(survey.data)

    philanthropic_profiles = {
    'Communitarian': {
        'description': '### **Doing good** makes sense for the community. Your contributions create ripple effects that strengthen social bonds and uplift those around you.',
        'icon': ':material/group:'
    },
    'Devout': {
        'description': '### **Doing good** is the will of a higher power. Your philanthropy is a sacred duty, a way to serve and fulfill your spiritual obligations.',
        'icon': ':material/auto_awesome:'
    },
    'Investor': {
        'description': '### **Doing good** is good business. You see philanthropy as an investment, generating returns not just for society, but for the world at large.',
        'icon': ':material/monetization_on:'
    },
    'Socialite': {
        'description': '### **Doing good** is sexy. Your generosity is a symbol of status and influence, making waves in social circles while benefiting the greater good.',
        'icon': ':material/party_mode:'
    },
    'Repayer': {
        'description': '### **Time to give back**. You have received much from society, and now it’s your turn to return the favor and support the next generation.',
        'icon': ':material/replay:'
    },
    'Dynast': {
        'description': '### **Following family tradition**. Philanthropy is in your blood, a legacy passed down through generations, and you proudly carry the torch.',
        'icon': ':material/family_restroom:'
    },
    'Altruist': {
        'description': '### **Giving from the heart**. Your generosity knows no bounds; you give selflessly and with deep compassion, driven by a love for humanity.',
        'icon': ':material/favorite:'
    },
    'Indifferent': {
        'description': '### **I don\'t give a shit about** philanthropy or social causes. You believe that everyone should fend for themselves, and you see no reason to contribute.',
        'icon': ':material/block:'
    },
    'Deflector': {
        'description': '### **It\'s somebody else\'s problem**. You believe that social issues and philanthropy are for others to worry about, not your concern or responsibility.',
        'icon': ':material/warning:'
    }
}
    show_pathways(philanthropic_profiles, cols=3)

    st.markdown("# <center> Step X: Example reading / xxx</center>", unsafe_allow_html=True)
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


    st.markdown("# <center> Step X: Finalise / commit</center>", unsafe_allow_html=True)
    st.markdown(
"""
To cover expenses and manage potential surplus funds, follow these steps:

1. **Clearly Communicate Goals:** Outline the primary objective of covering expenses for travel, accommodation, and meals. Specify that any extra funds will support projects in decision-making, scientific research, and artistic endeavors.


3. **Transparency:** Regularly update donors on how their contributions are being used.

4. **Acknowledge Contributions:** Recognize and thank donors for their support, detailing the impact of their donations.

5. **Engage Further:** Invite donors to follow the project’s progress and participate in future initiatives."""
    )
    
    
    # st.write(list(philanthropic_profiles.keys())[id-1])
    # st.write(list(philanthropic_profiles.items())[id-1][1]['description'])
    # st.session_state["profile"] = id
    # st.markdown(id)

    # if "profile" not in st.session_state:
        # st.session_state["profile"] = None
    # generate string based on data
    mask_string = lambda s: f"{s[0:4]}***{s[-4:]}"

    st.markdown("## `SCFS10110`" + '<code>' + mask_string("asdasdasdasdasdasda") + "</code>", unsafe_allow_html=True)

if __name__ == "__main__":
    alert_text = """
The 'Social Contract from Scratch' is a panel discussion at the Europe in Discourse 2024 conference in Athens (26-28 September), seeking to explore and redefine the fundamental principles of societal cooperation and governance in an era marked by simultaneous and interconnected 'polycrises'. 

Are you happy to proceed?
------------------------------------------------------------------------------------------------------------------------------------------------------
Click twice on the 'Yes' button _twice_ to go forward.

"""
    # disclaimed = ui.alert_dialog(show=not st.session_state["alerted"], 
    #                 title="Alert Dialog", 
    #                 description=alert_text, 
    #                 confirm_label="Yes", 
    #                 cancel_label="Whatever...", 
    #                 key="alert_dialog_1",
    #                 )

    # if disclaimed:
    #     st.session_state.alerted = True
    #     # st.rerun()  # Immediately rerun to refresh the page
    # else:
    #     st.write("Do you agree to proceed?")
    #     # click button to clear the cache
        
    #     if st.button("Yes"):
    #         st.session_state.clear()
    #         st.rerun()
            
    #     st.stop()
                

    body()
