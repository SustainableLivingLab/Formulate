import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from textblob import TextBlob
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
    )).update_layout(
        height=200,
        margin=dict(l=10, r=10, t=30, b=10)
    )

def show_survey_reports():
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
        .stPlotlyChart {
            background-color: white;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 Survey Analytics Dashboard")
    st.markdown("*Comprehensive analysis of survey responses*")

    # Survey ID input with validation
    col1, col2 = st.columns([4, 1])
    with col1:
        survey_id = st.text_input(
            "Survey ID",
            placeholder="Enter the Survey ID to analyze",
            help="Enter the unique identifier for your survey"
        )
    with col2:
        analyze_button = st.button("🔍 Analyze", use_container_width=True)

    if analyze_button and survey_id:
        with st.spinner("Loading survey data..."):
            survey_data = get_survey_data(survey_id)
            if not survey_data:
                st.error("❌ Survey not found. Please check the ID.")
                return

            responses = fetch_survey_responses(survey_id)
            if not responses:
                st.warning("⚠️ No responses recorded for this survey yet.")
                return

            # Process responses
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
            
            # Overview metrics
            total_responses = len(responses)
            completion_rate = round((total_responses / 100) * 100, 1)  # Example calculation
            avg_time = "5 mins"  # Example value

            # Metrics Row
            metrics_cols = st.columns(3)
            with metrics_cols[0]:
                fig = create_metric_card("Total Responses", total_responses)
                st.plotly_chart(fig, use_container_width=True)
            with metrics_cols[1]:
                fig = create_metric_card("Completion Rate", completion_rate, suffix="%")
                st.plotly_chart(fig, use_container_width=True)
            with metrics_cols[2]:
                fig = create_metric_card("Avg. Time", avg_time)
                st.plotly_chart(fig, use_container_width=True)

            # Create tabs for analysis
            tabs = st.tabs(["📊 Response Analysis", "📝 Text Analysis", "📈 Trends"])

            with tabs[0]:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Multiple Choice Responses")
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
                            fig.update_layout(
                                showlegend=True,
                                margin=dict(t=50, l=0, r=0, b=0),
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Rating Distributions")
                    likert = df[df["type"] == "likert_scale"]
                    if not likert.empty:
                        for question in likert["question"].unique():
                            data = likert[likert["question"] == question]
                            fig = go.Figure()
                            fig.add_trace(go.Histogram(
                                x=data["answer"],
                                nbinsx=5,
                                marker_color='rgb(55, 83, 109)'
                            ))
                            fig.update_layout(
                                title=question,
                                xaxis_title="Rating",
                                yaxis_title="Count",
                                bargap=0.1,
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)

            with tabs[1]:
                st.subheader("Text Analysis")
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
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

                    # Word frequency analysis using Plotly
                    words = ' '.join(open_ended['answer']).lower().split()
                    word_freq = pd.Series(words).value_counts().head(10)
                    
                    fig = px.bar(
                        x=word_freq.index,
                        y=word_freq.values,
                        title="Top 10 Most Common Words",
                        labels={'x': 'Word', 'y': 'Frequency'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

            with tabs[2]:
                st.subheader("Response Trends")
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
                fig.update_traces(
                    line_color='#2E86C1',
                    marker=dict(size=8)
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Number of Responses",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

                # Response time distribution
                fig = px.histogram(
                    df,
                    x='timestamp',
                    title='Response Time Distribution',
                    nbins=20,
                    color_discrete_sequence=['#2E86C1']
                )
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Number of Responses",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_survey_reports()