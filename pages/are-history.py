import streamlit as st
import requests
import time
import pandas as pd

import philoui
import streamlit.components.v1 as components

from streamlit_carousel import carousel
from philoui.io import QuestionnaireDatabase as IODatabase
from philoui.io import (
    conn,
    create_dichotomy,
    create_equaliser,
    create_qualitative,
    create_quantitative,
)
from philoui.survey import CustomStreamlitSurvey
from philoui.texts import hash_text, stream_text

# from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_timeline import timeline
from streamlit_gtag import st_gtag
from philoui.authentication_v2 import AuthenticateWithKey

# __import__("pdb").set_trace()
st_gtag(
    key="gtag_app_REHISTORY",
    id="G-Q55XHE2GJB",
    event_name="s&p_main_page",
    params={
        "event_category": "apply_s&p",
        "event_label": "test_s&p",
        "value": 97,
    },
)

#  == "Production"
# if st.secrets["runtime"]["STATUS"] is not None:
#     __import__("pdb").set_trace()
#     st.set_page_config(
#         page_title="The Social Contract from Scratch • Relations, Systems & Healing",
#         page_icon="✨",
#         # layout="wide",
#         initial_sidebar_state="collapsed",
#     )
cards = [
    dict(
        title="Why did the transatlantic slave trade tear our roots apart?",
        text=(
            "The forced separation of communities and the loss of human potential "
            "have left enduring scars on our societies. What might our future be if our ancestors "
            "had not been stolen away?"
        ),
        img="https://imgur.com/Cev833F.jpeg",  # Provided image URL
        link="https://example.com/more-on-slave-trade",  # Replace with your desired link
    ),
    dict(
        title="Why do arbitrary borders still divide our land?",
        text=(
            "The legacy of decisions made without our voices—carving boundaries that persist in fueling conflicts "
            "and division. How different if boundaries were drawn by our own hands?"
        ),
        img="https://imgur.com/eJgWX3R.jpeg",  # Provided image URL
        link="https://example.com/more-on-borders",  # Replace with your desired link
    ),
    dict(
        title="Why did the struggle for independence ignite new hope?",
        text=(
            "Fight for self-determination has birthed nations and inspired dreams of freedom. "
            "Who dares to envision a future beyond colonial chains?"
        ),
        img="https://imgur.com/Cev833F.jpeg",  # Provided image URL
        link="https://example.com/more-on-independence",  # Replace with your desired link
    ),
    dict(
        title="Why has our resource wealth become a double-edged sword?",
        text=(
            "The promise of prosperity from our natural riches turned into conflict and environmental decay. "
            "Who transforms exploitation?"
        ),
        img="https://imgur.com/eJgWX3R.jpeg",  # Provided image URL
        link="https://example.com/more-on-resource-wealth",  # Replace with your desired link
    ),
]
carousel(items=cards, container_height=400, width=1.0)


st.markdown("# History, written in real-time.")


"""`fast or slow?`"""


"""Would you like to play? I have a key and a question for you."""
"`fast backward to XXXX`"
st.markdown("## Why African history ...")

config = {
    "credentials": {"webapp": "are-history", "usernames": {}},
    "cookie": {
        "expiry_days": 30,
        "expiry_minutes": 30,
        "key": "are_history_cookie",
        "name": "are_history_cookie",
    },
    "preauthorized": {"emails": ""},
}

authenticator = AuthenticateWithKey(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
    pre_authorized=config["preauthorized"],
)

db = IODatabase(conn, "re0history")

fields_connect = {
    "Form name": "Forwrd to the Past",
    "Email": "Your Email Address",
    "Username": "Your Revolutionary Alias",
    "Password": "Secret Passcode",
    "Repeat password": "Confirm Your Passcode",
    "Register": "Retrieve Your Access Key",
    "Captcha": "Security Check",
}

fields_forge = {
    "Form name": "Lost Your Key? Forge a New One",
    "Email": "Your Email Address",
    "Username": "Choose Your Alias",
    "Password": "Set Your Secret Code",
    "Repeat password": "Confirm Your Code",
    "Register": "Forge It Now",
    "Captcha": "Security Check",
}


