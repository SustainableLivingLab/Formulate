import streamlit as st
from utils.create_database_tables import get_survey_data, insert_response_data
from ai.ai_service import generate_survey_questions  # Updated import
import json
from pathlib import Path
import os

# Get project root directory (parent of pages/)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# Create directories relative to root
Path(os.path.join(ROOT_DIR, "survey_jsons")).mkdir(exist_ok=True)
Path(os.path.join(ROOT_DIR, "responses")).mkdir(exist_ok=True)

# Add this near the top of the file, after the imports
st.set_page_config(
    page_title="Training Survey",
    page_icon="🎯",
    initial_sidebar_state="collapsed"  # This hides the sidebar
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
            
        with open(file_path, 'r') as file:
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
    """Render a multiple choice question."""
    return st.radio(
        question["question_text"],
        options=question["options"],
        key=f"mc_{question['question_text']}"
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

# def render_likert_scale(question):
#     """Render a Likert scale question."""
#     scale = question["scale"]
#     return st.select_slider(
#         question["question_text"],
#         options=scale["range"],
#         format_func=lambda x: f"{x} - {scale['max_label'] if x == max(scale['range']) else scale['min_label'] if x == min(scale['range']) else ''}",
#         key=f"ls_{question['question_text']}"
#     )

def render_likert_scale(question):
    """Render a Likert scale question with numerical labels and specific text at the ends."""
    scale = question["scale"]
    st.write(question["question_text"])  # Display question text above slider
    
    return st.select_slider(
        label="",
        options=scale["range"],
        format_func=lambda x: f"{scale['min_label'] if x == min(scale['range']) else scale['max_label'] if x == max(scale['range']) else x}",
        key=f"ls_{question['question_text']}"
    )

def render_open_ended(question):
    """Render an open-ended question."""
    return st.text_area(
        question["question_text"],
        placeholder="Please share your thoughts here...",
        key=f"oe_{question['question_text']}"
    )

def get_profile_questions():
    """Return the static profile questions"""
    return {
        "questions": [
            {
                "type": "open_ended",
                "question_text": "What is your full name?"
            },
            {
                "type": "open_ended",
                "question_text": "What department do you belong to?"
            },
            {
                "type": "multiple_choice",
                "question_text": "How many years of teaching experience do you have?",
                "options": ["Less than 1 year", "1-3 years", "3-5 years", "More than 5 years"]
            },
            {
                "type": "multiple_choice",
                "question_text": "What is the highest degree you have attained?",
                "options": ["Bachelor's", "Master's", "PhD", "Other"]
            },
            {
                "type": "multiple_choice",
                "question_text": "How comfortable are you with using technology in your teaching?",
                "options": ["Not comfortable", "Somewhat comfortable", "Very comfortable"]
            },
            {
                "type": "checkbox",
                "question_text": "Which digital tools or platforms do you commonly use in your classes? (Select all that apply)",
                "options": ["Learning Management Systems", "Online Quiz Tools", "Virtual Whiteboards", "None of the above"]
            },
            {
                "type": "likert_scale",
                "question_text": "How important is improving your digital literacy skills for your teaching?",
                "scale": {
                    "min_label": "Not important",
                    "max_label": "Very important",
                    "range": [1, 2, 3, 4, 5]
                }
            },
            {
                "type": "open_ended",
                "question_text": "What are your primary goals for participating in this training?"
            }
        ]
    }

def main():
    # Get survey ID from URL parameters
    survey_id = st.query_params.get("id", None)
    print(f"Received survey ID: {survey_id}")  # Debug log
    
    if not survey_id:
        st.error("No survey ID provided.")
        return
        
    # Get trainee email first
    st.title("Training Survey")
    email = st.text_input("Please enter your email address:", key="email_input")
    
    if not email:
        st.warning("Please enter your email address to proceed.")
        return
        
    # Get survey data and check expiration
    survey_data = get_survey_data(survey_id)
    print(f"Retrieved survey data: {survey_data}")  # Debug log
    
    if not survey_data:
        st.error("Survey not found or has expired.")
        return

    try:
        # Parse the trainer's responses (questionCount is already included from trainer's input)
        trainer_responses = survey_data.get('trainer_questions_responses', {})
        print(f"Trainer responses: {trainer_responses}")  # Debug log
        
        # Generate questions using AI
        generated_questions_json = generate_survey_questions(trainer_responses)
        # Parse the JSON string into a Python dictionary
        generated_questions = json.loads(generated_questions_json)
        # Get the questions array from the response
        questions = generated_questions.get('questions', [])
        print(f"Generated questions: {questions}")  # Debug log
        
    except Exception as e:
        print(f"Error generating questions: {e}")  # Debug log
        st.error("Error generating survey questions. Please try again later.")
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
        
        for i, question in enumerate(questions, 1):  # Changed to use questions from AI response
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
            success = insert_response_data(
                survey_id=survey_id,
                trainee_email=email,
                profile_responses=profile_responses,
                survey_responses=survey_responses
            )
            
            if success:
                st.success("Thank you for completing the survey!")
            else:
                st.error("There was an error submitting your responses. Please try again.")

if __name__ == "__main__":
    main()