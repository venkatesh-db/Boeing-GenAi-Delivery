"""Lab 2.5 — Streamlit chat page that calls the Lab 2.4 /chat.

Start Lab 2.4 first (port 8002), then from the aeroguard folder:
    streamlit run labs/day2/lab2_5_streamlit_chat.py
Starter version: labs/day2/starter/lab2_5_streamlit_chat.py
"""
import os

import requests
import streamlit as st

API = os.getenv("LAB_API_URL", "http://localhost:8002")

st.title("AeroGuard v1 — Maintenance Assistant")
st.caption("Advisory only: a certificated person decides.")

if "history" not in st.session_state:
    st.session_state.history = []  # (role, text) pairs

for role, text in st.session_state.history:
    st.chat_message(role).write(text)

# Step 1: a chat page that calls /chat
question = st.chat_input("Ask about a maintenance write-up")
if question:
    st.chat_message("user").write(question)
    st.session_state.history.append(("user", question))
    try:
        r = requests.post(f"{API}/chat", timeout=120,
                          json={"message": question})
        r.raise_for_status()
        answer = r.json()["answer"]
    # Step 2: show errors nicely when the backend is down
    except requests.ConnectionError:
        st.error(f"Cannot reach the backend at {API}. "
                 "Is uvicorn running?")
    except requests.RequestException as err:
        st.error(f"The backend returned an error: {err}")
    else:
        st.chat_message("assistant").write(answer)
        st.session_state.history.append(("assistant", answer))
