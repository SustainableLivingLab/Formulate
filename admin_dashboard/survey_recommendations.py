import streamlit as st
import pandas as pd
from utils.create_database_tables import fetch_survey_responses, get_survey_data
from ai.ai_service import generate_AI_summarisation
import json


def show_survey_recommendations():
    st.title("📈 Survey Recommendations")
    st.markdown(
        "##### 👉 Obtain insights and actionable recommendations from your survey responses."
    )

    st.write("---")

    # Input for Survey ID
    survey_id = st.text_input(
        "🔍 Enter Survey ID",
        placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000",
        help="📝 Enter the unique Survey ID to retrieve responses and generate recommendations.",
    )

    # Retrieve Survey Data and Responses on button click
    if st.button("🚀 Generate Recommendations"):
        if survey_id:
            with st.spinner("🔄 Retrieving data and generating recommendations..."):
                # Fetch survey data (title, description, questions, etc.)
                survey_data = get_survey_data(survey_id)
                if survey_data:
                    st.success("✅ Survey data retrieved successfully!")
                    st.write("---")

                    # Fetch trainee responses for the survey
                    responses = fetch_survey_responses(survey_id)
                    if responses:
                        # Format responses for AI processing
                        formatted_responses = {
                            "responses": [
                                {
                                    "trainee_email": response["trainee_email"],
                                    "trainee_responses": response["trainee_responses"][
                                        "survey"
                                    ],
                                }
                                for response in responses
                            ]
                        }

                        # Call AI function to analyze responses and generate recommendations
                        ai_summarization = generate_AI_summarisation(
                            json.dumps(formatted_responses)
                        )

                        if ai_summarization:
                            # Parse AI summarization JSON into a Python dictionary
                            recommendations = json.loads(ai_summarization)

                            # Display Survey Outcomes and Recommendations in tabs
                            tab1, tab2, tab3 = st.tabs(
                                [
                                    "📝 Survey Outcomes",
                                    "🔧 Recommended Modifications",
                                    "📌 Additional Observations",
                                ]
                            )

                            # Tab 1: Survey Outcomes
                            with tab1:
                                st.subheader("📝 Survey Outcomes")
                                survey_outcomes = recommendations.get(
                                    "Survey Outcomes", {}
                                )

                                # Display Summary as a table
                                summary_df = pd.DataFrame(
                                    survey_outcomes.get("Summary", []),
                                    columns=["💡 Key Insights"],
                                )
                                st.write(
                                    summary_df.to_html(
                                        index=False, escape=False, justify="left"
                                    ),
                                    unsafe_allow_html=True,
                                )

                                # Display Positive Aspects and Areas for Improvement in separate columns
                                st.markdown("### ⚖️ Balanced Feedback")
                                pos_aspects = survey_outcomes.get(
                                    "Balanced Feedback", {}
                                ).get("Positive Aspects", [])
                                improv_areas = survey_outcomes.get(
                                    "Balanced Feedback", {}
                                ).get("Areas for Improvement", [])

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("#### Positive Aspects")
                                    st.write(
                                        pd.DataFrame(
                                            pos_aspects, columns=["✨ Aspect"]
                                        ).to_html(
                                            index=False, escape=False, justify="left"
                                        ),
                                        unsafe_allow_html=True,
                                    )

                                with col2:
                                    st.markdown("#### Areas for Improvement")
                                    st.write(
                                        pd.DataFrame(
                                            improv_areas,
                                            columns=["⚠️ Area for Improvement"],
                                        ).to_html(
                                            index=False, escape=False, justify="left"
                                        ),
                                        unsafe_allow_html=True,
                                    )

                            # Tab 2: Recommended Modifications
                            with tab2:
                                st.subheader(
                                    "✨ Recommended Modifications to Learning Objectives"
                                )
                                recommended_modifications = recommendations.get(
                                    "Recommended Modifications to Learning Objectives",
                                    [],
                                )

                                if recommended_modifications:
                                    mod_df = pd.DataFrame(recommended_modifications)
                                    st.write(
                                        mod_df.to_html(
                                            index=False, escape=False, justify="left"
                                        ),
                                        unsafe_allow_html=True,
                                    )

                            # Tab 3: Additional Observations
                            with tab3:
                                st.subheader("📌 Additional Observations")
                                additional_observations = recommendations.get(
                                    "Additional Observations", []
                                )

                                if additional_observations:
                                    observations_df = pd.DataFrame(
                                        additional_observations,
                                        columns=["🔍 Observation"],
                                    )
                                    st.write(
                                        observations_df.to_html(
                                            index=False, escape=False, justify="left"
                                        ),
                                        unsafe_allow_html=True,
                                    )
                        else:
                            st.error(
                                "⚠️ Failed to generate recommendations. Please try again."
                            )
                    else:
                        st.info("ℹ️ No responses available for this survey.")
                else:
                    st.error("❌ Survey data not found. Please check the Survey ID.")
        else:
            st.warning("⚠️ Please enter a valid Survey ID.")


# Run the function to display the page
if __name__ == "__main__":
    show_survey_recommendations()