"""Welcome to ___________

### Re-enacting African Historical Decisions for Self-Determined Governance


History is not a record of the past. Today is XX/XX/XXX your decisions help re-enact pivotal moments in African history. Our goal is to empower us to explore, understand, and challenge historical decisions, fostering a collective narrative that moves toward self-determined governance.

Access Key Creation

If this is your first time here, please create your unique access key.
Your identity remains anonymous—your access key is all you need. It ensures that your trace is securely updated and that your interactions remain smooth.

	•	[Create Access Key]

Click the button to generate your key. Once created, you are responsible to store it securely for your future sessions.


### Do you want to play? Continue, be our guest

It's 8:14pm my cousin brother calls me. We had decided to have a chat today, 
it's been a while since we last spoke.

Do you pick this this evening call? [OK] [We'll interact another time]
"""
st.markdown("`Cool, it's good to sync every now and then. `")
"""
This is an interactive and participatory game that revisits, in time, key historical decisions in Africa, allowing the community to question, understand and rethink those crucial moments.

This game invites each of us to question the decisions that oppressed our peoples and to chart a path of freedom and self-determination.

My experience in strategy and your knowledge of the field, make our insights valuable in enriching this quest.

Re-History is not for the exclusive elites; it is for all of us, joining who fight against oppression from different fronts:
- Intellectuals and academics, for those who think, analyse, and transform reality with the power of understanding.
- Activists and community organisers, who mobilise people and generate change from the grassroots.
- Students and young leaders, with their energy and creativity, are looking forward to reshape the future.

You will take on historical roles, participate in decision-making, and interact with historical scenarios many in other ways.
This is a game, a learning experience, a coordination tool, a strategy for change, educational tool. 

MAKE YOUR MIX

This game is a hybrid of both digital and physical experiences.

EVENTS/ENJOY DANCE

### How to play

Choose a pivotal historical event from a curated list and immerse yourself in its rich context through documents, images, feedbacks, interviews, contributions, and interactive timelines. Once you’ve grasped the background, select a role and engage with history. Challenging “why” questions at key turning points, allowing your decisions to reshape the narrative. 

To reflect on your choices, dynamic visualizations and custom-driven insights. Join the community, real-time discussions and collective decisions— all while working toward earning an invitation to an  summit, to be held between December and April...

BECAUSE players make decisions in real-time (synchronously with other players) or asynchronously (logging in and contributing at different times), KNOWING YOUR TIMEZONE HELPS BALACING THE GAME.
WHERE YOU DO YOU CONNECT FROM?

[PRECISE LOCATION]
[] I am in Africa
[] I am in the diaspora
[] I am in the global south
[] I am in the global north
[] I am in the global east
[] I am in the global west
[] I am SOMEWEHERE ELSE

`LOVELY`

Players receive a personalized debriefing summarizing their choices, comparing them to real history, and showing how their approach aligns with different schools of thought. WHAT LEVEL OF DETAIL WOULD YOU LIKE TO RECEIVE? [BASIC] [ADVANCED] [BRAINY]


HERE IS WHERE TIMELINES SPLIT. 
We have interactive timelines, EXPLORE
- Pre-colonial Africa
- Colonial Africa
- Post-colonial Africa
- Contemporary Africa

Players interact. How do YOU PREFER: Discussion boards, debates, or voting systems?


"""
st.markdown("### THE NEXT EVENT HAPPENS IN - The Berlin Conference")
"""`no choice, given option, otherwis`"""
event_time = st.slider(
    "Select the time remaining for the next event (in years):", -60, -(2025 - 1884)
)
st.markdown(f"The next event will happen in {event_time} years.")
now = 2025
st.select_slider(
    "Select the time remaining for the next event (in years):",
    options=[
        1807 - now,
        1884 - now,
        1957 - now,
        1960 - now,
        1962 - now,
        1970 - now,
        0,
        1,
        2,
        3,
    ],
)
"""
1. The Abolition Movements (e.g., the British Slave Trade Act of 1807):
1. The Berlin Conference (1884-1885)
1. Declarations of National Independence: Ghana's independence in 1957, Nigeria's in 1960, and Algeria's in 1962
1. The Shift to an Oil-Dependent Economy (1970s Boom)
"""
