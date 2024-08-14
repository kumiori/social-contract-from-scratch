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
import streamlit_shadcn_ui as ui
import pandas as pd
from streamlit_extras.add_vertical_space import add_vertical_space 

with open("assets/discourse.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.write(f.read())
    
with open('assets/credentials.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    now = datetime.now()
    # st.markdown(f"`Now is {now.strftime('%s')}-{now.strftime('%f')}~` max is {st.session_state.range if st.session_state.range else ''}")

if 'alerted' not in st.session_state:
    st.session_state.alerted = False

db = IODatabase(conn, "discourse-data")
data = db.fetch_data()
df = pd.DataFrame(data)
item_count = len(df)


@st.dialog("Join the whitelist")
def join_waitlist():
    from email_validator import validate_email, EmailNotValidError
    st.markdown("**Welcome aboard**")
    st.markdown("""
We're excited that you are interested in joining our initiative. As we build a focused and passionate community, your interest is a great step, and we'd love to learn more about you and your ideas. 

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
            st.write(f"Thank you `{name}` for your interest. We will get back to you shortly.")
    # st.write("We are working on the whitelist feature. Please check back later.") 
    
    
def blurscape():
    with open("assets/effects.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


    # Embed custom HTML, CSS, and JavaScript using st.markdown
    st.markdown("""
        <div class="card">
            <svg 
                viewBox="0 0 100% 100%"
                xmlns='http://www.w3.org/2000/svg'
                class="noise"
                >
            <filter id='noiseFilter'>
                <feTurbulence 
                            type='fractalNoise' 
                            baseFrequency='0.85' 
                            numOctaves='6' 
                            stitchTiles='stitch' />
            </filter>
            <rect
                    width='100%'
                    height='100%'
                    preserveAspectRatio="xMidYMid meet"
                    filter='url(#noiseFilter)' />
            </svg>
            <div class="content">
            <center><h1>Tr∀*st Game</h1></center>
            <center><h2>The Gradient</h2></center>
            <center><h3>to the Steepest Descent</h3></center>
            <br />
            <p>Can we play experimental game designed to explore trust dynamics between humans and financial institutions?</p>
            <p>We explore questions of trust, trustworthiness, and cooperation in social interactions.</p>
            <h3><a href="">Play to Game</a></h3>
            <h3><a href="">Pay to Play</a></h3>
            <h3><a href="">Wait to See</a></h3>
            </div>
        </div>
        <div class="gradient-bg">
            <svg 
                viewBox="0 0 100vw 100vw"
                xmlns='http://www.w3.org/2000/svg'
                class="noiseBg"
                >
            <filter id='noiseFilterBg'>
                <feTurbulence 
                            type='fractalNoise'
                            baseFrequency='0.6'
                            stitchTiles='stitch' />
            </filter>
            <rect
                    width='100%'
                    height='100%'
                    preserveAspectRatio="xMidYMid meet"
                    filter='url(#noiseFilterBg)' 
            />
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg" class="svgBlur">
            <defs>
                <filter id="goo">
                <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
                <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -8" result="goo" />
                <feBlend in="SourceGraphic" in2="goo" />
                </filter>
            </defs>
            </svg>
            <div class="gradients-container">
            <div class="g1"></div>
            <div class="g2"></div>
            <div class="g3"></div>
            <div class="g4"></div>
            <div class="g5"></div>
            </div>
        </div>

        <script type="text/javascript">
            console.log('DOM loaded');
            document.addEventListener('DOMContentLoaded', () => {
                const interBubble = document.querySelector('.interactive');
                let curX = 0;
                let curY = 0;
                let tgX = 0;
                let tgY = 0;

                const move = () => {
                    curX += (tgX - curX) / 20;
                    curY += (tgY - curY) / 20;
                    interBubble.style.transform = `translate(${Math.round(curX)}px, ${Math.round(curY)}px)`;
                    requestAnimationFrame(move);
                };

            window.addEventListener('mousemove', (event) => {
                    tgX = event.clientX;
                    tgY = event.clientY;
                    console.log(tgX, tgY);
                });

                move();
            });
        </script>
    """, unsafe_allow_html=True)

def intro():
    cols = st.columns(4, vertical_alignment="center")
    today = datetime.now()
    target_date = datetime(today.year, 9, 26)

    # Calculate the time delta
    time_delta = target_date - today
        
    with cols[0]:
        ui.metric_card(title="Total count", content=item_count, description="Participants, so far.", key="card1")
    with cols[1]:
        ui.metric_card(title="Total GAME", content="0.1 €", description="Since  _____ we start", key="card2")
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


def request_booklet():
    st.toast("To request a booklet, \n please send an email to \n social.from.scratch@proton.me")

def body():
    st.divider()
    st.markdown("# <center> Join the initiative</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown("""
Philanthropy is our choice as a source of initial external support for our activity, helping fill in funding gaps: it is not charity but a way to connect and engage.
    """)
    add_vertical_space(3)
        
    links_row = row(4, vertical_align="center", gap="small")
    links_row.button(
        "I am a participant",
        use_container_width=True,
        on_click=request_booklet,
        type="secondary"
    )
    links_row.button(
        "Download the booklet",
        use_container_width=True,
        on_click=request_booklet,
        type="primary"
    )
    links_row.button(
        "I want to support",
        use_container_width=True,
        on_click=request_booklet,
    )
    links_row.link_button(
        "I want to know more",
        "#the-social-contract-from-scratch",
        # "https://www.europeindiscourse.eu/",
        use_container_width=True,
        type="primary"
    )
    st.divider()
    

def discourse():

    st.divider()
    st.markdown("# <center>The Social Contract from Scratch</center>", unsafe_allow_html=True)
    st.markdown("### <center>The intersection of Human and Natural Sciences, Philosophy, and Arts.</center>", unsafe_allow_html=True)
    # st.markdown('<center>`wait a minute`</center>', unsafe_allow_html=True)
    st.markdown(f"## _Today_ is {now.strftime('%A')}, {now.strftime('%-d')} {now.strftime('%B')} {now.strftime('%Y')}")
    st.divider()
    st.markdown(f"# <center>Chapter 0</center> ", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown("""
The **_social contract_** is a foundational concept in political philosophy, suggesting that individuals consent, either implicitly or explicitly, to form a so- ciety and abide by its rules, norms, and laws for mutual benefit. 

It posits that in exchange for giving up certain freedoms, individuals receive protection and order provided by the collective governance structure.
Historically articulated by philosophers, the social contract addresses questions of legitimacy, au- thority, and the origins of societal organisation. 

Right now, social inequalities, political polarisation, and breaches of trust between the governed and governing are calling into question the effectiveness and fairness of our current systems.

We wish to articulate this discourse with you, because all voices have a role.
""")
def tabs():
    st.markdown("# <center> The panel discussion</center>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["# Overview", "Contributions", "Minimal Glossary", "Frequency Asked Questions", "Acknowledgements", "Contacts"])
    

if __name__ == "__main__":
    alert_text = """
The 'Social Contract from Scratch' is a panel discussion at the Europe in Discourse 2024 conference in Athens (26-28 September), seeking to explore and redefine the fundamental principles of societal cooperation and governance in an era marked by simultaneous and interconnected 'polycrises'. 
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Systemic inequality, environmental degradation, resource scarcity, and geopolitical tensions, all of them challenge the effectiveness of traditional multilateral frameworks.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Consider your personal interests and join us ONLY IF they fit within your vision and plans. We address systemic issues, framing the importance of philanthropy on an international scale.

Are you happy to proceed?
------------------------------------------------------------------------------------------------------------------------------------------------------
Click twice on the 'Yes' button to go forward.

"""
    disclaimed = ui.alert_dialog(show=not st.session_state["alerted"], 
                    title="Alert Dialog", 
                    description=alert_text, 
                    confirm_label="Yes", 
                    cancel_label="Whatever...", 
                    key="alert_dialog_1")
    # st.write(disclaimed)
    
    # if not disclaimed:
    #     # st.dialog("Alert Dialog")
    #     st.write("Alerted")
    #     import sys
    #     sys.exit()
    # else:
    #     st.session_state.alerted = True
    if disclaimed:
        st.session_state.alerted = True
        # st.rerun()  # Immediately rerun to refresh the page
    else:
        st.write("You must agree to proceed.")
        st.stop()
                
    intro()
        
    st.toast("Welcome to the Social Contract from Scratch")
        
    # blurscape()
    
    discourse()
    body()
    # tabs()