import streamlit as st
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

from streamlit_extras.row import row
from streamlit_gtag import st_gtag

st_gtag(
    key="gtag_app_main",
    id="G-Q55XHE2GJB",
    event_name="main_page",
    params={
        "event_category": "SCFS",
        "event_label": "SCFS_a",
        "value": 97,
    },
)
import yaml
from yaml import SafeLoader
import philoui
from datetime import datetime
from philoui.io import conn, QuestionnaireDatabase as IODatabase
import streamlit_shadcn_ui as ui
import pandas as pd
from streamlit_extras.add_vertical_space import add_vertical_space 
from streamlit_player import st_player

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

blacklist = IODatabase(conn, "blacklist")
import json

def _whitelist_submit(email, name):
    with st.spinner("Checking your signature..."):
        # signature = st.session_state["username"]
        # serialised_data = st.session_state['serialised_data']
                
        time.sleep(2)

        st.write(f"Updating `whitelist`")
        try:
            if not email:
                raise ValueError("Email cannot be null or empty.")
        
            data = {
                'email': email,
                'full_name': name,
                'webapp': 'SCFS',
            }

            query = conn.table('blacklist')                \
                    .upsert(data, on_conflict=['email'])     \
                    .execute()
            
            if query:
                st.success("🎊 Preferences integrated successfully!")
        except ValueError as ve:
            st.error(f"Data error: {ve}")                
        except Exception as e:
            st.error("🫥 Sorry! We couldn't update the whitelist.")
            st.write(e)

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
            
            _whitelist_submit(email, name)
    # st.write("We are working on the whitelist feature. Please check back later.") 
    
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


