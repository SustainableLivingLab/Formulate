from ai.ai_service import generate_survey_questions
from utils.create_database_tables import insert_survey_data, load_db_config
import streamlit as st
import uuid
import json
from datetime import datetime, timedelta
import logging
import mysql.connector

# Add this function to handle URL generation
def get_base_url():
    """Get the base URL for the application."""
    return "https://formulate.streamlit.app"

# Add this function to test database connection
def test_db_connection():
    try:
        db_config = load_db_config()
        conn = mysql.connector.connect(**db_config)
        logging.debug("Database connection successful")
        return True
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def show_survey_management():
    if not test_db_connection():
        st.error("Database connection failed. Please check your configuration.")
        return
    # Get trainer_id from session
    trainer_id = 1 if st.session_state.get("username") == "admin" else 2
    logging.debug(f"Current trainer_id: {trainer_id}")
    
    st.header("📝 Survey Management")

    # Section for creating a new survey
    with st.expander("✨ Create New Survey"):
        
        # 1. Course Title
        st.write("**1. What is the title of the training course?**")
        course_title = st.text_input("Course Title", placeholder="e.g., Digital Literacy for Educators", label_visibility="collapsed")

        # 2. Target Audience
        st.write("**2. Who is the primary audience for this course? (e.g., middle school teachers, corporate managers, healthcare professionals)**")
        target_audience = st.text_input("Target Audience", placeholder="e.g., Middle school teachers", label_visibility="collapsed")

        # 3. Course Overview
        st.write("**3. Provide a brief overview of the course, describing its primary focus and goals.**")
        course_overview = st.text_area("Course Overview", placeholder="This course introduces essential digital literacy skills...", label_visibility="collapsed")

        # 4. Target Skill Level
        st.write("**4. What is the expected baseline skill level of the trainees? (Choose one)**")
        skill_level = st.selectbox("Target Skill Level", ["Beginner", "Intermediate", "Advanced", "Mixed Level"], label_visibility="collapsed")

        # 5. Key Competency Areas
        st.write("**5. List 3-5 key competencies that the course will cover, focusing on the primary skills or knowledge areas relevant to the course.**")
        competencies = st.text_area("Key Competency Areas", placeholder="e.g., Basic digital literacy concepts\nUse of digital tools in education\nDigital safety and responsible use", label_visibility="collapsed")

        # 6. Learning Outcome Goals
        st.write("**6. What are the primary learning outcomes for this course? List 2-3 specific goals that trainees should achieve by the end.**")
        learning_outcomes = st.text_area("Learning Outcome Goals", placeholder="e.g., Teachers should understand fundamental digital literacy concepts...", label_visibility="collapsed")

        # 7. Expected Application Level
        st.write("**7. Describe the level of understanding or practical application trainees are expected to achieve by the end of the course. (e.g., Familiarity, Understanding, Application, Mastery)**")
        application_level = st.text_input("Expected Application Level", placeholder="e.g., Understanding and Application", label_visibility="collapsed")

        # 8. Known Pain Points or Challenges
        st.write("**8. List any known challenges or pain points that trainees may face in relation to this course content (optional).**")
        pain_points = st.text_area("Known Pain Points or Challenges", placeholder="e.g., Teachers may feel overwhelmed by the fast pace of technology...", label_visibility="collapsed")

        # 9. Course Duration and Structure
        st.write("**9. Provide details about the course structure (e.g., number of sessions, duration per session).**")
        course_duration = st.text_input("Course Duration and Structure", placeholder="e.g., 3 sessions over 1 week, each session lasting 2 hours", label_visibility="collapsed")

        # 10. Number of Survey Questions
        st.write("**10. How many pre-survey questions would you like the AI to generate? (Specify a number)**")
        question_count = st.number_input("Number of Survey Questions", min_value=1, max_value=50, value=10, label_visibility="collapsed")

        # Add expiration datetime fields
        st.write("**11. When should this survey expire?**")
        # Default expiration date is 7 days from now
        default_date = datetime.now().date() + timedelta(days=7)
        expiration_date = st.date_input("Expiration Date", value=default_date, min_value=datetime.now().date())
        # Set default time to 23:59
        default_time = datetime.strptime("23:59", "%H:%M").time()
        expiration_time = st.time_input("Expiration Time", value=default_time)
        
        # Combine date and time into datetime
        expiration_datetime = datetime.combine(expiration_date, expiration_time)

        # Generate Survey Questions Button
        if st.button("Generate Survey Questions"):
            if all([course_title, target_audience, course_overview, competencies, 
                   learning_outcomes, course_duration, expiration_datetime]):
                
                with st.spinner("Generating survey questions..."):
                    # Prepare data for API call
                    survey_data = {
                        "courseTitle": course_title,
                        "targetAudience": target_audience,
                        "courseOverview": course_overview,
                        "targetSkillLevel": skill_level,
                        "keyCompetencies": competencies.split("\n"),
                        "learningOutcomes": learning_outcomes.split("\n"),
                        "expectedApplicationLevel": application_level,
                        "knownPainPoints": pain_points.split("\n") if pain_points else None,
                        "courseDuration": course_duration,
                        "questionCount": question_count
                    }
                    logging.debug(f"Prepared survey_data: {survey_data}")

                    try:
                        # Generate questions using AI
                        logging.debug("Starting AI question generation...")
                        questions = generate_survey_questions(survey_data)
                        logging.debug(f"Generated questions: {questions[:100]}...")  # First 100 chars
                        
                        # Insert into database
                        logging.debug("Attempting database insertion...")
                        success, survey_id = insert_survey_data(
                            trainer_id=trainer_id,
                            trainer_questions_responses=json.dumps(survey_data),
                            expiration_datetime=expiration_datetime
                        )
                        logging.debug(f"Database insertion result - Success: {success}, Survey ID: {survey_id}")
                        
                        if success:
                            base_url = get_base_url()  # Use the function to get base URL
                            survey_link = f"{base_url}/trainee_form?id={survey_id}"
                            logging.debug(f"Generated survey link: {survey_link}")
                            
                            st.success("Survey created successfully!")
                            st.write("Share this link with trainees:")
                            
                            # Create a container for the link and copy icon
                            st.markdown(f"""
                                <div style="display: flex; align-items: center; background-color: #2E7D32; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                    <input type="text" value="{survey_link}" 
                                        style="flex-grow: 1; border: none; background: transparent; padding: 0.5rem; color: white;" 
                                        readonly>
                                    <button onclick="copyToClipboard()" 
                                        style="background: none; border: none; cursor: pointer; padding: 0.5rem; color: white;">
                                        📋
                                    </button>
                                </div>
                                
                                <script>
                                function copyToClipboard() {{
                                    const linkInput = document.querySelector('input[type="text"]');
                                    navigator.clipboard.writeText(linkInput.value)
                                        .then(() => {{
                                            const copyButton = document.querySelector('button');
                                            copyButton.innerHTML = '✓';
                                            setTimeout(() => {{
                                                copyButton.innerHTML = '📋';
                                            }}, 2000);
                                        }})
                                        .catch(err => console.error('Failed to copy:', err));
                                }}
                                </script>
                            """, unsafe_allow_html=True)
                            
                            # Display expiration info
                            st.info(f"This survey will expire on: {expiration_datetime.strftime('%Y-%m-%d %H:%M')}")
                        else:
                            logging.error("Database insertion failed")
                            st.error("Failed to create survey. Please try again.")
                            
                    except Exception as e:
                        logging.exception("Error in survey creation process")
                        st.error(f"Error creating survey: {str(e)}")
                        
            else:
                logging.warning("Missing required fields")
                st.error("Please fill in all required fields to create a survey.")

    # Section for listing active surveys
    st.subheader("Active Surveys")
    
    # TODO: Implement active surveys listing from database
    # This will require a new database function to fetch active surveys
    st.info("Survey listing feature coming soon!")
