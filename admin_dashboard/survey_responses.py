import streamlit as st
import pandas as pd
from utils.create_database_tables import get_survey_data, fetch_survey_responses


def show_survey_responses():
    st.header("📋 Survey Responses")

    # Input for Survey ID
    survey_id = st.text_input(
        "Enter Survey ID", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000"
    )

    if st.button("Retrieve Survey Data"):
        if survey_id:
            with st.spinner("Retrieving survey data..."):
                # Fetch the survey data (title, description, questions, etc.)
                survey_data = get_survey_data(survey_id)
                if survey_data:
                    st.success("Survey data retrieved successfully!")

                    # Access trainer questions responses data safely
                    trainer_input = survey_data.get("trainer_questions_responses", {})

                    # Display survey details with default values if keys are missing
                    st.subheader("Survey Details")
                    st.write(
                        f"**Title**: {trainer_input.get('surveyTitle', 'No Title Available')}"
                    )
                    st.write(
                        f"**Description**: {trainer_input.get('surveyDescription', 'No Description Available')}"
                    )
                    st.write(
                        f"**Instructions**: {trainer_input.get('surveyInstructions', 'No Instructions Available')}"
                    )
                    st.write(
                        f"**Trainer Username**: {survey_data.get('trainer_username', 'N/A')}"
                    )
                    st.write(f"**Created At**: {survey_data.get('created_at', 'N/A')}")
                    st.write(
                        f"**Expiration Date**: {survey_data.get('expiration_datetime', 'N/A')}"
                    )

                    # Fetch trainee responses
                    st.subheader("Trainee Responses")
                    responses = fetch_survey_responses(survey_id)
                    if responses:
                        for response in responses:
                            with st.expander(
                                f"Trainee: {response['trainee_email']} | Submitted At: {response['submission_datetime']}"
                            ):

                                # Display profile responses in table format
                                st.markdown("### Profile Information")
                                profile_data = response["trainee_responses"].get(
                                    "profile", {}
                                )
                                profile_table = pd.DataFrame(
                                    [
                                        {
                                            "Question": item["question"],
                                            "Answer": item["answer"],
                                        }
                                        for key, item in profile_data.items()
                                    ]
                                )
                                st.table(profile_table)

                                # Display survey responses in table format
                                st.markdown("### Survey Responses")
                                survey_data = response["trainee_responses"].get(
                                    "survey", {}
                                )
                                survey_table = pd.DataFrame(
                                    [
                                        {
                                            "Question": item["question"],
                                            "Answer": item["answer"],
                                        }
                                        for key, item in survey_data.items()
                                    ]
                                )
                                st.table(survey_table)

                    else:
                        st.info("No responses available for this survey.")
                else:
                    st.error("Survey data not found. Please check the Survey ID.")
        else:
            st.warning("Please enter a valid Survey ID.")
