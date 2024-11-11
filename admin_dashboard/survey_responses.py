import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from datetime import datetime, timedelta
import numpy as np

def parse_datetime(datetime_str):
    """Safely parse datetime string to datetime object"""
    if not datetime_str:
        return None
    try:
        return datetime.fromisoformat(str(datetime_str).replace('Z', '+00:00'))
    except (ValueError, TypeError):
        try:
            return datetime.strptime(str(datetime_str), '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return None

def calculate_time_left(expiry_date):
    """Calculate time left until expiry in days"""
    if not expiry_date:
        return "No expiry set"
    now = datetime.now()
    expiry = parse_datetime(expiry_date)
    if not expiry:
        return "Invalid date"
    if expiry < now:
        return "Expired"
    days_left = (expiry - now).days
    return f"{days_left} days"

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

    # Initialize session state for survey data
    if 'survey_data' not in st.session_state:
        st.session_state.survey_data = None
        st.session_state.responses = None
        st.session_state.filtered_responses = None

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

    # Load survey data only when View button is clicked
    if load_responses and survey_id:
        try:
            st.session_state.survey_data = get_survey_data(survey_id)
            st.session_state.responses = fetch_survey_responses(survey_id)
            if st.session_state.responses:
                st.session_state.filtered_responses = st.session_state.responses.copy()
        except Exception as e:
            st.error(f"Error loading survey data: {str(e)}")

    # Display survey data if available in session state
    if st.session_state.survey_data and st.session_state.responses:
        try:
            survey_data = st.session_state.survey_data
            responses = st.session_state.responses
            
            if not survey_data or not responses:
                st.error("No survey or responses found for this ID")
                return

            # Quick Overview Section
            st.markdown("### 📊 Response Overview")
            
            # Calculate relevant metrics
            total_responses = len(responses)
            recent_responses = sum(1 for r in responses 
                                 if parse_datetime(r.get('submission_datetime')) and 
                                 (datetime.now() - parse_datetime(r.get('submission_datetime'))).days <= 7)

            # Display metrics
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
                    <h1>{len([r for r in responses if parse_datetime(r.get('submission_datetime')).date() == datetime.now().date()])}</h1>
                    <p>Today's Responses</p>
                </div>""", 
                unsafe_allow_html=True
            )
            cols[3].markdown(
                f"""<div class='quick-stats'>
                    <h1>{calculate_time_left(survey_data.get('expiration_datetime'))}</h1>
                    <p>Time Until Expiry</p>
                </div>""", 
                unsafe_allow_html=True
            )

            # Response Explorer Section
            st.markdown("### 🔍 Response Explorer")
            
            # Smart Filters
            with st.expander("📋 Filter Responses", expanded=True):
                filter_cols = st.columns(3)
                with filter_cols[0]:
                    date_range = st.date_input("Date Range", value=[])
                with filter_cols[1]:
                    sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Response Time"])
                with filter_cols[2]:
                    search = st.text_input("Search", placeholder="Search by email or content")

            # Apply filters
            filtered_responses = st.session_state.responses.copy()
            
            # Date filter
            if len(date_range) == 2:
                filtered_responses = [
                    r for r in filtered_responses
                    if date_range[0] <= parse_datetime(r.get('submission_datetime')).date() <= date_range[1]
                ]

            # Search filter
            if search:
                search = search.lower()
                filtered_responses = [
                    r for r in filtered_responses
                    if search in str(r.get('trainee_email', '')).lower() or 
                    search in str(r.get('trainee_responses', {})).lower()
                ]

            # Sort responses
            if sort_by == "Newest First":
                filtered_responses.sort(
                    key=lambda x: parse_datetime(x.get('submission_datetime')) or datetime.min,
                    reverse=True
                )
            elif sort_by == "Oldest First":
                filtered_responses.sort(
                    key=lambda x: parse_datetime(x.get('submission_datetime')) or datetime.min
                )
            elif sort_by == "Response Time":
                filtered_responses.sort(
                    key=lambda x: (
                        parse_datetime(x.get('submission_datetime')) - 
                        parse_datetime(x.get('start_time'))
                    ).total_seconds() if parse_datetime(x.get('submission_datetime')) and 
                    parse_datetime(x.get('start_time')) else float('inf')
                )

            # Timeline visualization
            timeline_data = []
            for response in filtered_responses:
                submission_time = parse_datetime(response.get('submission_datetime'))
                if submission_time:
                    timeline_data.append({
                        'date': submission_time,
                        'count': 1
                    })
            
            if timeline_data:
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
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
                )
                st.plotly_chart(fig, use_container_width=True)

            # Display filtered responses
            for response in filtered_responses:
                with st.container():
                    submission_time = parse_datetime(response.get('submission_datetime'))
                    submission_display = submission_time.strftime('%Y-%m-%d %H:%M:%S') if submission_time else 'Time not available'
                    
                    st.markdown(f"""
                        <div class='response-card'>
                            <h4>Response from {response.get('trainee_email', 'Unknown User')}</h4>
                            <p>Submitted: {submission_display}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Response Details in Tabs
                    response_tabs = st.tabs(["📝 Answers", "📊 Analytics", "🔍 Details"])
                    
                    with response_tabs[0]:
                        # Display answers with error handling
                        trainee_responses = response.get('trainee_responses', {})
                        if trainee_responses:
                            for section, answers in trainee_responses.items():
                                st.markdown(f"**{section.title()}**")
                                if isinstance(answers, dict):
                                    for q_id, answer_data in answers.items():
                                        col1, col2 = st.columns([1, 2])
                                        col1.markdown(f"*{answer_data.get('question', 'Unknown Question')}*")
                                        col2.markdown(f"{answer_data.get('answer', 'No answer provided')}")
                        else:
                            st.info("No response data available")
                    
                    with response_tabs[1]:
                        # Calculate completion time if possible
                        start_time = parse_datetime(response.get('start_time'))
                        end_time = parse_datetime(response.get('submission_datetime'))
                        
                        if start_time and end_time:
                            completion_time = (end_time - start_time).total_seconds() / 60
                            completion_time = f"{completion_time:.0f} minutes"
                        else:
                            completion_time = "Unknown"

                        st.markdown(f"""
                            - ⏱️ Completion Time: {completion_time}
                            - 📊 Answer Quality Score: {response.get('quality_score', 'N/A')}
                            - 🎯 Response Completeness: {response.get('completeness', 'N/A')}
                        """)
                    
                    with response_tabs[2]:
                        # Show technical details
                        st.json({
                            "response_id": response.get('response_id', 'N/A'),
                            "start_time": str(start_time) if start_time else 'N/A',
                            "completion_time": str(end_time) if end_time else 'N/A',
                            "platform": response.get('platform', 'web'),
                            "status": response.get('status', 'unknown')
                        })

            # Updated Quick Insights
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                st.markdown("### 🎯 Quick Insights")
                insight_cols = st.columns(2)
                
                with insight_cols[0]:
                    # Calculate most active hour if we have data
                    if not timeline_df.empty:
                        peak_hour = timeline_df['date'].dt.hour.mode().iloc[0]
                        peak_hour_str = f"{peak_hour:02d}:00"
                    else:
                        peak_hour_str = "N/A"
                        
                    st.markdown(f"""
                        <div class='insight-pill'>Most active hour: {peak_hour_str}</div>
                        <div class='insight-pill'>Responses today: {len([r for r in filtered_responses if parse_datetime(r.get('submission_datetime')).date() == datetime.now().date()])}</div>
                        <div class='insight-pill'>Total responses: {len(filtered_responses)}</div>
                    """, unsafe_allow_html=True)
                
                with insight_cols[1]:
                    st.markdown(f"""
                        <div class='insight-pill'>Recent responses: {recent_responses}</div>
                        <div class='insight-pill'>Time until expiry: {calculate_time_left(survey_data.get('expiration_datetime'))}</div>
                        <div class='insight-pill'>Survey status: {'Active' if not survey_data.get('is_expired') else 'Expired'}</div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error displaying survey responses: {str(e)}")
            st.exception(e)
    
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
