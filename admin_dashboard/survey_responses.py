import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from datetime import datetime

def show_survey_responses():
    # Enhanced CSS styling
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background-color: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 10px;
        }
        .survey-header {
            background-color: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .response-card {
            background-color: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .metric-container {
            background-color: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Enhanced header
    st.markdown('<div class="survey-header">', unsafe_allow_html=True)
    st.title("📋 Survey Responses Dashboard")
    st.markdown("View and analyze detailed survey responses with insights")
    st.markdown('</div>', unsafe_allow_html=True)

    # Input section with better layout
    col1, col2 = st.columns([4, 1])
    with col1:
        survey_id = st.text_input(
            "Survey ID",
            placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000",
            help="Enter the unique identifier for your survey",
            label_visibility="collapsed"
        )
    with col2:
        retrieve_button = st.button("🔍 Analyze", use_container_width=True)

    if retrieve_button and survey_id:
        with st.spinner("📊 Analyzing survey data..."):
            survey_data = get_survey_data(survey_id)
            if survey_data:
                # Create tabs for better organization
                tabs = st.tabs(["📊 Overview", "👥 Responses", "📈 Analytics"])

                with tabs[0]:
                    # Survey Overview tab
                    trainer_input = survey_data.get("trainer_questions_responses", {})
                    
                    # Display survey metadata in a more organized way
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 📝 Survey Details")
                        st.markdown(f"""
                            **Title**: {trainer_input.get('surveyTitle', 'No Title Available')}  
                            **Description**: {trainer_input.get('surveyDescription', 'No Description Available')}  
                            **Instructions**: {trainer_input.get('surveyInstructions', 'No Instructions Available')}
                        """)
                    
                    with col2:
                        st.markdown("### ⚙️ Survey Metadata")
                        st.markdown(f"""
                            **Trainer**: {survey_data.get('trainer_username', 'N/A')}  
                            **Created**: {survey_data.get('created_at', 'N/A')}  
                            **Expires**: {survey_data.get('expiration_datetime', 'N/A')}
                        """)

                with tabs[1]:
                    # Responses tab
                    responses = fetch_survey_responses(survey_id)
                    if responses:
                        # Add response metrics
                        metrics_cols = st.columns(4)
                        total_responses = len(responses)
                        avg_completion_time = 15  # Calculate this based on actual data
                        
                        metrics_cols[0].metric("Total Responses", total_responses)
                        metrics_cols[1].metric("Avg. Completion Time", f"{avg_completion_time}min")
                        metrics_cols[2].metric("Response Rate", "85%")  # Calculate this
                        metrics_cols[3].metric("Completion Rate", "95%")  # Calculate this

                        # Response Timeline
                        response_dates = [datetime.fromisoformat(r.get('submission_datetime', '')) for r in responses]
                        timeline_df = pd.DataFrame({'date': response_dates})
                        fig = px.line(timeline_df, x='date', title='Response Timeline')
                        fig.update_layout(showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)

                        # Enhanced response display
                        for response in responses:
                            with st.expander(
                                f"📝 Response from {response['trainee_email']} | {response['submission_datetime']}"
                            ):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("### 👤 Profile Information")
                                    profile_data = response["trainee_responses"].get("profile", {})
                                    profile_table = pd.DataFrame(
                                        [{"Question": item["question"], "Answer": item["answer"]}
                                         for key, item in profile_data.items()]
                                    )
                                    st.table(profile_table)

                                with col2:
                                    st.markdown("### 📋 Survey Responses")
                                    survey_data = response["trainee_responses"].get("survey", {})
                                    survey_table = pd.DataFrame(
                                        [{"Question": item["question"], "Answer": item["answer"]}
                                         for key, item in survey_data.items()]
                                    )
                                    st.table(survey_table)

                with tabs[2]:
                    # Analytics tab
                    if responses:
                        st.markdown("### 📊 Response Analytics")
                        
                        # Create word cloud from text responses
                        st.markdown("#### 🔤 Common Response Terms")
                        # Add word cloud visualization here
                        
                        # Response patterns
                        st.markdown("#### 📈 Response Patterns")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Add daily response distribution
                            st.markdown("Daily Response Distribution")
                            # Add visualization
                            
                        with col2:
                            # Add completion time distribution
                            st.markdown("Completion Time Distribution")
                            # Add visualization

                    else:
                        st.info("No responses available for analytics.")

            else:
                st.error("❌ Survey not found. Please check the Survey ID.")
    else:
        st.info("👆 Enter a Survey ID and click Analyze to view responses.")

if __name__ == "__main__":
    show_survey_responses()
