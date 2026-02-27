from app.core.config import settings
import streamlit as st
import requests


BACKEND_URL = settings.BACKEND_URL or "http://127.0.0.1:8000"


st.set_page_config(page_title="Enterprise GenAI", layout="wide")
st.title("🚀 Enterprise GenAI Assistant")

if "token" not in st.session_state:
    st.session_state.token = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def register(email, password):
    response = requests.post(f"{BACKEND_URL}/auth/register", json={"email": email, "password": password})

    if response.status_code == 200:
        st.success("Registered successfully. Now login.")
    else:
        st.error(response.json())

def login(email, password):
    response = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        st.session_state.token = response.json()["access_token"]
        st.success("Login successful")
        st.rerun()
    else:
        st.error(response.text)

if st.session_state.token:
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.session_id = None
        st.rerun()

if not st.session_state.token:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            login(email, password)

    with tab2:
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            register(email, password)

    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# Auto-load or auto-create session after login
if st.session_state.token and not st.session_state.session_id:
    # Get user sessions
    response = requests.get(f"{BACKEND_URL}/sessions/my-sessions", headers=headers)
    if response.status_code == 200:
        sessions = response.json()
        if sessions:
            # Open latest session
            latest_session = sessions[0]  # because ordered desc
            st.session_state.session_id = latest_session["id"]
            msg_response = requests.get(f"{BACKEND_URL}/sessions/{latest_session['id']}/messages", headers=headers)

            if msg_response.status_code == 200:
                messages = msg_response.json()
                st.session_state.chat_history = [(m["role"], m["content"]) for m in messages]
        else:
            # No sessions → create one automatically
            create_resp = requests.post(f"{BACKEND_URL}/sessions/create", headers=headers)
            if create_resp.status_code == 200:
                st.session_state.session_id = create_resp.json()["session_id"]
                st.session_state.chat_history = []

        st.rerun()

with st.sidebar:
    st.title("💬 Chats")

    # New Chat Button
    if st.button("➕ New Chat"):
        response = requests.post(f"{BACKEND_URL}/sessions/create", headers=headers)
        if response.status_code == 200:
            st.session_state.session_id = response.json()["session_id"]
            st.session_state.chat_history = []
            st.rerun()

    # Fetch all sessions
    response = requests.get(f"{BACKEND_URL}/sessions/my-sessions", headers=headers)
    if response.status_code == 200:
        sessions = response.json()
        for session in sessions:
            col1, col2, col3 = st.columns([4,1,1])

            # Open session
            with col1:
                if st.button(session["title"], key=f"open_{session['id']}"):
                    st.session_state.session_id = session["id"]
                    msg_response = requests.get(f"{BACKEND_URL}/sessions/{session['id']}/messages", headers=headers)
                    if msg_response.status_code == 200:
                        messages = msg_response.json()
                        st.session_state.chat_history = [(m["role"], m["content"]) for m in messages]
                        st.rerun()

            # Rename button
            with col2:
                if st.button("✏", key=f"rename_{session['id']}"):
                    st.session_state.rename_target = session["id"]

            # Delete icon
            with col3:
                if st.button("🗑", key=f"delete_{session['id']}"):
                    st.session_state.delete_target = session["id"]

        # Delete button
        if "delete_target" in st.session_state:
            st.warning("Are you sure you want to delete this chat?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete"):
                    requests.delete(f"{BACKEND_URL}/sessions/{st.session_state.delete_target}", headers=headers)
                    if st.session_state.session_id == st.session_state.delete_target:
                        st.session_state.session_id = None
                        st.session_state.chat_history = []

                    del st.session_state.delete_target
                    st.rerun()

            with col2:
                if st.button("Cancel"):
                    del st.session_state.delete_target
                    st.rerun()

        if "rename_target" in st.session_state:
            rename_id = st.session_state.rename_target
            new_title = st.text_input("Rename Chat", key="sidebar_rename_input")
            col1, col2 = st.columns(2)

            # Save
            with col1:
                if st.button("Save"):
                    if not new_title.strip():
                        st.warning("Title cannot be empty")
                    else:
                        requests.put(f"{BACKEND_URL}/sessions/{rename_id}/rename", headers=headers, json={"title": new_title.strip()})
                        del st.session_state.rename_target
                        st.rerun()

            # Cancel
            with col2:
                if st.button("Cancel"):
                    del st.session_state.rename_target
                    st.rerun()

st.subheader("📄 Upload Document")

uploaded_file = st.file_uploader("Upload PDF / TXT / CSV")
if uploaded_file and st.button("Upload"):
    files = {"file": uploaded_file.getvalue()}

    response = requests.post(f"{BACKEND_URL}/sessions/upload", headers=headers, files={"file": (uploaded_file.name, uploaded_file.getvalue())})
    if response.status_code == 200:
        st.success("Document Indexed")
    else:
        st.error("Upload Failed")

st.subheader("💬 Chat")

if not st.session_state.session_id:
    st.info("Start a new chat from sidebar")

# Render existing history
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)

# Input
user_input = st.chat_input("Ask something...")
if user_input:
    # Show user message immediately
    st.session_state.chat_history.append(("user", user_input))

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⏳ Generating response...")

        # Call backend
        response = requests.post(f"{BACKEND_URL}/chat/{st.session_state.session_id}", headers=headers, json={"content": user_input})
        if response.status_code == 200:
            data = response.json()
            answer = data["answer"]

            # Typing effect
            full_text = ""
            for word in answer.split():
                full_text += word + " "
                placeholder.markdown(full_text)
                import time
                time.sleep(0.015)

            st.session_state.chat_history.append(("assistant", answer))
            if len(st.session_state.chat_history) == 2:
                st.rerun()
        else:
            placeholder.markdown("❌ Error generating response")
