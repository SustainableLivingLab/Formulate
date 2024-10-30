import streamlit as st
from utils.auth import authenticate, login, logout

from admin_dashboard import survey_management, survey_responses, survey_reports, survey_recommendations

st.set_page_config(page_title="Formulate Admin Dashboard", layout="wide")

# Initialize session state for login status if it doesn't exist
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Home page with login functionality
def show_login_page():
    st.title("Welcome to Formulate")
    st.subheader("Admin Dashboard for Dynamic Survey and Training Management")

    st.write("Log in to access your personalized dashboard, where you can create and manage surveys, review responses, generate reports, and customize training recommendations.")

    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Log In")

    # Authentication
    if login_button:
        if authenticate(username, password):
            login()
            st.success("You’re now logged in! Redirecting to your dashboard...")
            st.experimental_rerun()  # Refresh the page to show the dashboard
        else:
            st.error("Invalid username or password. Please try again.")

def show_dashboard():
    st.title("Formulate - Admin Dashboard")
    st.sidebar.header("Navigation")

    # Logout button
    if st.sidebar.button("Log Out"):
        logout()
        st.experimental_rerun()  # Refresh the page to show the login form

    # Sidebar navigation
    section = st.sidebar.radio("Select a section", ["Survey Management", "Survey Responses", "Survey Reports", "Survey Recommendations"])

    if section == "Survey Management":
        survey_management.show_survey_management()

    elif section == "Survey Responses":
        survey_responses.show_survey_responses()

    elif section == "Survey Reports":
        survey_reports.show_survey_reports()

    elif section == "Survey Recommendations":
        survey_recommendations.show_survey_recommendations()

# Main Application Flow
if st.session_state["logged_in"]:
    show_dashboard()
else:
    show_login_page()
