import streamlit as st

# Dummy user data; replace with a database or secure auth system for production
USER_DATA = {
    "admin": "password123",
    "trainer": "trainerpass"
}

def authenticate(username, password):
    if username in USER_DATA and USER_DATA[username] == password:
        return True
    return False

def login():
    st.session_state["logged_in"] = True

def logout():
    st.session_state["logged_in"] = False
