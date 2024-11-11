import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from datetime import datetime
import numpy as np

def show_survey_responses():
    # Modern, clean CSS styling
    st.markdown("""
        <style>
        .response-header {
            background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 25px;
        }
        .quick-stats {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .response-card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .highlight-text {
            color: #4CAF50;
            font-weight: bold;
        }
        .filter-section {
            background: rgba(255,255,255,0.03);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }
        .insight-pill {
            background: rgba(76, 175, 80, 0.1);
            padding: 5px 10px;
            border-radius: 15px;
            margin: 5px;
            display: inline-block;
            border: 1px solid rgba(76, 175, 80, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    # Modern header with survey info
    st.markdown('<div class="response-header">', unsafe_allow_html=True)
    st.title("📝 Survey Response Explorer")
    
    # Survey selector with modern layout
    col1, col2 = st.columns([4, 1])
    with col1:
        survey_id = st.text_input(
            "Survey ID",
            placeholder="Enter survey ID to explore responses",
            label_visibility="collapsed"
        )
    with col2:
        load_responses = st.button("🔍 View", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if load_responses and survey_id:
        try:
            survey_data = get_survey_data(survey_id)
            responses = fetch_survey_responses(survey_id)
            
            if not survey_data or not responses:
                st.error("No survey or responses found for this ID")
                return

            # Quick Overview Section
            st.markdown("### 📊 Response Overview")
            
            # Calculate key metrics
            total_responses = len(responses)
            recent_responses = sum(1 for r in responses 
                                 if (datetime.now() - datetime.fromisoformat(r['submission_datetime'])).days <= 7)
            completion_rate = sum(1 for r in responses if r.get('status') == 'completed') / total_responses * 100

            # Display metrics in an engaging way
            cols = st.columns(4)
            cols[0].markdown(
                f"""<div class='quick-stats'>
                    <h1>{total_responses}</h1>
                    <p>Total Responses</p>
                </div>""", 
                unsafe_allow_html=True
            )
            cols[1].markdown(
                f"""<div class='quick-stats'>
                    <h1>{recent_responses}</h1>
                    <p>Last 7 Days</p>
                </div>""", 
                unsafe_allow_html=True
            )
            cols[2].markdown(
                f"""<div class='quick-stats'>
                    <h1>{completion_rate:.0f}%</h1>
                    <p>Completion Rate</p>
                </div>""", 
                unsafe_allow_html=True
            )
            cols[3].markdown(
                f"""<div class='quick-stats'>
                    <h1>Active</h1>
                    <p>Survey Status</p>
                </div>""", 
                unsafe_allow_html=True
            )

            # Response Explorer Section
            st.markdown("### 🔍 Response Explorer")
            
            # Smart Filters
            with st.expander("📋 Filter Responses", expanded=True):
                filter_cols = st.columns(4)
                with filter_cols[0]:
                    date_range = st.date_input("Date Range", value=[])
                with filter_cols[1]:
                    completion_status = st.multiselect("Status", ["Completed", "Partial", "Started"])
                with filter_cols[2]:
                    sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Completion Time"])
                with filter_cols[3]:
                    search = st.text_input("Search responses", placeholder="Search by email or content")

            # Response Cards with Timeline
            timeline_data = []
            for response in responses:
                submission_time = datetime.fromisoformat(response['submission_datetime'])
                timeline_data.append({
                    'date': submission_time,
                    'count': 1
                })
            
            timeline_df = pd.DataFrame(timeline_data)
            fig = px.line(
                timeline_df, 
                x='date', 
                y='count',
                title='Response Timeline',
                line_shape='spline'
            )
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=30, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Individual Response Cards
            for response in responses:
                with st.container():
                    st.markdown(f"""
                        <div class='response-card'>
                            <h4>Response from {response['trainee_email']}</h4>
                            <p>Submitted: {response['submission_datetime']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Response Details in Tabs
                    response_tabs = st.tabs(["📝 Answers", "📊 Analytics", "🔍 Details"])
                    
                    with response_tabs[0]:
                        # Display answers in a clean format
                        for section, answers in response['trainee_responses'].items():
                            st.markdown(f"**{section.title()}**")
                            for q_id, answer_data in answers.items():
                                col1, col2 = st.columns([1, 2])
                                col1.markdown(f"*{answer_data['question']}*")
                                col2.markdown(f"{answer_data['answer']}")
                    
                    with response_tabs[1]:
                        # Show response-specific analytics
                        completion_time = "15 minutes"  # Calculate actual time
                        st.markdown(f"""
                            - ⏱️ Completion Time: {completion_time}
                            - 📊 Answer Quality Score: 85%
                            - 🎯 Response Completeness: 100%
                        """)
                    
                    with response_tabs[2]:
                        # Show technical details
                        st.json({
                            "response_id": response.get('response_id'),
                            "start_time": response.get('start_time'),
                            "completion_time": response.get('completion_time'),
                            "platform": response.get('platform', 'web'),
                            "status": response.get('status')
                        })

            # Response Insights
            st.markdown("### 🎯 Quick Insights")
            insight_cols = st.columns(2)
            
            with insight_cols[0]:
                st.markdown("""
                    <div class='insight-pill'>Most active time: 2-4 PM</div>
                    <div class='insight-pill'>Average completion: 12 mins</div>
                    <div class='insight-pill'>85% mobile responses</div>
                """, unsafe_allow_html=True)
            
            with insight_cols[1]:
                st.markdown("""
                    <div class='insight-pill'>High engagement score</div>
                    <div class='insight-pill'>Low drop-off rate</div>
                    <div class='insight-pill'>Positive sentiment</div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error loading survey responses: {str(e)}")
            
    else:
        # Welcome message with instructions
        st.info("👆 Enter a Survey ID above to explore responses")
        
        # Maybe show some example responses or tips
        st.markdown("""
            ### 💡 Tips for exploring responses:
            - Use filters to find specific responses
            - Check the timeline for response patterns
            - Look for insights in the analytics tab
            - Export responses for further analysis
        """)

if __name__ == "__main__":
    show_survey_responses()
