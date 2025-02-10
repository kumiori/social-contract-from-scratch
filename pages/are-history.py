import streamlit as st
import requests
import time
import pandas as pd

import philoui
import streamlit.components.v1 as components
from datetime import datetime
import yaml
import random
from streamlit_carousel import carousel
from philoui.io import QuestionnaireDatabase as IODatabase
from philoui.io import (
    conn,
    create_dichotomy,
    create_equaliser,
    create_qualitative,
    create_quantitative,
    create_yesno_row,
)
from philoui.geo import get_coordinates
from streamlit_extras.stateful_button import button as stateful_button

from philoui.survey import CustomStreamlitSurvey
from philoui.texts import hash_text, stream_text
import streamlit_shadcn_ui as ui

# from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_timeline import timeline
from streamlit_gtag import st_gtag
from philoui.authentication_v2 import AuthenticateWithKey
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime, timedelta

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

survey = CustomStreamlitSurvey()

st.markdown("# History is writing, in real-time.")


def on_yes():
    # Route the player to the game screen
    st.session_state.page = "game"
    st.success("Great! Let’s start the game.")
    # pause 1 second
    # show spinner
    with st.spinner("Loading the game..."):
        time.sleep(1)


def on_no():
    # Route the player to an exit or info screen
    st.session_state.page = "exit"
    st.info("No problem. You can explore more about our story later.")
    st.markdown("Close this browser tab to exit the application.")
    st.stop()


"""Would you like to play? I have a key and a question for you."""

response = create_yesno_row(
    "play_yesno_row", kwargs={"survey": survey, "callback": [on_yes, on_no]}
)

"""`fast or slow?`"""


def authentifier():
    tab_returning, tab_new = st.tabs(["I am returning", "I am new"])

    with tab_returning:
        if st.session_state["authentication_status"] is None:
            authenticator.login("Connect", "main", fields=fields_connect)
            st.warning("Enter your forged access key to proceed.")
        else:
            st.markdown(
                f"#### Your access key is already forged. Its signature: `{mask_string(st.session_state['username'])}`."
            )

    with tab_new:
        if st.session_state["authentication_status"] is None:
            """
            A key awaits your forging.  
            Complete the captcha and click `Here • Now` to retrieve your unique access key.
            """
            try:
                match = True
                success, access_key, response = authenticator.register_user(
                    data=match,
                    captcha=True,
                    pre_authorization=False,
                    fields=fields_forge,
                )
                if success:
                    st.success("Access key forged successfully")
                    st.toast(f"Access key: {access_key}")
                    st.session_state["username"] = access_key
                    st.markdown(
                        f"### Your access key is `{access_key}`. Connect using this key and safeguard it—it unlocks the next stage of our journey."
                    )
            except Exception as e:
                st.error(e)
        else:
            st.info("You are already connected.")
            authenticator.logout()


def my_create_dichotomy(key, id=None, kwargs={}):
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
        survey = kwargs.get("survey")
        label = kwargs.get("label", "Confidence")
        name = kwargs.get("name", "there")
        question = kwargs.get("question", "Dychotomies, including time...")
        messages = kwargs.get(
            "messages", ["🖤", "Meh. Balloons?", "... in between ..."]
        )
        inverse_choice = kwargs.get("inverse_choice", lambda x: x)
        _response = kwargs.get("response", "` always ...`")
        col1, col2, col3 = st.columns([3, 0.1, 1])
        response = survey.dichotomy(
            name=name,
            label=label,
            question=question,
            gradientWidth=kwargs.get("gradientWidth", 10),
            key=key,
        )
        if response:
            st.markdown("\n")
            if float(response) < 0.1:
                st.success(messages[0])
            if float(response) > 0.9:
                st.info(messages[1])
            elif 0.1 < float(response) < 0.9:
                st.success(messages[2])
        else:
            st.markdown(f"#### Take your time", unsafe_allow_html=True)
            st.markdown(_response)
    return response


