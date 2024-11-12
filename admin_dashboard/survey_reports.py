import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from textblob import TextBlob
from wordcloud import WordCloud
import nltk
from datetime import datetime, timedelta
import numpy as np

# Download nltk stopwords if not already downloaded
nltk.download('stopwords')
from nltk.corpus import stopwords

def create_metric_card(title, value, delta=None, suffix="", description=None):
    display_value = value
    if isinstance(value, str):
        try:
            numeric_value = float(''.join(filter(str.isdigit, value)))
        except ValueError:
            numeric_value = 0
    else:
        numeric_value = value

    fig = go.Figure(go.Indicator(
        mode="number+delta" if delta else "number",
        value=numeric_value,
        title={
            "text": f"{title}",
            "font": {"size": 20, "color": "white", "family": "Arial"}
        },
        number={
            "suffix": suffix,
            "font": {"size": 36, "color": "white", "family": "Arial"},
            "valueformat": ".1f"
        },
        delta={"reference": delta, "relative": True} if delta else None,
    ))
    
    if description:
        fig.add_annotation(
            text=description,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0,
            showarrow=False,
            font=dict(size=14, color="rgba(255,255,255,0.7)"),
            xanchor="center"
        )
    
    fig.update_layout(
        height=160,
        margin=dict(l=10, r=10, t=30, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def show_survey_reports():
    # Custom CSS with improved styling
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background-color: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 5px;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: rgba(255,255,255,0.1);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }
        .metric-row {
            background-color: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }
        .stPlotlyChart {
            background-color: rgba(0,0,0,0);
            border-radius: 10px;
            padding: 15px;
            width: 100%;
        }
        .insight-card {
            background-color: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .stExpander {
            background-color: rgba(255,255,255,0.02) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 28px;
        }
        [data-testid="stMetricDelta"] {
            font-size: 20px;
        }
        .metric-container {
            background-color: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            width: 100%;
            padding: 0.5rem;
        }
        .element-container {
            width: 100%;
        }
        .element-container:has(> div > div > h1) {
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with survey info
    st.title("📊 Survey Analytics Dashboard")
    
    # Survey selector with recent surveys list
    col1, col2 = st.columns([4, 1])
    with col1:
        survey_id = st.text_input(
            "Survey ID",
            placeholder="Enter the Survey ID to analyze",
            help="Enter the unique identifier for your survey",
            label_visibility="collapsed"
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

            # Process responses with enhanced metadata
            all_responses = []
            response_times = []
            last_response_time = None
            
            for response in responses:
                timestamp = datetime.fromisoformat(response.get("timestamp", datetime.now().isoformat()))
                if last_response_time:
                    response_times.append((timestamp - last_response_time).total_seconds() / 3600)
                last_response_time = timestamp
                
                for key, answer_data in response["trainee_responses"]["survey"].items():
                    all_responses.append({
                        "question": answer_data["question"],
                        "answer": answer_data["answer"],
                        "type": answer_data["type"],
                        "timestamp": timestamp,
                        "trainee_email": response.get("trainee_email"),
                        "day_of_week": timestamp.strftime('%A'),
                        "hour_of_day": timestamp.hour
                    })

            df = pd.DataFrame(all_responses)

            # Enhanced Overview metrics
            total_responses = len(responses)
            completion_rate = round((total_responses / total_responses) * 100, 1)
            avg_response_time = np.mean(response_times) if response_times else 0

            # Calculate unique and insightful metrics
            total_responses = len(responses)
            
            # Most Active Time Window
            df['hour'] = df['timestamp'].dt.hour
            busy_hours = df.groupby('hour').size()
            peak_hour_start = busy_hours.idxmax()
            peak_window = f"{peak_hour_start:02d}:00-{(peak_hour_start+1):02d}:00"
            peak_percentage = (busy_hours.max() / len(df)) * 100

            # Response Diversity
            unique_respondents = df['trainee_email'].nunique()
            repeat_respondents = sum(df.groupby('trainee_email').size() > 1)
            diversity_score = (unique_respondents / total_responses) * 100

            # Question Engagement Score
            question_engagement = {}
            for _, response in df.iterrows():
                if response['type'] == 'open_ended':
                    # Score based on word count
                    words = len(str(response['answer']).split())
                    question_engagement[response['question']] = question_engagement.get(response['question'], [])
                    question_engagement[response['question']].append(min(words / 10, 1))  # Cap at 1, 10 words = full score
                elif response['type'] == 'likert_scale':
                    # Score based on non-neutral answers (1,2 or 4,5 vs 3)
                    score = abs(float(response['answer']) - 3) / 2  # Convert to 0-1 scale
                    question_engagement[response['question']] = question_engagement.get(response['question'], [])
                    question_engagement[response['question']].append(score)

            avg_engagement = np.mean([np.mean(scores) for scores in question_engagement.values()]) * 100

            # Metrics Row with creative insights
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            metrics_cols = st.columns([1, 1, 1, 1])
            with metrics_cols[0]:
                fig = create_metric_card(
                    "Total Responses", 
                    total_responses,
                    description="Survey submissions"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with metrics_cols[1]:
                fig = create_metric_card(
                    "Peak Activity Time", 
                    peak_percentage,
                    suffix="%",
                    description=f"at {peak_window}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with metrics_cols[2]:
                fig = create_metric_card(
                    "Response Diversity", 
                    diversity_score,
                    suffix="%",
                    description=f"{repeat_respondents} repeat participants"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with metrics_cols[3]:
                fig = create_metric_card(
                    "Engagement Score", 
                    avg_engagement,
                    suffix="%",
                    description="Based on response quality"
                )
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Create tabs with enhanced analysis
            tabs = st.tabs([
                "📊 Response Analysis", 
                "📝 Text Analysis", 
                "📈 Trends",
                "🎯 Insights Dashboard"
            ])

            with tabs[0]:
                st.markdown("### Response Analysis Overview")
                
                # Summary statistics
                total_questions = len(df["question"].unique())
                mc_questions = len(df[df["type"] == "multiple_choice"]["question"].unique())
                rating_questions = len(df[df["type"] == "likert_scale"]["question"].unique())
                
                # Quick stats row
                stats_cols = st.columns(4)
                stats_cols[0].metric("Total Questions", total_questions)
                stats_cols[1].metric("Multiple Choice Questions", mc_questions)
                stats_cols[2].metric("Rating Questions", rating_questions)
                stats_cols[3].metric("Average Rating", f"{df[df['type'] == 'likert_scale']['answer'].astype(float).mean():.1f}/5")

                # Container for aligned columns
                with st.container():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                            <div style='background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
                                <h3 style='margin:0;'>Multiple Choice Responses</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        multiple_choice = df[df["type"] == "multiple_choice"]
                        if not multiple_choice.empty:
                            for question in multiple_choice["question"].unique():
                                # Create expandable container for each question
                                with st.expander(f"📊 {question}", expanded=True):
                                    data = multiple_choice[multiple_choice["question"] == question]
                                    value_counts = data["answer"].value_counts().reset_index()
                                    value_counts.columns = ["answer", "count"]
                                    
                                    # Calculate percentages
                                    total = value_counts["count"].sum()
                                    value_counts["percentage"] = (value_counts["count"] / total * 100).round(1)
                                    
                                    # Create pie chart
                                    fig = px.pie(
                                        data_frame=value_counts,
                                        values="count",
                                        names="answer",
                                        title=f"Response Distribution",
                                        hole=0.4,
                                        color_discrete_sequence=px.colors.qualitative.Set3
                                    )
                                    fig.update_layout(
                                        showlegend=True,
                                        margin=dict(t=50, l=0, r=0, b=0),
                                        height=400,
                                        title_font_color="white",
                                        font_color="white",
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)'
                                    )
                                    
                                    # Display chart and key insights
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Show key insights
                                    top_answer = value_counts.iloc[0]
                                    st.markdown(f"""
                                        **Key Insights:**
                                        - Most common response: **{top_answer['answer']}** ({top_answer['percentage']}%)
                                        - Total responses: **{total}**
                                        - Number of unique answers: **{len(value_counts)}**
                                    """)

                    with col2:
                        st.markdown("""
                            <div style='background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
                                <h3 style='margin:0;'>Rating Distributions</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        likert = df[df["type"] == "likert_scale"]
                        if not likert.empty:
                            for question in likert["question"].unique():
                                with st.expander(f"📈 {question}", expanded=True):
                                    data = likert[likert["question"] == question]
                                    
                                    # Convert answers to numeric
                                    data["answer"] = pd.to_numeric(data["answer"])
                                    
                                    # Calculate statistics
                                    avg_rating = data["answer"].mean()
                                    median_rating = data["answer"].median()
                                    mode_rating = data["answer"].mode().iloc[0]
                                    
                                    # Create histogram
                                    fig = go.Figure()
                                    fig.add_trace(go.Histogram(
                                        x=data["answer"],
                                        nbinsx=5,
                                        marker_color='rgb(55, 83, 109)'
                                    ))
                                    
                                    # Add mean line
                                    fig.add_vline(
                                        x=avg_rating,
                                        line_dash="dash",
                                        line_color="red",
                                        annotation_text="Mean"
                                    )
                                    
                                    fig.update_layout(
                                        title="Response Distribution",
                                        xaxis_title="Rating",
                                        yaxis_title="Count",
                                        bargap=0.1,
                                        height=400,
                                        title_font_color="white",
                                        font_color="white",
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)'
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Display statistics
                                    stats_cols = st.columns(3)
                                    stats_cols[0].metric("Average Rating", f"{avg_rating:.1f}")
                                    stats_cols[1].metric("Median Rating", f"{median_rating:.1f}")
                                    stats_cols[2].metric("Most Common", f"{mode_rating:.1f}")
                                    
                                    # Additional insights
                                    st.markdown(f"""
                                        **Rating Insights:**
                                        - Response range: **{data['answer'].min()}-{data['answer'].max()}**
                                        - Standard deviation: **{data['answer'].std():.2f}**
                                        - Total responses: **{len(data)}**
                                    """)

            with tabs[1]:
                st.subheader("Text Analysis")
                open_ended = df[df["type"] == "open_ended"]
                if not open_ended.empty:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Enhanced Sentiment Analysis with explanation
                        sentiments = open_ended["answer"].apply(
                            lambda x: TextBlob(x).sentiment
                        )
                        avg_polarity = sentiments.apply(lambda x: x.polarity).mean()
                        avg_subjectivity = sentiments.apply(lambda x: x.subjectivity).mean()
                        
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=avg_polarity,
                            title={'text': "Average Sentiment Score", 'font': {'color': 'white'}},
                            gauge={
                                'axis': {'range': [-1, 1], 'tickcolor': "white"},
                                'bar': {'color': "#2E86C1"},
                                'steps': [
                                    {'range': [-1, -0.3], 'color': "#E74C3C"},
                                    {'range': [-0.3, 0.3], 'color': "#F7DC6F"},
                                    {'range': [0.3, 1], 'color': "#2ECC71"}
                                ],
                                'threshold': {
                                    'line': {'color': "white", 'width': 4},
                                    'thickness': 0.75,
                                    'value': avg_polarity
                                }
                            }
                        ))
                        fig.update_layout(
                            height=300,
                            paper_bgcolor='rgba(0,0,0,0)',
                            font={'color': 'white'}
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # Sentiment Interpretation
                        st.markdown("""
                            <div style='background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;'>
                                <h4>📊 Sentiment Analysis Explained</h4>
                                <p><strong>Polarity Score (-1 to +1):</strong></p>
                                <ul>
                                    <li>-1.0 to -0.3: Strong negative emotions/criticism</li>
                                    <li>-0.3 to 0.3: Neutral or balanced feedback</li>
                                    <li>0.3 to 1.0: Strong positive feedback/praise</li>
                                </ul>
                                <p><strong>Objectivity Score (0 to 100%):</strong></p>
                                <ul>
                                    <li>0-30%: Highly subjective (opinions, emotions)</li>
                                    <li>30-70%: Balanced perspective</li>
                                    <li>70-100%: Highly objective (facts, observations)</li>
                                </ul>
                                <p><strong>Response Quality Indicators:</strong></p>
                                <ul>
                                    <li>Detailed: {avg_words:.1f} words per response</li>
                                    <li>Structured: {avg_sentences:.1f} sentences per response</li>
                                </ul>
                            </div>
                        """.format(
                            avg_words=df[df['type'] == 'open_ended']['answer'].str.split().str.len().mean(),
                            avg_sentences=df[df['type'] == 'open_ended']['answer'].apply(lambda x: len(TextBlob(x).sentences)).mean()
                        ), unsafe_allow_html=True)

                    # Add response quality metrics
                    quality_cols = st.columns(3)
                    with quality_cols[0]:
                        st.metric(
                            "Response Detail",
                            f"{avg_sentence_length:.1f}",
                            "words per sentence",
                            help="Higher numbers indicate more detailed responses"
                        )
                    with quality_cols[1]:
                        st.metric(
                            "Response Clarity",
                            f"{(1 - avg_subjectivity) * 100:.1f}%",
                            help="Higher percentages indicate clearer, more objective responses"
                        )
                    with quality_cols[2]:
                        st.metric(
                            "Engagement Level",
                            f"{avg_word_count:.0f}",
                            "words per response",
                            help="Higher numbers indicate more engaged respondents"
                        )

                    # Detailed Sentiment Metrics
                    metrics_cols = st.columns(3)
                    
                    # Calculate sentiment distributions
                    sentiment_counts = sentiments.apply(lambda x: (
                        "Positive" if x.polarity > 0.3 
                        else "Negative" if x.polarity < -0.3 
                        else "Neutral"
                    )).value_counts()
                    
                    total_responses = len(sentiments)
                    positive_pct = (sentiment_counts.get("Positive", 0) / total_responses) * 100
                    negative_pct = (sentiment_counts.get("Negative", 0) / total_responses) * 100
                    neutral_pct = (sentiment_counts.get("Neutral", 0) / total_responses) * 100

                    metrics_cols[0].metric(
                        "Positive Responses",
                        f"{positive_pct:.1f}%",
                        delta=f"{sentiment_counts.get('Positive', 0)} responses"
                    )
                    metrics_cols[1].metric(
                        "Neutral Responses",
                        f"{neutral_pct:.1f}%",
                        delta=f"{sentiment_counts.get('Neutral', 0)} responses"
                    )
                    metrics_cols[2].metric(
                        "Negative Responses",
                        f"{negative_pct:.1f}%",
                        delta=f"{sentiment_counts.get('Negative', 0)} responses"
                    )

                    # Sentiment Over Time Analysis
                    st.markdown("### 📈 Sentiment Trends")
                    sentiment_time = pd.DataFrame({
                        'timestamp': open_ended['timestamp'],
                        'polarity': sentiments.apply(lambda x: x.polarity),
                        'subjectivity': sentiments.apply(lambda x: x.subjectivity)
                    })
                    
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    # Add polarity line
                    fig.add_trace(
                        go.Scatter(
                            x=sentiment_time['timestamp'],
                            y=sentiment_time['polarity'].rolling(window=3).mean(),
                            name="Sentiment (Polarity)",
                            line=dict(color="#2ECC71", width=3)
                        )
                    )
                    
                    # Add subjectivity line
                    fig.add_trace(
                        go.Scatter(
                            x=sentiment_time['timestamp'],
                            y=sentiment_time['subjectivity'].rolling(window=3).mean(),
                            name="Objectivity Level",
                            line=dict(color="#E74C3C", width=3, dash='dash')
                        ),
                        secondary_y=True
                    )
                    
                    fig.update_layout(
                        title="Sentiment and Objectivity Trends",
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white'},
                        hovermode='x unified'
                    )
                    fig.update_yaxes(title_text="Sentiment Score", secondary_y=False)
                    fig.update_yaxes(title_text="Objectivity Level", secondary_y=True)
                    
                    st.plotly_chart(fig, use_container_width=True)

                    # Key Insights Box
                    st.markdown("""
                        <div style='background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h4>🔍 Key Insights</h4>
                            <ul>
                                <li>Overall sentiment is {}</li>
                                <li>Responses are {} objective ({}% objectivity score)</li>
                                <li>Most {} responses recorded on {}</li>
                                <li>Sentiment trend is {}</li>
                            </ul>
                        </div>
                    """.format(
                        "positive" if avg_polarity > 0.3 else "negative" if avg_polarity < -0.3 else "neutral",
                        "highly" if avg_subjectivity < 0.3 else "moderately" if avg_subjectivity < 0.7 else "less",
                        round((1 - avg_subjectivity) * 100, 1),
                        "positive" if positive_pct > negative_pct else "negative",
                        sentiment_time.groupby(sentiment_time['timestamp'].dt.date)['polarity'].mean().idxmax().strftime('%Y-%m-%d'),
                        "improving" if sentiment_time['polarity'].corr(pd.Series(range(len(sentiment_time)))) > 0.1 
                        else "declining" if sentiment_time['polarity'].corr(pd.Series(range(len(sentiment_time)))) < -0.1 
                        else "stable"
                    ), unsafe_allow_html=True)

                    # Continue with existing word frequency analysis...

            with tabs[2]:
                st.subheader("Response Trends")
                # Group by timestamp and trainee_email to get unique responses per day
                daily_responses = df.groupby(['timestamp', 'trainee_email']).size().reset_index()
                daily_responses = daily_responses.groupby(daily_responses['timestamp'].dt.date).size().reset_index()
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

            # New Insights Dashboard tab
            with tabs[3]:
                st.subheader("🎯 Key Insights Dashboard")
                
                # Response patterns
                col1, col2 = st.columns(2)
                with col1:
                    # Day of week analysis
                    day_counts = df.groupby(['day_of_week', 'trainee_email']).size().reset_index()
                    day_counts = day_counts.groupby('day_of_week').size()
                    fig = px.bar(
                        x=day_counts.index,
                        y=day_counts.values,
                        title="Response Distribution by Day",
                        labels={'x': 'Day', 'y': 'Count'}
                    )
                    fig.update_layout(
                        height=300,
                        title_font_color="white",
                        font_color="white",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Hour of day analysis
                    hour_counts = df.groupby(['hour_of_day', 'trainee_email']).size().reset_index()
                    hour_counts = hour_counts.groupby('hour_of_day').size().sort_index()
                    fig = px.line(
                        x=hour_counts.index,
                        y=hour_counts.values,
                        title="Response Distribution by Hour",
                        labels={'x': 'Hour', 'y': 'Count'}
                    )
                    fig.update_layout(
                        height=300,
                        title_font_color="white",
                        font_color="white",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Key findings section
                st.markdown("""
                    <div class='insight-card'>
                        <h4>📌 Key Findings</h4>
                        <ul>
                            <li>Most active day: {}</li>
                            <li>Peak response hour: {}:00</li>
                            <li>Average response interval: {:.1f} hours</li>
                            <li>Response trend: {}</li>
                        </ul>
                    </div>
                """.format(
                    day_counts.index[0],
                    hour_counts.idxmax(),
                    avg_response_time,
                    "Increasing" if len(response_times) > 1 and response_times[-1] > response_times[0] else "Stable"
                ), unsafe_allow_html=True)

                # Export options
                st.markdown("### 📤 Export Options")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Export as Excel"):
                        # Add Excel export functionality
                        pass
                with col2:
                    if st.button("📑 Export as PDF Report"):
                        # Add PDF export functionality
                        pass

if __name__ == "__main__":
    show_survey_reports()