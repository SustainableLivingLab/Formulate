import streamlit as st
import pandas as pd
from utils.create_database_tables import fetch_survey_responses, get_survey_data
from ai.ai_service import generate_AI_summarisation
import json


def show_survey_recommendations():
    st.header("📈 Survey Recommendations")

    # Input for Survey ID
    survey_id = st.text_input("Enter Survey ID", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000")

    # Retrieve Survey Data and Responses on button click
    if st.button("Generate Recommendations"):
        if survey_id:
            with st.spinner("Retrieving data and generating recommendations..."):
                # Fetch survey data (title, description, questions, etc.)
                survey_data = get_survey_data(survey_id)
                if survey_data:
                    st.success("Survey data retrieved successfully!")

                    # Fetch trainee responses for the survey
                    responses = fetch_survey_responses(survey_id)
                    if responses:
                        # Format responses for AI processing
                        formatted_responses = {
                            "responses": [
                                {
                                    "trainee_email": response["trainee_email"],
                                    "trainee_responses": response["trainee_responses"]["survey"]
                                }
                                for response in responses
                            ]
                        }
                        # Call AI function to analyze responses and generate recommendations
                        ai_summarization = generate_AI_summarisation(json.dumps(formatted_responses))

                        if ai_summarization:
                            # Parse AI summarization JSON into a Python dictionary
                            recommendations = json.loads(ai_summarization)
                            
                            # Extract Survey Outcomes and Modifications into separate lists
                            survey_outcomes = recommendations["Summarisation"][0]["Survey outcome"]
                            recommended_modifications = recommendations["Summarisation"][0]["Recommended Modification to learning Objectives"]
                            
                            # Create a DataFrame for a cleaner table display
                            max_len = max(len(survey_outcomes), len(recommended_modifications))
                            survey_outcomes.extend([""] * (max_len - len(survey_outcomes)))
                            recommended_modifications.extend([""] * (max_len - len(recommended_modifications)))
                            df = pd.DataFrame({
                                "Survey Outcomes": survey_outcomes,
                                "Recommended Modifications to Learning Objectives": recommended_modifications
                            })
                            
                            # Display the DataFrame as a table
                            st.subheader("Recommendations Table")
                            st.table(df)
                        else:
                            st.error("Failed to generate recommendations. Please try again.")
                    else:
                        st.info("No responses available for this survey.")
                else:
                    st.error("Survey data not found. Please check the Survey ID.")
        else:
            st.warning("Please enter a valid Survey ID.")

# Run the function to display the page
if __name__ == "__main__":
    show_survey_recommendations()