def body():
    st.divider()
    
    """    
    ### _Committing to action._ Our digital platform is desiged to allow connection and establish a base for sharing understanding. 
    -----------
    """
    st.markdown("# <center> Join the initiative</center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 9, 1])
    with col2:
        st.markdown("""
Philanthropy is our choice as a source of initial external support for our activity, helping fill in funding gaps: it is not charity but a way to connect and engage.
    """)
    add_vertical_space(3)
        
    links_row = row(2, vertical_align="center", gap="small")
    links_row.button(
        "Author log in",
        use_container_width=True,
        type="secondary"
    )
    # links_row.button(
    #     "I want the booklet",
    #     use_container_width=True,
    #     on_click=request_booklet,
    #     type="primary"
    # )
    with open('assets/SocialContractFromScratch-Panel.pso.pdf', 'rb') as f:
        links_row.download_button(
            "I want the booklet",
            f,
            use_container_width=True,
            file_name="Social•Contract•From•Scratch-Athens-Panel.pdf",
            type="primary"
        )
    event = st_player("https://vimeo.com/1007188309", key='vimeo_player')
        
    # links_row.page_link("pages/apply.py", label="Application for Support", icon="1️⃣")
    # links_row.button(
    # # link_button(
    #     "I want to apply for support",
    #     # "/pages/apply",
    #     use_container_width=True,
    #     type="secondary"
    # )
    st.divider()
  
    """
    We have made significant steps in organising the panel, gathering a diverse group of friends, scholars, and practitioners who are eager to contribute. Our digital tools are being developed to facilitate interactive participation and real-time feedback during the event. 
    
    We are now seeking support for our 17-member team,  the Athena Collective, to cover the costs of attending the event, and curating the edition of the _Social Contract_ booklet.
    
    Join our initiative _as a philanthropist_, supporting our work.
    """

    st.page_link("pages/apply.py", label="Philanthropy for Us 📣", icon="📣", use_container_width=True)
    st.page_link("pages/apply.py", label="Application for Philanthropic Support 💭", icon="🔮", use_container_width=True)

    """
    -----------
    """
    """
### Social inequalities, environmental degradation, and political polarisation. Pressing global issues? 
-----
    """  
    """**What are we going to deliver?**
   We aim to start a groundwork activity to experience new ways of engaging in cooperation, governance, and societal agreements. Among the outcomes: a _Social Contract_, actionable insights, a collaborative framework for future initiatives, and a real-time digital app that will be shared with all participants and stakeholders.
   
   Your participation will directly support the creation of these deliverables and help us _etch a scratch_.
    """
    
    
def discourse():

    st.divider()
    st.markdown("# <center>The Social Contract from Scratch</center>", unsafe_allow_html=True)
    st.markdown("## <center>A meeting of Social and Natural Sciences, Philosophy, and Arts.</center>", unsafe_allow_html=True)
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
    st.markdown("# <center> Overview</center>", unsafe_allow_html=True)
    
    # tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["# Overview", "Contributions", "Minimal Glossary", "Frequency Asked Questions", "Acknowledgements", "Contacts"])
    tab1, tab2, tab3, tab4, tab5, = st.tabs(["How", "What", "Who", "Why", "Where"])
    
    with tab1:
        st.write("## How are we doing?")
        st.markdown("""
                    We have made significant steps in organising the panel, gathering a diverse group of friends, scholars, and practitioners who are eager to contribute. Our digital tools are being developed to facilitate interactive participation and real-time feedback during the event. However, to fully realise our Panel in Athens, we still need financial support to cover essential costs.
                    """)
    
    with tab2:
        st.write("## What is the event?")
        st.markdown("""
                    The event is the "Europe in Discourse*" conference in Athens, we will host a panel discussion titled "The Social Contract from Scratch." This event addresses "Future Trajectories for Europe" . The goal is to engage in a meaningful dialogue on how to reconstruct the foundational agreements of society in today's challenging context.
                    """)
    
    with tab3:
        st.write("## Who is going to attend?")
        st.markdown("""
                    The event features a diverse lineup of participants, including well-known policy experts, historians, discourse analysts, authors, public intellectuals, and passionate advocates for social change. 
                    
                    Philanthropic support will help us bring together many voices and ensure that the discussion reaches a wide and engaged audience.
                    """)
    
    with tab4:
        st.write("## Why are we doing this?")
        st.markdown("""
                    We are undertaking this project because the current social, political, and economic systems are showing signs of strain and imbalance. We understand the necessity of rebuilding a foundation — a social contract from scratch — where diverse perspectives can come together to address the complexity of today's challenges. 
                    
                    Traditional structures often lack transparency, participation, and inclusivity, which leads to growing discontent, polarisation, and inequality.
                    
                    Decision-making _should be_  transparent and inclusive. Where policies are not top-down but co-created by the many. Where solutions are not imposed but developed collaboratively, addressing the real needs and desires of society.
                    
                    Why is it not _already_ so?
                    """)
    with tab5:
        st.write("## Where is this happening?")
        st.markdown("""
                    The event will take place at the Hellenic University of Athens, Greece, from 26-28 September 2024. The panel discussion will be part of the "Europe in Discourse" conference, the fourth episode of a conference series.
                    
                    All of this is happening at the intersection of global crises and local realities. Where communities are coming together to demand change; and in digital spaces, where people are connecting across borders to collaborate.
                    
                    But more than anything, it's happening in the spaces in-between: between the cracks of existing systems, in the gaps where traditional power structures are weak, in the fragments of "free time", and where ideas can emerge. It's in these spaces that our initiative is finding fertile soil, aiming to bridge across boundaries, the personal with the collective, and the theoretical with the practical.

                    """)

if __name__ == "__main__":
    alert_text = """
The 'Social Contract from Scratch' is a panel discussion at the Europe in Discourse 2024 conference in Athens (26-28 September), seeking to explore and redefine the fundamental principles of societal cooperation and governance, in an epoch marked by simultaneous and _interconnected_ 'polycrises'. 

------------------------------------------------------------------------------------------------------------------------------------------------------
Click twice on the button.

"""
    disclaimed = ui.alert_dialog(show=not st.session_state["alerted"], 
                    title="Alert Dialog", 
                    description=alert_text, 
                    confirm_label="I am happy to proceed", 
                    cancel_label="Whatever...", 
                    key="alert_dialog_1")

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
    tabs()