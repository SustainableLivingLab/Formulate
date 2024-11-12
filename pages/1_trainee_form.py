import streamlit as st
from utils.create_database_tables import get_survey_data, insert_response_data
import json
from pathlib import Path
import os
from datetime import datetime
import time

# Get project root directory (parent of pages/)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# Create directories relative to root
Path(os.path.join(ROOT_DIR, "survey_jsons")).mkdir(exist_ok=True)
Path(os.path.join(ROOT_DIR, "responses")).mkdir(exist_ok=True)

# Add this near the top of the file, after the imports
st.set_page_config(
    page_title="Training Survey",
    page_icon="./Images/trainer.png",
    initial_sidebar_state="collapsed",  # This hides the sidebar
)

# Hide streamlit default menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
section[data-testid="stSidebar"] {display: none;}
button[kind="header"] {display: none;}
.stDeployButton {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def load_survey_json(file_path=None, survey_id=None):
    """Load survey questions from JSON file."""
    try:
        survey_jsons_dir = os.path.join(ROOT_DIR, "survey_jsons")
        json_files = list(Path(survey_jsons_dir).glob("*.json"))

        if not json_files:
            st.error("No surveys available. Please contact the administrator.")
            return None

        # If no survey_id provided or invalid survey_id, use the first JSON file
        if not survey_id or not any(survey_id == f.stem for f in json_files):
            first_json = json_files[0]
            survey_id = first_json.stem
            st.query_params["id"] = survey_id
            file_path = str(first_json)
        else:
            file_path = os.path.join(survey_jsons_dir, f"{survey_id}.json")

        with open(file_path, "r") as file:
            # First, load the string content
            json_string = json.load(file)
            # Then parse the string content as JSON
            return json.loads(json_string)

    except FileNotFoundError:
        st.error("Survey configuration not found. Please contact the administrator.")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Invalid survey configuration. Error: {str(e)}")
        return None


def render_multiple_choice(question):
    """Render a multiple choice question without default selection."""
    return st.radio(
        question["question_text"],
        options=question["options"],
        index=None,  # This removes default selection
        key=f"mc_{question['question_text']}",
    )


def render_checkbox(question):
    """Render a checkbox question."""
    # Container to store selected options
    selected_options = []

    st.write(question["question_text"])
    # Create a checkbox for each option
    for option in question["options"]:
        if st.checkbox(option, key=f"cb_{question['question_text']}_{option}"):
            selected_options.append(option)

    return selected_options


def render_likert_scale(question):
    """Render a Likert scale question with numerical labels and specific text at the ends."""
    scale = question["scale"]

    # Create a label that combines question text with min/max labels
    label = (
        f"{question['question_text']}\n({scale['min_label']} → {scale['max_label']})"
    )

    return st.select_slider(
        label=label,
        options=scale["range"],
        format_func=lambda x: str(x),  # Simply show the number
        key=f"ls_{question['question_text']}",
    )


def render_open_ended(question):
    """Render an open-ended question with appropriate input field size."""
    # List of questions that should use single-line input
    single_line_questions = [
        "What is your email address?",
        "What is your full name?",
        "What department do you belong to?",
    ]

    if question["question_text"] in single_line_questions:
        return st.text_input(
            question["question_text"],
            placeholder="Please share your thoughts here...",
            key=f"oe_{question['question_text']}",
        )
    else:
        return st.text_area(
            question["question_text"],
            placeholder="Please share your thoughts here...",
            key=f"oe_{question['question_text']}",
        )


def get_profile_questions():
    """Return a versatile set of profile questions suitable for diverse audiences, including students, teachers, and professionals."""
    return {
        "questions": [
            {
                "type": "open_ended",
                "question_text": "What is your full name?",
                "required": True,
            },
            {
                "type": "open_ended",
                "question_text": "What is your email address?",
                "required": True,
            },
            {
                "type": "open_ended",
                "question_text": "What is your current role or grade level? (e.g., Student - Grade 10, Teacher, Manager)",
                "required": True,
            },
            {
                "type": "open_ended",
                "question_text": "Which school, organization, or institution are you currently part of?",
                "required": True,
            },
            {
                "type": "multiple_choice",
                "question_text": "What is your primary reason for joining this training?",
                "options": [
                    "To gain new skills",
                    "To improve existing knowledge",
                    "For academic requirements",
                    "For career advancement",
                    "Out of general interest",
                    "Other",
                ],
            },
            {
                "type": "multiple_choice",
                "question_text": "How would you describe your familiarity with the topic of this training?",
                "options": [
                    "Beginner",
                    "Somewhat familiar",
                    "Knowledgeable",
                    "Very experienced",
                ],
            },
            {
                "type": "checkbox",
                "question_text": "What types of learning activities do you find most engaging? (Select all that apply)",
                "options": [
                    "Hands-on activities",
                    "Group discussions",
                    "Independent study",
                    "Visual presentations",
                    "Quizzes and interactive exercises",
                    "Other",
                ],
            },
            {
                "type": "likert_scale",
                "question_text": "How confident do you feel about learning new material on this topic?",
                "scale": {
                    "min_label": "Not confident",
                    "max_label": "Very confident",
                    "range": [1, 2, 3, 4, 5],
                },
            },
            {
                "type": "open_ended",
                "question_text": "Are there specific topics or skills you hope to learn in this training?",
            },
            {
                "type": "checkbox",
                "question_text": "What challenges, if any, have you faced in learning similar topics before? (Select all that apply)",
                "options": [
                    "Difficulty understanding complex ideas",
                    "Limited practical experience",
                    "Lack of support or resources",
                    "Staying motivated",
                    "Time constraints",
                    "No challenges faced",
                ],
            },
            {
                "type": "likert_scale",
                "question_text": "How comfortable are you with using digital tools or online platforms for learning?",
                "scale": {
                    "min_label": "Not comfortable",
                    "max_label": "Very comfortable",
                    "range": [1, 2, 3, 4, 5],
                },
            },
            {
                "type": "open_ended",
                "question_text": "What personal goals or achievements do you hope to gain from this training?",
            },
        ]
    }


def show_thank_you_message():
    # Create a centered container for the thank you message
    thank_you_container = st.empty()
    with thank_you_container.container():
        st.success("Thank you for completing the survey!")
        st.write("Your responses have been recorded successfully.")
        st.write("You may close this window now.")

        # Add some styling to center the message
        st.markdown(
            """
            <style>
            .stSuccess {
                text-align: center;
                padding: 2rem;
                margin: 2rem auto;
                max-width: 500px;
            }
            p {
                text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


def main():
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

    if st.session_state.form_submitted:
        show_thank_you_message()
        return

    # Get survey ID from URL parameters
    survey_id = st.query_params.get("id", None)
    print(f"DEBUG: Received survey ID: {survey_id}")

    if not survey_id:
        st.error("No survey ID provided.")
        return

    # Get survey data - only make one database call
    if "survey_data" not in st.session_state:
        st.session_state.survey_data = get_survey_data(survey_id)

    survey_data = st.session_state.survey_data
    print(f"DEBUG: Full survey data: {survey_data}")

    if not survey_data:
        st.error("Survey not found or has expired.")
        return

    # Check expiration status
    if survey_data["is_expired"]:
        st.error("This survey has expired.")
        expiry_date = survey_data["expiration_datetime"]
        st.info(f"Survey expired on: {expiry_date.strftime('%Y-%m-%d %H:%M')}")
        return

    try:
        trainer_input = survey_data.get("trainer_questions_responses", {})
        print(f"DEBUG: Parsed trainer input: {trainer_input}")

        # Display survey header
        st.title(trainer_input.get("surveyTitle", "Training Survey"))

        if trainer_input.get("surveyDescription"):
            st.markdown("### About this Survey")
            st.info(trainer_input["surveyDescription"])

        if trainer_input.get("surveyInstructions"):
            st.markdown("### Instructions")
            st.warning(trainer_input["surveyInstructions"])

        st.markdown("---")

        # Get questions for the form
        questions = survey_data.get("generated_questions", {}).get("questions", [])

    except Exception as e:
        print(f"Error processing questions: {e}")  # Debug log
        st.error("Error loading survey questions. Please try again later.")
        return

    # Create form
    with st.form("survey_form"):
        # Profile Questions Section
        st.header("Profile Information")
        profile_responses = {}
        profile_questions = get_profile_questions()

        for i, question in enumerate(profile_questions["questions"], 1):
            st.subheader(f"Question {i}")
            question_type = question["type"]

            if question_type == "multiple_choice":
                response = render_multiple_choice(question)
            elif question_type == "checkbox":
                response = render_checkbox(question)
            elif question_type == "likert_scale":
                response = render_likert_scale(question)
            elif question_type == "open_ended":
                response = render_open_ended(question)

            profile_responses[f"Q{i}"] = response
            st.markdown("---")

        # Survey Questions Section
        st.header("Survey Questions")
        survey_responses = {}

        for i, question in enumerate(
            questions, 1
        ):  # Changed to use questions from AI response
            st.subheader(f"Question {i}")
            question_type = question["type"].lower()  # Ensure lowercase for matching

            if question_type == "multiple_choice":
                response = render_multiple_choice(question)
            elif question_type == "checkbox":
                response = render_checkbox(question)
            elif question_type == "likert_scale":
                response = render_likert_scale(question)
            elif question_type == "open_ended":
                response = render_open_ended(question)

            survey_responses[f"Q{i}"] = response
            st.markdown("---")

        # Submit button
        if st.form_submit_button("Submit Survey"):
            trainee_email = profile_responses.get("Q1", "")

            if not trainee_email:
                st.error("Please provide your email address.")
                return

            # Format profile responses with questions
            profile_responses_with_questions = {
                f"Q{i+1}": {
                    "question": profile_questions["questions"][i]["question_text"],
                    "type": profile_questions["questions"][i]["type"],
                    "answer": response,
                }
                for i, (_, response) in enumerate(profile_responses.items())
            }

            # Format survey responses with complete question data
            survey_responses_with_questions = {
                f"Q{i+1}": {
                    "question": questions[i]["question_text"],
                    "type": questions[i]["type"],
                    "options": questions[i].get(
                        "options", []
                    ),  # For multiple choice/checkbox
                    "scale": questions[i].get("scale", {}),  # For Likert scale
                    "answer": response,
                }
                for i, (_, response) in enumerate(survey_responses.items())
            }

            # Remove email from profile responses to avoid duplication
            profile_responses_without_email = {
                k: v for k, v in profile_responses_with_questions.items() if k != "Q1"
            }

            # Final combined response structure
            combined_responses = {
                "profile": profile_responses_without_email,
                "survey": survey_responses_with_questions,
                "metadata": {
                    "submission_datetime": str(datetime.now()),
                    "survey_id": survey_id,
                },
            }

            # Insert into database
            success = insert_response_data(
                survey_id=survey_id,
                trainee_email=trainee_email,
                trainee_responses=combined_responses,
            )

            if success:
                st.session_state.form_submitted = True
                show_thank_you_message()
            else:
                st.error(
                    "There was an error submitting your responses. Please try again."
                )


if __name__ == "__main__":
    main()
