"""Lab 2.5 STARTER — Streamlit chat page that calls the Lab 2.4 /chat.

Start Lab 2.4 first (port 8002), then from the aeroguard folder:
    streamlit run labs/day2/starter/lab2_5_streamlit_chat.py
Fill in every TODO. Solution: labs/day2/lab2_5_streamlit_chat.py
"""
import os

import requests  # noqa: F401
import streamlit as st

API = os.getenv("LAB_API_URL", "http://localhost:8002")

st.title("AeroGuard v1 — Maintenance Assistant")
st.caption("Advisory only: a certificated person decides.")

if "history" not in st.session_state:
    st.session_state.history = []  # (role, text) pairs

for role, text in st.session_state.history:
    st.chat_message(role).write(text)

question = st.chat_input("Ask about a maintenance write-up")
if question:
    st.chat_message("user").write(question)
    st.session_state.history.append(("user", question))
    # TODO step 1: requests.post(f"{API}/chat",
    #   json={"message": question}, timeout=120), then show
    #   r.json()["answer"] with st.chat_message("assistant") and
    #   append ("assistant", answer) to the history.
    # TODO step 2: wrap the call in try/except:
    #   requests.ConnectionError -> st.error("Cannot reach the
    #   backend ... Is uvicorn running?"); other request errors ->
    #   st.error with the reason. The page must never crash.
    st.info("TODO: call the backend here (steps 1 and 2).")
