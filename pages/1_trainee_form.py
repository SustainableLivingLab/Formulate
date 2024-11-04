import streamlit as st
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

def main():
    # Get survey ID from URL parameters
    survey_id = st.query_params.get("id", None)

    # Load survey configuration with survey_id
    survey_data = load_survey_json(survey_id=survey_id)
    
    if not survey_data:
        return

    # Set static title since course_title is no longer in JSON
    st.title("Training Survey")
    st.write("Please complete this survey to help us customize the training to your needs.")

    # Dictionary to store responses
    responses = {}

    # Create form
    with st.form("survey_form"):
        # Changed from survey_data["survey_questions"] to survey_data["questions"]
        for i, question in enumerate(survey_data["questions"], 1):
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
            else:
                st.warning(f"Unsupported question type encountered. Please contact the administrator.")
                continue
            
            responses[f"Q{i}"] = response
            st.markdown("---")

        # Submit button
        submitted = st.form_submit_button("Submit Survey")
        
        if submitted:
            st.success("Thank you for completing the survey! Your responses have been recorded.")
            
            # Save responses with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            response_file = os.path.join(ROOT_DIR, "responses", f"survey_response_{timestamp}.json")
            
            # Save responses
            with open(response_file, "w") as f:
                json.dump(responses, f, indent=2)

if __name__ == "__main__":
    main()