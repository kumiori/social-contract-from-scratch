import streamlit as st
from coolname import generate_slug
from datetime import datetime, timedelta
import time
import uuid


# Cache global review sessions (shared across users)
@st.cache_resource
def get_review_sessions():
    """Return the global review sessions."""
    return {}


# Cache the uploaded markdown text so that it is loaded once
@st.cache_data
def load_markdown(file):
    return file.read().decode("utf-8")


with st.sidebar:
    st.write(st.session_state)

if st.button("Clear session state"):
    st.session_state = {}


def initialize_review(mode="solo", board_size=3, paragraphs=None):
    """
    Initialize a new review session.

    Parameters:
      mode: "solo" (collaborative mode) will wait for multiple players.
      paragraphs: List of text paragraphs to review.

    Returns:
      A dictionary representing the session state.
    """
    session = {
        "review_over": False,
        "wait_to_start": mode == "solo",  # Wait for more players if in solo mode.
        "progress": 0,  # Track which paragraph is under review.
        "responses": {},  # Store review responses by paragraph index.
        "players": [],  # List of players in the session.
        "document": paragraphs or [],  # The list of paragraphs from the uploaded file.
    }
    return session


def create_new_review(review_mode="solo", paragraphs=None):
    """Create a new review session with the provided document paragraphs."""
    session_id = generate_slug(2)
    sessions = get_review_sessions()
    sessions[session_id] = initialize_review(
        mode=review_mode, board_size=3, paragraphs=paragraphs
    )
    st.session_state.session_id = session_id
    st.query_params["session_id"] = session_id

    return session_id


def join_review_session(session_id, reviewer_name):
    """Add a player to the review session if not already added."""
    sessions = get_review_sessions()
    with st.expander("Debug", expanded=False):
        st.write(sessions)
        st.write(session_id)
        st.write(reviewer_name)
    if session_id in sessions:
        if reviewer_name not in sessions[session_id]["players"]:
            sessions[session_id]["players"].append(reviewer_name)
            st.session_state.session_id = session_id
            # st.session_state.reviewer_name = reviewer_name
            return True
        __import__("pdb").set_trace()
        return False


def update_review_progress(session_id, new_progress):
    """Update the progress (current paragraph index) for a given session."""
    sessions = get_review_sessions()
    if session_id in sessions:
        sessions[session_id]["progress"] = new_progress


@st.dialog("Terminate")
def terminate_review(session_id):
    """Mark the review as over and return the collected responses."""
    sessions = get_review_sessions()
    st.success("Review terminated and broadcast to all reviewers!")

    st.markdown("### Review Summary")
    if session_id in sessions:
        st.json(sessions[session_id]["responses"])
        sessions[session_id]["review_over"] = True
        return sessions[session_id]["responses"]


# --- Streamlit App ---
st.title("Collaborative Document Review Session")
with st.expander("Debug", expanded=False):
    st.write(st.session_state)
    sessions = get_review_sessions()
    st.write(sessions)
# Step 1: Upload the Markdown File (only the host does this)
uploaded_file = st.file_uploader(
    "Upload the Markdown file to review", type=["md"], key="upload"
)
document_paragraphs = []
if uploaded_file:
    markdown_text = load_markdown(uploaded_file)
    # Split document into paragraphs (using double newline as delimiter)
    document_paragraphs = [p.strip() for p in markdown_text.split("\n\n") if p.strip()]
    st.markdown("### Document Uploaded")
    with st.expander("Click to view", expanded=False):
        st.markdown(markdown_text)

# Step 2: Choose to Create or Join a Session
action = st.radio(
    "Action", ["Create New Review Session", "Join Existing Session"], key="action"
)

# list existing active sessions

if action == "Create New Review Session":
    review_mode = st.selectbox(
        "Review Mode",
        options=[
            "multi",
            "solo",
            "ai",
        ],
        key="review_mode",
    )
    if st.button("Create Session"):
        # If no document is uploaded, warn the user
        if not document_paragraphs:
            st.error("Please upload a Markdown file to create a session.")
        else:
            session_id = create_new_review(review_mode, paragraphs=document_paragraphs)
            st.success(f"Session created with ID: {session_id}")
elif action == "Join Existing Session":
    st.write("Active sessions")
    st.write(sessions.keys())

    session_id_input = st.text_input("Enter Session ID", key="join_session")
    reviewer_name = st.text_input("Your Name", key="reviewer_name")
    if st.button("Join Session") and session_id_input and reviewer_name:
        join_review_session(session_id_input, reviewer_name)
        st.session_state.session_id = session_id_input
        st.success(f"Joined session {session_id_input} as {reviewer_name}")

msg_area = st.empty()

if "session_id" in st.query_params and "session_id" not in st.session_state:
    session_id = st.query_params["session_id"]
    reviewer_name = str(uuid.uuid4())
    st.session_state["reviewer_name"] = reviewer_name
    st.write("Session ID from URL:", session_id)

    if join_review_session(session_id, reviewer_name):
        st.session_state.wait_to_start = False
        st.success("Successfully joined the session!")
        st.balloons()
        # Wait a short while to let users see the success message, then rerun.
        time.sleep(2)
        st.rerun()
    else:
        msg_area.error(f"Session ID **{session_id}** not found. Please try again.")

# Step 3: If a session exists, allow reviewing
if "session_id" in st.session_state:
    sessions = get_review_sessions()
    session_id = st.session_state.session_id
    session_info = sessions.get(session_id, {})
    st.markdown("### Current Session Information")
    st.write("Session ID:", session_id)
    st.write("Progress (current step):", session_info.get("progress"))
    st.progress(session_info.get("progress") / len(session_info.get("document", [])))
    st.write("Active reviewers:", len(session_info.get("players")))
    with st.expander("Debug", expanded=False):
        st.write(session_info.get("players"))
    if "reviewer_name" in st.session_state:
        st.write(f"I am reviewer {st.session_state['reviewer_name']}")
        # st.write("Collected Responses:", session_info.get("responses"))

    # Ensure that the session has a document loaded
    if not session_info.get("document"):
        st.error("No document available in this session.")
    else:
        paragraphs = session_info["document"]
        total = len(paragraphs)
        current_index = session_info.get("progress", 0)
        print(st.session_state)
        st.markdown(f"### Reviewing Paragraph {current_index} of {total}")

        st.markdown(paragraphs[current_index])

        # Provide review options for the current paragraph
        review_options = [
            "Rejected",
            "Accepted as is",
            "Minor modifications",
            "Major modifications",
        ]
        # review = st.radio(
        #     "Review this paragraph", review_options, key=f"review_{current_index}"
        # )
        current_value = session_info["responses"].get(current_index)
        print(f"Default for current_value: {current_value}")
        review_control = st.segmented_control(
            "Review choice",
            review_options,
            default=current_value,
            selection_mode="single",
        )

        st.write(review_control)
        session_info["responses"][current_index] = review_control

        # Navigation buttons
        col_prev, col_next, col_term = st.columns(3)
        msg_area = st.empty()
        with col_prev:
            if st.button("Previous") and current_index > 0:
                update_review_progress(session_id, current_index - 1)
                st.rerun()
        with col_next:
            if st.button("Next") and current_index < total - 1:
                update_review_progress(session_id, current_index + 1)
                st.rerun()
            # else:
            # session_info["review_over"] = True
        with col_term:
            if st.button("Terminate Review"):
                summary = terminate_review(session_id)
                # st.write(summary)
                # msg_area.json(summary)

        st.markdown("### My Review")
        if st.button("Clear review"):
            session_info["responses"] = {}
        st.json(session_info["responses"], expanded=False)
