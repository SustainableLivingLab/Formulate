import streamlit as st
import json
from pathlib import Path
import os

# Get project root directory (parent of pages/)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# Create directories relative to root
Path(os.path.join(ROOT_DIR, "survey_jsons")).mkdir(exist_ok=True)
Path(os.path.join(ROOT_DIR, "responses")).mkdir(exist_ok=True)

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
            
            # Update URL with correct survey ID
            st.query_params["id"] = survey_id
            file_path = str(first_json)
        else:
            file_path = os.path.join(survey_jsons_dir, f"{survey_id}.json")
            
        with open(file_path, 'r') as file:
            #print file path in streamlit
            st.write(file_path)
            
            return json.load(file)
    except FileNotFoundError:
        st.error("Survey configuration not found. Please contact the administrator.")
        return None
    except json.JSONDecodeError:
        st.error("Invalid survey configuration. Please contact the administrator.")
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
    # Get survey ID from URL parameters - updated from experimental to stable API
    survey_id = st.query_params.get("id", None)

    # Load survey configuration with survey_id
    survey_data = load_survey_json(survey_id=survey_id)
    
    if not survey_data:
        return

    # Get course title from survey data, fallback to default if not found
    course_title = survey_data.get("course_title", "AI in the Classroom")
    
    # Dynamic title and subtitle
    st.title(f"{course_title} - Pre-Course Survey")
    st.write("Please complete this survey to help us customize the training to your needs.")

    # Dictionary to store responses
    responses = {}

    # Create form
    with st.form("survey_form"):
        # Display analysis data if available
        if "analysed_data" in survey_data:
            st.header("Course Analysis")
            
            for analysis_item in survey_data["analysed_data"]:
                # Course Overview
                st.subheader("Course Overview")
                st.write(analysis_item.get("Course Overview", ""))
                
                # Target Skill Level and Competencies
                st.subheader("Target Skill Level and Competencies")
                st.write(analysis_item.get("Target Skill Level and Competencies", ""))
                
                # Learning Outcome Goals
                st.subheader("Learning Outcome Goals")
                st.write(analysis_item.get("Learning Outcome Goals", ""))
                
                # Challenges and Considerations
                st.subheader("Challenges and Considerations")
                st.write(analysis_item.get("Challenges and Considerations", ""))
                
                # Course Structure
                st.subheader("Course Structure")
                st.write(analysis_item.get("Course Structure", ""))
            
            st.markdown("---")

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