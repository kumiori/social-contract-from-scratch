import streamlit as st
from streamlit_extras.row import row
conceptual_questions = {
    'Catastrophe Scenarios': {
        'description': '## **With the ability** to foresee future moments, you navigate life with wisdom beyond your years. Embrace your time-bending vision to illustrate the catastrophe scenarios that await planet Earth.',
        'icon': ':material/biotech:'
    },
    'New Economic Order': {
        'description': '## **Explore the idea** of a global economic reset. What systems would replace the current ones? How do we ensure they promote fairness and sustainability?',
        'icon': ':material/hearing:'
    },
    'Food (The Problem of Hunger)': {
        'description': '## **Hunger remains** one of the most pressing global issues. \n How can we innovate food distribution and production to eliminate hunger worldwide?',
        'icon': ':material/casino:'
    },
    'Development and Collaboration': {
        'description': '## **International collaboration** is key to sustainable development. \n How can countries work together more effectively to address global challenges?',
        'icon': ':material/wb_twilight:'
    },
    'Economic Dogmas': {
        'description': '## **Challenge the existing** economic beliefs and doctrines. What would a new set of economic principles look like, and how would they impact society?',
        'icon': ':material/polyline:'
    },
    'Business and War': {
        'description': '## **Examine the intricate** relationship between business interests and military conflicts. \n How can this entanglement be untangled for a more peaceful world?',
        'icon': ':material/flaky:'
    },
    'Conflicts and Entanglement': {
        'description': '## **Global conflicts** are often interconnected in complex ways. \n How can we untangle these conflicts to find pathways to peace?',
        'icon': ':material/kayaking:'
    },
    'Ethical Technology': {
        'description': '## **How can we** navigate the ethical challenges posed by rapid technological advancements, ensuring they benefit society as a whole?',
        'icon': ':material/signal_wifi_statusbar_not_connected:'
    },
    'Moral Boundaries': {
        'description': '## **As society evolves**, so do its moral standards. What are the new moral boundaries, and how do we uphold them?',
        'icon': ':material/no_adult_content:'
    },
    'Emergency Preparedness': {
        'description': '## **Are we truly** prepared for the unexpected? \n How can we improve our responses to sudden crises, be they natural or man-made?',
        'icon': ':material/emergency_heat:'
    },
    'Digital Privacy': {
        'description': '## **In a world** dominated by digital communication, \n how do we protect our privacy and ensure our data remains secure?',
        'icon': ':material/network_locked:'
    },
    'Freedom of Access': {
        'description': '## **The internet** was once envisioned as a space of freedom. How do we reclaim and protect this ideal in an era of increasing control?',
        'icon': ':material/captive_portal:'
    },
    'Environmental Awareness': {
        'description': '## **With climate change** becoming more pronounced, \n how can we raise awareness and encourage proactive measures to protect our planet?',
        'icon': ':material/brightness_alert:'
    },
    'Identity and Anonymity': {
        'description': '## **As the lines** between online and offline blur, \n how do we navigate issues of identity and the need for anonymity?',
        'icon': ':material/domino_mask:'
    },
    'Global Communication': {
        'description': '## **In a world** connected by technology, \n how can we ensure that communication remains clear, truthful, and effective?',
        'icon': ':material/thread_unread:'
    },
    'Climate Resilience': {
        'description': '## **As extreme weather** events become more common, \n how can societies adapt to ensure long-term resilience?',
        'icon': ':material/rainy_snow:'
    },
    'Health and Immunity': {
        'description': '## **With global health** challenges on the rise, \n how can we bolster immunity and improve healthcare systems worldwide?',
        'icon': ':material/immunology:'
    }
}

if "votes" not in st.session_state:
    st.session_state["votes"] = {}

if "current_pathway" not in st.session_state:
    st.session_state["current_pathway"] = None

@st.dialog("Vote", width="small")
def vote_callback(description, id):
    # st.session_state["current_pathway"] = None
    
    st.session_state["current_pathway"] = id
    st.markdown(description)

    st.write(f"current_pathway {st.session_state["current_pathway"]}")
    st.write(f"current_pathway {id}")

    if id not in st.session_state["votes"]:
        st.session_state["votes"][id] = 0

    st.write(f"Votes: {st.session_state['votes'][id]}")

    # Button to register the vote
    if st.button("Vote", 
                    key=f"vote_button_{id}", 
                    help="Click to vote for this pathway", 
                    use_container_width=True):
        # Increment the vote count for the specific item
        st.session_state["votes"][id] += 1
        
    if st.button("Done with voting", key=f"close_button_{id}", use_container_width=True, type="primary"):
        st.session_state["current_pathway"] = None
        st.rerun()

def show_pathways():
    links_row = row(len(conceptual_questions)//3, vertical_align="center")
    
    st.session_state["current_pathway"] = None
    
    st.write(f"current_pathway {st.session_state["current_pathway"]}")

    for id, (pathway, details) in enumerate(conceptual_questions.items(), start=1):
        icon = details['icon']
        description = details['description'] 

        button_text = f"{icon}"
        links_row.button(button_text, help=description, key=pathway, on_click = vote_callback, args = (description, id))
    
    st.write('''<style>
        [data-testid="stVerticalBlock"] [data-testid="baseButton-secondary"] p {
            font-size: 4rem;
            padding: 1rem;
        }
    </style>''', unsafe_allow_html=True)
    
show_pathways()
st.write(st.session_state["votes"])
# Display the dialog with the selected pathway's information
st.write(f"current_pathway {st.session_state["current_pathway"]}")

if st.session_state["current_pathway"] is not None:
    current_id = st.session_state["current_pathway"]
    current_description = conceptual_questions[list(conceptual_questions.keys())[current_id-1]]['description']
    st.dialog(f"Vote {current_id}", width="small").markdown(current_description)

    # Display the current vote count
    st.write(f"Votes: {st.session_state['votes'][current_id]}")

    # Button to register another vote
    if st.button("Vote", key=f"vote_button_{current_id}"):
        vote_callback(current_id)