def next_step():
    # User location input
    location = st.text_input("Where are you connecting from?")

    # Try to obtain coordinates for the provided location
    if location:
        coordinates = get_coordinates(st.secrets.opencage["OPENCAGE_KEY"], location)
        if coordinates:
            st.write(
                f"`Coordinates for {location}: Latitude {coordinates[0]}, Longitude {coordinates[1]}`"
            )
            st.session_state.location = location
            st.session_state.coordinates = coordinates
        else:
            st.error("Could not find coordinates for that location.")

    # Pre-defined cities for the map
    cities = [
        {
            "name": "Paris",
            "lat": 48.8566,
            "lng": 2.3522,
            "maxR": random.random() * 20 + 3,
            "propagationSpeed": (random.random() - 0.5) * 20 + 1,
            "repeatPeriod": random.random() * 2000 + 200,
            "size": random.random(),
        },
        {
            "name": "Abidjan",
            "lat": 5.3599,  # Approximate latitude for Abidjan
            "lng": -4.008,  # Approximate longitude for Abidjan
            "maxR": random.random() * 20 + 3,
            "propagationSpeed": (random.random() - 0.5) * 20 + 1,
            "repeatPeriod": random.random() * 2000 + 200,
            "size": random.random(),
        },
    ]

    # If user coordinates are available, add them as a new city for mapping
    if "coordinates" in st.session_state:
        user_city = {
            "name": st.session_state.location,
            "lat": st.session_state.coordinates[0],
            "lng": st.session_state.coordinates[1],
            "maxR": random.random() * 20 + 3,
            "propagationSpeed": (random.random() - 0.5) * 20 + 1,
            "repeatPeriod": random.random() * 2000 + 200,
            "size": random.random(),
        }
        cities.append(user_city)

    timezone_finder = TimezoneFinder()

    for city in cities:
        tz_str = timezone_finder.timezone_at(lat=city["lat"], lng=city["lng"])
        city["timezone"] = tz_str
        if tz_str:
            tz = pytz.timezone(tz_str)
            # Get the current UTC offset as a timedelta
            utc_offset = tz.utcoffset(datetime.now())
            # city["utc_offset"] = utc_offset
            city["utc_offset"] = (
                utc_offset.total_seconds() if utc_offset is not None else None
            )
        else:
            city["utc_offset"] = None

    # Optionally, display each city's time zone info
    for city in cities:
        st.write(
            f"{city['name']}: Time Zone: {city.get('timezone', 'Unknown')}, "
            f"UTC Offset: {city.get('utc_offset', 'Unknown')}"
        )

    # Compute the barycentre of the UTC offsets (only for cities with a valid offset)
    offsets_seconds = [
        city["utc_offset"] for city in cities if city["utc_offset"] is not None
    ]

    if offsets_seconds:
        avg_offset_seconds = sum(offsets_seconds) / len(offsets_seconds)
        avg_offset_timedelta = timedelta(seconds=avg_offset_seconds)
        # Convert the average offset to hours and minutes
        total_seconds = avg_offset_timedelta.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        # Format the average offset as a UTC string
        barycentre_str = f"UTC{'+' if hours >= 0 else ''}{hours}:{minutes:02d}"
        st.write(f"Barycentre of offsets: {barycentre_str}")
    else:
        st.write("No valid UTC offsets found.")
    # For now, simply display the list of cities (which you can later use to render a map)

    # st.write(cities)
    _manual = st.toggle("Rotate manually", False, key="manual_cities")
    st.write("Rotate manually", _manual)

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

    const map = Globe()
    (document.getElementById('globeViz'))
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .ringsData(cityData)
    //.pointsData(markerData)
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
    map.controls().autoRotate = {"true" if not _manual else "false"};
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


