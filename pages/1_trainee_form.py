import streamlit as st
from utils.create_database_tables import get_survey_data, insert_response_data
import json
from pathlib import Path
import os
from datetime import datetime
import time
import random

# Get project root directory (parent of pages/)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# Create directories relative to root
Path(os.path.join(ROOT_DIR, "survey_jsons")).mkdir(exist_ok=True)
Path(os.path.join(ROOT_DIR, "responses")).mkdir(exist_ok=True)

# Set page configuration with title and icon
st.set_page_config(
    page_title="Training Survey",
    page_icon="./Images/trainer.png",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit default menu and footer
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
            st.error("🚫 No surveys available. Please contact the administrator.")
            return None

        if not survey_id or not any(survey_id == f.stem for f in json_files):
            first_json = json_files[0]
            survey_id = first_json.stem
            st.query_params["id"] = survey_id
            file_path = str(first_json)
        else:
            file_path = os.path.join(survey_jsons_dir, f"{survey_id}.json")

        with open(file_path, "r") as file:
            json_string = json.load(file)
            return json.loads(json_string)

    except FileNotFoundError:
        st.error("🚫 Survey configuration not found. Please contact the administrator.")
        return None
    except json.JSONDecodeError as e:
        st.error(f"🚫 Invalid survey configuration. Error: {str(e)}")
        return None


def render_multiple_choice(question):
    return st.radio(
        f"{question['question_text']}",
        options=question["options"],
        index=None,
        key=f"mc_{question['question_text']}",
    )


def render_checkbox(question):
    selected_options = []
    st.write(f"{question['question_text']}")
    for option in question["options"]:
        if st.checkbox(option, key=f"cb_{question['question_text']}_{option}"):
            selected_options.append(option)
    return selected_options


def render_likert_scale(question):
    scale = question["scale"]
    label = (
        f"{question['question_text']}\n({scale['min_label']} → {scale['max_label']})"
    )
    return st.select_slider(
        label=label,
        options=scale["range"],
        format_func=lambda x: str(x),
        key=f"ls_{question['question_text']}",
    )


def render_open_ended(question):
    single_line_questions = [
        "What is your full name?",
        "What is your email address?",
        "What do you teach in your current role?",
        "Which school, organization, or institution are you affiliated with?",
    ]

    if question["question_text"] in single_line_questions:
        return st.text_input(
            f"{question['question_text']}",
            placeholder="Please share your response...",
            key=f"oe_{question['question_text']}",
        )
    else:
        return st.text_area(
            f"{question['question_text']}",
            placeholder="Please share your response...",
            key=f"oe_{question['question_text']}",
        )


def get_profile_questions():
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
                "question_text": "Which school, organization, or institution are you affiliated with?",
                "required": True,
            },
            {
                "type": "open_ended",
                "question_text": "What do you teach in your current role?",
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
                "required": True,
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
                "required": True,
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
                "required": True,
            },
        ]
    }


def show_thank_you_message():
    """Display a thank you message upon form submission."""
    thank_you_container = st.empty()
    with thank_you_container.container():
        st.success("🎉 Thank you for completing the survey!")
        st.write("Your responses have been recorded successfully.")
        st.write("You may close this window now.")
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

    survey_id = st.query_params.get("id", None)
    if not survey_id:
        st.error("🚫 No survey ID provided.")
        return

    if "survey_data" not in st.session_state:
        st.session_state.survey_data = get_survey_data(survey_id)

    survey_data = st.session_state.survey_data
    if not survey_data:
        st.error("🚫 Survey not found or has expired.")
        return

    if survey_data["is_expired"]:
        st.error("⏳ This survey has expired.")
        expiry_date = survey_data["expiration_datetime"]
        st.info(f"Survey expired on: {expiry_date.strftime('%Y-%m-%d %H:%M')}")
        return

    try:
        trainer_input = survey_data.get("trainer_questions_responses", {})
        st.title(f"📋 {trainer_input.get('surveyTitle', 'Training Survey')}")

        if trainer_input.get("surveyDescription"):
            st.markdown("### 📝 About this Survey")
            st.info(trainer_input["surveyDescription"])

        if trainer_input.get("surveyInstructions"):
            st.markdown("### 📌 Instructions")
            st.warning(trainer_input["surveyInstructions"])

        st.markdown("---")

        # Handle both structure types
        generated_questions = survey_data.get("generated_questions", {})
        if isinstance(generated_questions, dict):
            if "survey" in generated_questions:
                # Handle second structure
                questions = generated_questions["survey"]["questions"]
                # Optionally display additional survey info
                if "title" in generated_questions["survey"]:
                    st.title(generated_questions["survey"]["title"])
                if "description" in generated_questions["survey"]:
                    st.info(generated_questions["survey"]["description"])
                if "instructions" in generated_questions["survey"]:
                    st.warning(generated_questions["survey"]["instructions"])
            else:
                # Handle first structure
                questions = generated_questions.get("questions", [])
        else:
            questions = []

        for question in questions:
            question.setdefault("required", True)

        # Shuffle questions to randomize order
        random.shuffle(questions)
    except Exception as e:
        st.error(f"🚫 Error loading survey questions: {str(e)}")
        return

    with st.form("survey_form"):
        st.header("👤 Profile Information")
        profile_responses = {}
        profile_questions = get_profile_questions()

        incomplete_responses = []

        for i, question in enumerate(profile_questions["questions"], 1):
            st.caption(f"🔹 Question {i}")
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
            if question.get("required") and not response:
                incomplete_responses.append(f"Profile Question {i}")

            st.markdown("---")

        st.header("📋 Survey Questions")
        survey_responses = {}
        for i, question in enumerate(questions, 1):
            st.caption(f"🔸 Question {i}")
            question_type = question["type"].lower()

            if question_type == "multiple_choice":
                response = render_multiple_choice(question)
            elif question_type == "checkbox":
                response = render_checkbox(question)
            elif question_type == "likert_scale":
                response = render_likert_scale(question)
            elif question_type == "open_ended":
                response = render_open_ended(question)

            survey_responses[f"Q{i}"] = response
            if question.get("required") and not response:
                incomplete_responses.append(f"Survey Question {i}")

            st.markdown("---")

        if st.form_submit_button("✅ Submit Survey"):
            if incomplete_responses:
                st.error(
                    f"❗ Please complete all required questions: {', '.join(incomplete_responses)}"
                )
                return

            trainee_email = profile_responses.get("Q2", "")
            if not trainee_email:
                st.error("❗ Please provide your email address.")
                return

            profile_responses_with_questions = {
                f"Q{i+1}": {
                    "question": profile_questions["questions"][i]["question_text"],
                    "type": profile_questions["questions"][i]["type"],
                    "answer": response,
                }
                for i, (_, response) in enumerate(profile_responses.items())
            }
            survey_responses_with_questions = {
                f"Q{i+1}": {
                    "question": questions[i]["question_text"],
                    "type": questions[i]["type"],
                    "options": questions[i].get("options", []),
                    "scale": questions[i].get("scale", {}),
                    "answer": response,
                }
                for i, (_, response) in enumerate(survey_responses.items())
            }

            profile_responses_without_email = {
                k: v for k, v in profile_responses_with_questions.items() if k != "Q2"
            }

            combined_responses = {
                "profile": profile_responses_without_email,
                "survey": survey_responses_with_questions,
                "metadata": {
                    "submission_datetime": str(datetime.now()),
                    "survey_id": survey_id,
                },
            }

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
                    "❗ There was an error submitting your responses. Please try again."
                )


if __name__ == "__main__":
    main()
