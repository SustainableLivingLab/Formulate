from ai.ai_service import generate_survey_questions
from utils.create_database_tables import insert_survey_data
import streamlit as st
import uuid
import json
from datetime import datetime, timedelta


# Add this function to handle URL generation
def get_base_url():
    """Get the base URL for the application."""
    return "https://formulate.streamlit.app"


def show_survey_management():
    # Get trainer_id from session
    trainer_id = 1 if st.session_state.get("username") == "admin" else 2

    st.header("📝 Survey Management")

    # Section for creating a new survey
    with st.expander("✨ Create New Survey"):

        # 1. Survey Title
        st.write("**1. What is the title of the survey?**")
        survey_title = st.text_input(
            "Survey Title",
            placeholder="e.g., Pre-Training Assessment for Digital Literacy Program",
            label_visibility="collapsed",
        )

        # 2. Survey Description
        st.write("**2. Provide a brief description of the survey.**")
        survey_description = st.text_area(
            "Survey Description",
            placeholder="This survey aims to assess trainees' current digital literacy skills before the training session...",
            label_visibility="collapsed",
        )

        # 3. Instructions for Participants
        st.write("**3. Any specific instructions for trainees?**")
        survey_instructions = st.text_area(
            "Instructions",
            placeholder="Please answer all questions to the best of your knowledge to help tailor the training to your needs...",
            label_visibility="collapsed",
        )

        # 4. Course Title
        st.write("**4. What is the title of the training course?**")
        course_title = st.text_input(
            "Course Title",
            placeholder="e.g., Digital Literacy for Educators",
            label_visibility="collapsed",
        )

        # 5. Target Audience
        st.write(
            "**5. Who is the primary audience for this course? (e.g., middle school teachers, corporate managers, healthcare professionals)**"
        )
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Middle school teachers",
            label_visibility="collapsed",
        )

        # 6. Course Overview
        st.write(
            "**6. Provide a brief overview of the course, describing its primary focus and goals.**"
        )
        course_overview = st.text_area(
            "Course Overview",
            placeholder="This course introduces essential digital literacy skills...",
            label_visibility="collapsed",
        )

        # 7. Target Skill Level
        st.write(
            "**7. What is the expected baseline skill level of the trainees? (Choose one)**"
        )
        skill_level = st.selectbox(
            "Target Skill Level",
            ["Beginner", "Intermediate", "Advanced", "Mixed Level"],
            label_visibility="collapsed",
        )

        # 8. Key Competency Areas
        st.write(
            "**8. List 3-5 key competencies that the course will cover, focusing on the primary skills or knowledge areas relevant to the course.**"
        )
        competencies = st.text_area(
            "Key Competency Areas",
            placeholder="e.g., Basic digital literacy concepts\nUse of digital tools in education\nDigital safety and responsible use",
            label_visibility="collapsed",
        )

        # 9. Learning Outcome Goals
        st.write(
            "**9. What are the primary learning outcomes for this course? List 2-3 specific goals that trainees should achieve by the end.**"
        )
        learning_outcomes = st.text_area(
            "Learning Outcome Goals",
            placeholder="e.g., Teachers should understand fundamental digital literacy concepts...",
            label_visibility="collapsed",
        )

        # 10. Expected Application Level
        st.write(
            "**10. Describe the level of understanding or practical application trainees are expected to achieve by the end of the course. (e.g., Familiarity, Understanding, Application, Mastery)**"
        )
        application_level = st.text_input(
            "Expected Application Level",
            placeholder="e.g., Understanding and Application",
            label_visibility="collapsed",
        )

        # 11. Known Pain Points or Challenges
        st.write(
            "**11. List any known challenges or pain points that trainees may face in relation to this course content (optional).**"
        )
        pain_points = st.text_area(
            "Known Pain Points or Challenges",
            placeholder="e.g., Teachers may feel overwhelmed by the fast pace of technology...",
            label_visibility="collapsed",
        )

        # 12. Course Duration and Structure
        st.write(
            "**12. Provide details about the course structure (e.g., number of sessions, duration per session).**"
        )
        course_duration = st.text_input(
            "Course Duration and Structure",
            placeholder="e.g., 3 sessions over 1 week, each session lasting 2 hours",
            label_visibility="collapsed",
        )

        # 13. Number of Survey Questions
        st.write(
            "**13. How many pre-survey questions would you like the AI to generate? (Specify a number)**"
        )
        question_count = st.number_input(
            "Number of Survey Questions",
            min_value=1,
            max_value=50,
            value=10,
            label_visibility="collapsed",
        )

        # Position Expiration Date and Time at the end of the form
        st.write("**Set Survey Expiration**")

        # Set default expiration to 7 days from now at 23:59
        default_date = datetime.now().date() + timedelta(days=7)
        default_time = datetime.strptime("23:59", "%H:%M").time()

        # Display Date and Time input side-by-side using columns
        col1, col2 = st.columns([1, 1])

        with col1:
            expiration_date = st.date_input(
                "Expiration Date",
                value=default_date,
                min_value=datetime.now().date(),
                help="Choose the date when the survey should expire.",
            )

        with col2:
            expiration_time = st.time_input(
                "Expiration Time",
                value=default_time,
                help="Choose the time on the expiration date when the survey should expire.",
            )

        # Combine date and time into a single datetime object
        expiration_datetime = datetime.combine(expiration_date, expiration_time)

        # Generate Survey Questions Button
        if st.button("Generate Survey Questions"):
            if all(
                [
                    course_title,
                    target_audience,
                    course_overview,
                    competencies,
                    learning_outcomes,
                    course_duration,
                    expiration_datetime,
                ]
            ):

                with st.spinner("Generating survey questions..."):
                    # Prepare data for API call
                    survey_data = {
                        "surveyTitle": survey_title,
                        "surveyDescription": survey_description,
                        "surveyInstructions": survey_instructions,
                        "courseTitle": course_title,
                        "targetAudience": target_audience,
                        "courseOverview": course_overview,
                        "targetSkillLevel": skill_level,
                        "keyCompetencies": competencies.split("\n"),
                        "learningOutcomes": learning_outcomes.split("\n"),
                        "expectedApplicationLevel": application_level,
                        "knownPainPoints": (
                            pain_points.split("\n") if pain_points else None
                        ),
                        "courseDuration": course_duration,
                        "questionCount": question_count,
                    }

                    try:
                        # Generate survey questions using GPT-4O
                        ai_generated_questions = generate_survey_questions(survey_data)

                        # Insert into Trainer table
                        success, survey_id = insert_survey_data(
                            trainer_id=trainer_id,
                            trainer_questions_responses=json.dumps(survey_data),
                            expiration_datetime=expiration_datetime,
                            ai_generated_questions=ai_generated_questions,
                        )

                        if success:
                            # Display survey link
                            base_url = "https://formulate.streamlit.app"
                            survey_link = f"{base_url}/trainee_form?id={survey_id}"

                            st.success("Survey created successfully!")
                            st.write("Share this link with trainees:")

                            # Create a container for the link and copy icon
                            st.markdown(
                                f"""
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
                            """,
                                unsafe_allow_html=True,
                            )

                            # Display expiration info
                            st.info(
                                f"This survey will expire on: {expiration_datetime.strftime('%Y-%m-%d %H:%M')}"
                            )
                        else:
                            st.error("Failed to create survey. Please try again.")

                    except Exception as e:
                        st.error(f"Error creating survey: {str(e)}")

            else:
                st.error("Please fill in all required fields to create a survey.")

    # Section for listing active surveys
    st.subheader("Active Surveys")

    # TODO: Implement active surveys listing from database
    # This will require a new database function to fetch active surveys
    st.info("Survey listing feature coming soon!")