def exploded():
    st.markdown("""
        Imagine Africa, its contours laid bare, the seas and the forests, the oceans stretching across a land filled with life, it's contours, the landscapes
    always moving, always shifting.
    natural boundaries, in all their complexity, all connected.

    At which level is Africa truly united? Have we looked deep into history—into the forces of division, the legacy of imposed borders, and the stark contrasts of oppression—that have molded these landscapes? Today, this is a mirror reflecting differences and divisions, as well as a call to reimagine unity. Not just a map. Would you like to see it differently?
    """)

    _manual = st.toggle("Rotate manually", False)

    javascript_code = f"""
    const world = new Globe(document.getElementById('fragWorldViz'))
    .backgroundColor('rgb(255, 255, 255)')
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
    //  .pointOfView({{ altitude: 4 }}, 5000)
      .polygonCapColor(feat => 'rgba(200, 0, 0, 0.6)')
      .polygonSideColor(() => 'rgba(0, 100, 0, 0.1)');
    
    world.controls().autoRotate = {"true" if not _manual else "false"};
    world.controls().autoRotateSpeed = 1.8;
    
    fetch('https://raw.githubusercontent.com/vasturiano/globe.gl/refs/heads/master/example/datasets/ne_110m_admin_0_countries.geojson')
  .then(response => response.json())
  .then(geojson => {{
    console.log('Countries GeoJSON:', geojson);
    world.polygonsData(geojson.features.filter(d => d.properties.ISO_A2 !== 'AQ'));
    setTimeout(() => world
      //.polygonAltitude(feat => Math.max(0.1, Math.sqrt(+feat.properties.POP_EST) * 7e-5))
      .polygonAltitude(feat => {{
           return feat.properties.CONTINENT === 'Africa'
             ? Math.max(0.1, Math.sqrt(+feat.properties.POP_EST) * 7e-5)
             : 0.01;
      }})
      .polygonsTransitionDuration(4000)
    );
 }})
  .catch(err => console.error('Error fetching countries GeoJSON:', err));

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
    <div id="fragWorldViz"></div>
    <div id="time"></div>
    
    <script type="module">
        { javascript_code }
    </script>
    </body>
    """
    col1, col2 = st.columns(2)
    with col1:
        st.components.v1.html(html_code, height=700, width=700)


def intro():
    # Create four equally spaced columns for our header metrics and navigation
    cols = st.columns(4, vertical_alignment="center")
    today = datetime.now()
    target_date = datetime(today.year, 9, 26)  # Strategic summit target date
    time_delta = target_date - today  # Calculate remaining days

    with cols[0]:
        ui.metric_card(
            title="Decisions Recorded",
            content="0",
            description="Your choices, our collective history.",
            key="card1",
        )
    with cols[1]:
        st.button(
            "Enter the Archives", key="connect", disabled=True, use_container_width=True
        )
    with cols[2]:
        ui.metric_card(
            title="Days to Re-History",
            content=f"{time_delta.days}",
            description="Until the strategic summit",
            key="card3",
        )
    with cols[3]:
        st.markdown("#### Areas")
        # Display badges representing key domains of interest
        ui.badges(
            badge_list=[
                # ("Social Events", "secondary"),
                ("Environmental Challenges", "secondary"),
                # ("Geopolitical Accords", "secondary"),
                ("Cultural Debates", "secondary"),
            ],
            class_name="flex gap-2",
            key="viz_badges2",
        )
        switch_value = ui.switch(
            default_checked=True, label="Political mode", key="switch1"
        )
        st.toast(f"Political mode is {switch_value}")
        whitelist = ui.button(text="Review the Outcomes", url="", key="link_btn")

    st.markdown(
        "# <center>Re-History: Rewiring The Past, Shaping Our Future</center>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "## <center>Cultural insights for transformative action.</center>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"## _Today_ is {today.strftime('%A')}, {today.strftime('%-d')} {today.strftime('%B')} {today.strftime('%Y')}"
    )

    st.divider()


my_create_dichotomy(
    key="event",
    id="event",
    kwargs={
        "survey": survey,
        "label": "future_event",
        "question": "Click to express your viewpoint.",
        "gradientWidth": 1,
        "height": 250,
        "title": "",
        "name": "intuition",
        "messages": [
            "*Black*",
            "*White*",
            "*A sharp mix*",
        ],
        # 'inverse_choice': inverse_choice,
        "callback": lambda x: "",
    },
)


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
    "Form name": "Roll back to Now",
    "Email": "Your Email Address",
    "Username": "Your Revolutionary Alias",
    "Password": "Secret Passcode",
    "Repeat password": "Confirm Your Passcode",
    "Register": "Retrieve Your Access Key",
    "Captcha": "Numbers to forget",
}

fields_forge = {
    "Form name": "Here's your access key",
    "Email": "Your Email Address",
    "Username": "Choose Your Alias",
    "Password": "Set Your Secret Code",
    "Repeat password": "Confirm Your Code",
    "Register": "Forge It Now",
    "Captcha": "Numbers to forget",
}

with open("assets/re0history.css", "r") as f:
    st.html(f"<style>{f.read()}</style>")

with open("assets/credentials.yml") as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)
    now = datetime.now()

