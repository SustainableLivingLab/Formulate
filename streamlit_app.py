import streamlit as st
from utils.auth import authenticate, login, logout
from admin_dashboard.survey_management import show_survey_management
from admin_dashboard.survey_responses import show_survey_responses

from admin_dashboard import survey_reports, survey_recommendations

st.set_page_config(page_title="Formulate", page_icon="./Images/trainer.png", initial_sidebar_state="collapsed")

# Initialize session state for login status if it doesn't exist
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Enhanced Home Page with Login Functionality
def show_login_page():
    st.title("Welcome to Formulate 📚")
    st.markdown("""
    ### Unlock the Power of Data-Driven Training
    **Formulate** is your all-in-one solution for creating, managing, and analyzing dynamic training surveys. Streamline training needs assessment, customize content to meet trainee expectations, and drive impactful learning outcomes.
    
    > _Effortlessly generate surveys, gather insights, and tailor training programs to maximize engagement and learning effectiveness._
    """)

    st.markdown("#### Log in to Access Your Dashboard")

    # Centered login form
    with st.form(key="login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_button = st.form_submit_button("Log In")

        # Authentication
        if login_button:
            if authenticate(username, password):
                login()
                st.success("You’re now logged in! Redirecting to your dashboard...")
                st.experimental_rerun()  # Refresh the page to show the dashboard
            else:
                st.error("Invalid username or password. Please try again.")

    st.markdown("""
    ---
    **Don’t have an account?** Contact your system administrator to request access.
    """)

# Enhanced Dashboard with Sidebar and Navigation
def show_dashboard():
    st.title("Formulate 📚")

    st.sidebar.image("./Images/trainer.png")
    st.sidebar.header("Formulate - Admin Dashboard")

    # Sidebar navigation
    section = st.sidebar.radio("Select a section", ["📝 Survey Management", "📋 Survey Responses", "📊 Survey Reports", "📈 Survey Recommendations"])

    # Logout button
    if st.sidebar.button("Log Out"):
        logout()
        st.experimental_rerun()  # Refresh the page to show the login form

    # Navigation logic for different sections
    if section == "📝 Survey Management":
        show_survey_management()

    elif section == "📋 Survey Responses":
        show_survey_responses()

    elif section == "📊 Survey Reports":
        survey_reports.show_survey_reports()

    elif section == "📈 Survey Recommendations":
        survey_recommendations.show_survey_recommendations()

# Main Application Flow
if st.session_state["logged_in"]:
    show_dashboard()
else:
    show_login_page()
