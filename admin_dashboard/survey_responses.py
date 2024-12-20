import streamlit as st
import pandas as pd
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from datetime import datetime, timedelta

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
        # .response-header {
        #     background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        #     padding: 20px;
        #     border-radius: 15px;
        #     margin-bottom: 25px;
        # }
        .quick-stats {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .quick-stats h1 {
            font-size: 1.5rem !important;
            line-height: 1.2 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .quick-stats p {
            margin: 5px 0 0 0 !important;
            font-size: 0.9rem !important;
        }
        .stTable {
            width: 100%;
        }
        .stTable td {
            white-space: normal !important;
            padding: 8px;
            vertical-align: top;
            text-align: left;
        }
        .stTable th {
            white-space: normal !important;
            padding: 8px;
            text-align: left !important;
            background-color: rgba(255, 255, 255, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state for survey data
    if 'survey_data' not in st.session_state:
        st.session_state.survey_data = None
        st.session_state.responses = None
        st.session_state.filtered_responses = None

    # Modern header with survey info
    # st.markdown('<div class="response-header">', unsafe_allow_html=True)
    st.title("📋 Survey Response Explorer")

    st.markdown(
        "##### 👉 View individual survey responses to understand your audience’s feedback."
    )

    st.write("---")
    
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
            
            # 1. Response Overview Section
            st.markdown("### 📊 Response Overview")
            total_responses = len(responses)
            recent_responses = sum(1 for r in responses 
                                 if parse_datetime(r.get('submission_datetime')) and 
                                 (datetime.now() - parse_datetime(r.get('submission_datetime'))).days <= 7)
            
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

            # 2. Response Explorer Section
            st.markdown("### 🔍 Response Explorer")
            
            # Filters
            with st.expander("📋 Filter Responses", expanded=True):
                filter_cols = st.columns(3)
                with filter_cols[0]:
                    date_range = st.date_input("Date Range", value=[])
                with filter_cols[1]:
                    sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First"])
                with filter_cols[2]:
                    search = st.text_input("Search", placeholder="Search by email")

            # Apply filters
            filtered_responses = responses.copy()
            
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
                    if search in str(r.get('trainee_email', '')).lower()
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

            # 3. Response Summary Table
            st.markdown("### 📋 Response Summary")
            summary_data = []
            for idx, response in enumerate(filtered_responses, 1):
                submission_time = parse_datetime(response.get('submission_datetime'))
                summary_data.append({
                    'Response ID': idx,
                    'Email': response.get('trainee_email', 'Unknown'),
                    'Submission Date': submission_time.strftime('%Y-%m-%d') if submission_time else 'N/A',
                    'Submission Time': submission_time.strftime('%H:%M:%S') if submission_time else 'N/A'
                })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Response ID": st.column_config.NumberColumn("ID", width="small"),
                        "Email": st.column_config.TextColumn("Email", width="medium"),
                        "Submission Date": st.column_config.TextColumn("Date", width="small"),
                        "Submission Time": st.column_config.TextColumn("Time", width="small")
                    }
                )
            else:
                st.info("No responses available to display in summary")

            # 4. Individual Responses
            st.markdown("### 📝 Detailed Responses")

            for response in filtered_responses:
                submission_time = parse_datetime(response.get('submission_datetime'))
                submission_display = submission_time.strftime('%Y-%m-%d %H:%M:%S') if submission_time else 'Time not available'
                
                with st.expander(f"Response from {response.get('trainee_email', 'Unknown User')} - {submission_display}"):
                    trainee_responses = response.get('trainee_responses', {})
                    
                    if isinstance(trainee_responses, dict):
                        # Profile Section
                        if 'profile' in trainee_responses:
                            st.markdown("#### 👤 Profile Information")
                            profile_data = []
                            
                            for q_id, answer_data in trainee_responses['profile'].items():
                                if isinstance(answer_data, dict):
                                    question = answer_data.get('question', '')
                                    answer = answer_data.get('answer', '')
                                    
                                    if isinstance(answer, list):
                                        answer = ", ".join(str(item) for item in answer)
                                    elif isinstance(answer, (int, float)):
                                        if answer_data.get('type') == 'likert_scale':
                                            answer = f"{answer}/5"
                                    
                                    profile_data.append([question, str(answer)])
                            
                            if profile_data:
                                # Convert to DataFrame and display
                                df = pd.DataFrame(profile_data, columns=['Question', 'Response'])
                                st.write(df.to_html(
                                    index=False, 
                                    escape=False, 
                                    classes='stTable',
                                    justify='left'
                                ), unsafe_allow_html=True)

                        # Survey Section
                        if 'survey' in trainee_responses:
                            st.markdown("#### 📋 Survey Responses")
                            survey_data = []
                            
                            for q_id, answer_data in trainee_responses['survey'].items():
                                if isinstance(answer_data, dict):
                                    question = answer_data.get('question', '')
                                    answer = answer_data.get('answer', '')
                                    answer_type = answer_data.get('type', '')
                                    
                                    if isinstance(answer, list):
                                        answer = ", ".join(str(item) for item in answer)
                                    elif isinstance(answer, (int, float)) and answer_type == 'likert_scale':
                                        scale = answer_data.get('scale', {})
                                        max_label = scale.get('max_label', '')
                                        answer = f"{answer}/5 - {max_label}"
                                    
                                    survey_data.append([question, str(answer)])
                            
                            if survey_data:
                                # Convert to DataFrame and display
                                df = pd.DataFrame(survey_data, columns=['Question', 'Response'])
                                st.write(df.to_html(
                                    index=False, 
                                    escape=False, 
                                    classes='stTable',
                                    justify='left'
                                ), unsafe_allow_html=True)

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
        """)

if __name__ == "__main__":
    show_survey_responses()
