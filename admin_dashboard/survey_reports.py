import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from wordcloud import WordCloud
import nltk
from datetime import datetime

# Download nltk stopwords if not already downloaded
nltk.download('stopwords')
from nltk.corpus import stopwords

def create_metric_card(title, value, delta=None, suffix=""):
    return go.Figure(go.Indicator(
        mode="number+delta" if delta else "number",
        value=value,
        title={"text": title, "font": {"size": 20}},
        number={"suffix": suffix, "font": {"size": 30}},
        delta={"reference": delta, "relative": True} if delta else None,
    )).update_layout(height=200)

def show_survey_reports():
    st.set_page_config(layout="wide", page_title="Survey Analytics Dashboard")
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 5px;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1f4287;
        }
        .metric-row {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Dashboard Header with Logo/Icon
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://your-logo-url.png", width=100)  # Replace with your logo
    with col2:
        st.title("📊 Survey Analytics Dashboard")
        st.markdown("*Comprehensive analysis and insights from survey responses*")

    # Enhanced Survey ID input with validation
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            survey_id = st.text_input(
                "Survey ID",
                placeholder="Enter Survey ID",
                help="Enter the unique identifier for your survey"
            )
        with col2:
            analyze_button = st.button("🔍 Analyze", use_container_width=True)
        with col3:
            export_button = st.button("📥 Export Data", use_container_width=True)

    if analyze_button and survey_id:
        with st.spinner("Generating comprehensive analytics..."):
            survey_data = get_survey_data(survey_id)
            if not survey_data:
                st.error("❌ Survey not found. Please check the ID.")
                return

            responses = fetch_survey_responses(survey_id)
            if not responses:
                st.warning("⚠️ No responses recorded for this survey yet.")
                return

            # Overview Metrics
            st.markdown("### 📈 Survey Overview")
            total_responses = len(responses)
            
            # Create metric cards row
            metric_cols = st.columns(4)
            with metric_cols[0]:
                fig = create_metric_card("Total Responses", total_responses)
                st.plotly_chart(fig, use_container_width=True)
            
            with metric_cols[1]:
                avg_completion = 85  # Calculate this based on your data
                fig = create_metric_card("Completion Rate", avg_completion, suffix="%")
                st.plotly_chart(fig, use_container_width=True)
            
            with metric_cols[2]:
                response_trend = 12  # Calculate this based on your data
                fig = create_metric_card("Daily Responses", response_trend, delta=8)
                st.plotly_chart(fig, use_container_width=True)
            
            with metric_cols[3]:
                avg_rating = 4.2  # Calculate this based on your data
                fig = create_metric_card("Average Rating", avg_rating, suffix="/5")
                st.plotly_chart(fig, use_container_width=True)

            # Process responses into DataFrame
            all_responses = []
            for response in responses:
                for key, answer_data in response["trainee_responses"]["survey"].items():
                    all_responses.append({
                        "question": answer_data["question"],
                        "answer": answer_data["answer"],
                        "type": answer_data["type"],
                        "timestamp": response.get("timestamp", datetime.now().isoformat())
                    })

            df = pd.DataFrame(all_responses)

            # Create tabs for different analyses
            tabs = st.tabs(["📊 Response Analysis", "📝 Text Analysis", "📈 Trends", "📋 Raw Data"])

            with tabs[0]:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Multiple Choice Responses")
                    multiple_choice = df[df["type"] == "multiple_choice"]
                    if not multiple_choice.empty:
                        for question in multiple_choice["question"].unique():
                            data = multiple_choice[multiple_choice["question"] == question]
                            fig = px.pie(
                                data_frame=data["answer"].value_counts().reset_index(),
                                values="count",
                                names="index",
                                title=question,
                                hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("### Likert Scale Responses")
                    likert = df[df["type"] == "likert_scale"]
                    if not likert.empty:
                        for question in likert["question"].unique():
                            data = likert[likert["question"] == question]
                            fig = px.histogram(
                                data,
                                x="answer",
                                title=question,
                                color_discrete_sequence=['#2E86C1'],
                                nbins=5
                            )
                            fig.update_layout(bargap=0.1)
                            st.plotly_chart(fig, use_container_width=True)

            with tabs[1]:
                st.markdown("### Text Analysis")
                open_ended = df[df["type"] == "open_ended"]
                if not open_ended.empty:
                    # Sentiment Analysis
                    sentiments = open_ended["answer"].apply(
                        lambda x: TextBlob(x).sentiment.polarity
                    )
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=sentiments.mean(),
                        title={'text': "Average Sentiment Score"},
                        gauge={
                            'axis': {'range': [-1, 1]},
                            'bar': {'color': "#2E86C1"},
                            'steps': [
                                {'range': [-1, -0.3], 'color': "#E74C3C"},
                                {'range': [-0.3, 0.3], 'color': "#F7DC6F"},
                                {'range': [0.3, 1], 'color': "#2ECC71"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': sentiments.mean()
                            }
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)

            with tabs[2]:
                st.markdown("### Response Trends")
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                daily_responses = df.groupby(df['timestamp'].dt.date).size().reset_index()
                daily_responses.columns = ['date', 'count']
                
                fig = px.line(
                    daily_responses,
                    x='date',
                    y='count',
                    title='Daily Response Trend',
                    markers=True
                )
                fig.update_traces(line_color='#2E86C1')
                st.plotly_chart(fig, use_container_width=True)

            with tabs[3]:
                st.markdown("### Raw Response Data")
                st.dataframe(
                    df.style.background_gradient(cmap='Blues'),
                    use_container_width=True
                )

# Run the analytics dashboard
if __name__ == "__main__":
    show_survey_reports()