mask_string = lambda s: f"{s[0:4]}***{s[-4:]}"


"""Welcome to ___________

### Re-enacting African Historical Decisions for Self-Determined Governance


"""

intro()

"""

History is not a record of the past. Today is XX/XX/XXX your decisions help re-enact pivotal moments in African history. Our goal is to empower us to explore, understand, and challenge historical decisions, fostering a collective narrative that moves toward self-determined governance.

`Access Key Creation`
"""

exploded()

"""
Your identity remains anonymous—your access key is all you need. 
If this is your first time here, create yours.
It ensures that your trace is securely updated and that your interactions remain smooth.

"""
authentifier()


"""


Click the button to generate your key. Once created, you are responsible to store it securely for your future sessions.


### Do you want to play? Continue, be our guest

It's 8:14pm my cousin brother calls me. We had decided to have a chat today, 
it's been a while since we last spoke.

It's black or white? Do you pick (Black) this this evening call (Or not, White)? 
"""


st.markdown("`Cool, it's good to sync every now and then. `")
"""
This is an interactive and participatory game that revisits, in time, key historical decisions in Africa, allowing the community to question, understand and rethink those crucial moments.

This game invites each of us to question the decisions that oppressed our peoples and to chart a path of freedom and self-determination.

My experience in strategy and your knowledge of the field, make our insights valuable in enriching this quest.

Decision is not for the exclusive elites; it is for all of us, joining who work against oppression from different fronts:
- Intellectuals and academics, for those who think, analyse, and transform reality with the power of understanding.
- Activists and community organisers, who mobilise people and generate change from the grassroots.
- Students and young leaders, with their energy and creativity, are looking forward to reshape the future.

Here's the deal: you take on historical role, participate in decision-making, and interact with historical scenarios many in other ways.
This is a game, a learning experience, a coordination tool, a strategy for change, educational tool. 



"""

equaliser_data = [
    ("Soc", ""),
    ("Pol", ""),
    ("Env", ""),
    ("XXX", ""),
    ("YYY", ""),
]

st.subheader("YOUR MIX")

create_equaliser(
    key="equaliser",
    id="equaliser",
    kwargs={"survey": survey, "data": equaliser_data},
)

"""

This game is a hybrid of both digital and physical experiences.

EVENTS/ENJOY DANCE

### How to play

A pivotal historical event [from a curated list] and immerse yourself in its rich context through documents, images, feedbacks, interviews, contributions, and interactive timelines. Once you’ve grasped the background, select a role and engage with history. Challenging “why” questions at key turning points, allowing your decisions to reshape the narrative. 

"""
next_step()

"""
To reflect on your choices, dynamic visualizations and custom-driven insights. Join the community, real-time discussions and collective decisions— all while working toward earning an invitation to an  summit, to be held between December and April...

Participants make decisions in real-time (synchronously with other players) or asynchronously (logging in and contributing at different times), KNOWING YOUR TIMEZONE HELPS BALACING THE GAME.
WHERE YOU DO YOU CONNECT FROM?


"""


# Define the geographic context options
geo_options = [
    "I am in Africa",
    "I am in the diaspora",
    "I am in the global south",
    "I am in the global north",
    "I am in the global east",
    "I am in the global west",
    "I am SOMEWHERE ELSE",
]

# Use a radio button to allow the user to select one option
selected_geo = st.radio(
    "Indicate your geographic context:", geo_options, key="geo_context", horizontal=True
)

"""

`LOVELY`

Players receive a personalized debriefing summarizing their choices, comparing them to real history, and showing how their approach aligns with different schools of thought. WHAT LEVEL OF DETAIL WOULD YOU LIKE TO RECEIVE? 


"""

"--------"

_response = survey.qualitative_parametric(
    name="quali",
    label="quali",
    question="quali",
    key="quali",
    data_values=[
        1,
        2,
    ],
    areas=3,
)
_response = survey.quantitative(
    name="quantitative",
    label="Quantitative",
    question="Quantitative",
    key="quantitative",
    data_values=[
        1,
        2,
    ],
)

qualitative_key = "demo_qualitative"
# create_qualitative(qualitative_key, kwargs={"survey": survey})
# create_quantitative("quanti", kwargs={"survey": survey})


"--------"

"""


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
