import streamlit as st
import json
from pathlib import Path

def load_survey_json(file_path):
    """Load survey questions from JSON file."""
    try:
        with open(file_path, 'r') as file:
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
    responses = []
    for option in question["options"]:
        if st.checkbox(option, key=f"cb_{question['question_text']}_{option}"):
            responses.append(option)
    return responses

def render_likert_scale(question):
    """Render a Likert scale question."""
    scale = question["scale"]
    
    # Render slider with only numbers shown above
    value = st.select_slider(
        question["question_text"],
        options=scale["range"],
        format_func=lambda x: str(x),
        key=f"ls_{question['question_text']}"
    )
    
    # Display min and max labels with their numbers, max label aligned to right
    st.markdown(f"{scale['min_label']} <span style='float: right;'>{scale['max_label']}</span>", unsafe_allow_html=True)
    
    return value

def render_open_ended(question):
    """Render an open-ended question."""
    return st.text_area(
        question["question_text"],
        key=f"oe_{question['question_text']}"
    )

def main():
    st.title("AI in the Classroom - Pre-Course Survey")
    st.write("Please complete this survey to help us customize the training to your needs.")

    # Load survey configuration
    survey_data = load_survey_json("sample_input.json")
    
    if not survey_data:
        return

    # Dictionary to store responses
    responses = {}

    # Create form
    with st.form("survey_form"):
        for i, question in enumerate(survey_data["survey_questions"], 1):
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
            response_file = f"responses/survey_response_{timestamp}.json"
            
            # Create responses directory if it doesn't exist
            Path("responses").mkdir(exist_ok=True)
            
            # Save responses
            with open(response_file, "w") as f:
                json.dump(responses, f, indent=2)

if __name__ == "__main__":
    main()