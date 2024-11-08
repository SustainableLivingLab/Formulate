import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.create_database_tables import get_survey_data, fetch_survey_responses
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from wordcloud import WordCloud
import nltk

# Download nltk stopwords if not already downloaded
nltk.download('stopwords')
from nltk.corpus import stopwords

def show_survey_reports():
    st.header("📊 Survey Analytics Dashboard")

    # Input for Survey ID
    survey_id = st.text_input("Enter Survey ID", placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000")

    if st.button("Generate Analytics"):
        if survey_id:
            with st.spinner("Generating analytics..."):
                # Fetch survey data
                survey_data = get_survey_data(survey_id)
                if survey_data:
                    st.success("Survey data retrieved successfully!")

                    # Access trainer questions responses data safely
                    trainer_input = survey_data.get("trainer_questions_responses", {})
                    st.subheader("Survey Overview")
                    st.write(f"**Title**: {trainer_input.get('surveyTitle', 'No Title Available')}")
                    st.write(f"**Description**: {trainer_input.get('surveyDescription', 'No Description Available')}")

                    # Fetch trainee responses
                    responses = fetch_survey_responses(survey_id)
                    if responses:
                        st.subheader("Analytics Overview")

                        # Prepare response data for analysis
                        all_responses = []
                        for response in responses:
                            for key, answer_data in response["trainee_responses"]["survey"].items():
                                question = answer_data["question"]
                                answer = answer_data["answer"]
                                answer_type = answer_data["type"]
                                all_responses.append({"question": question, "answer": answer, "type": answer_type})

                        # Convert to DataFrame for easier processing
                        df = pd.DataFrame(all_responses)

                        # Structured Question Analytics
                        st.subheader("Structured Question Analytics")

                        # Multiple Choice Responses
                        st.markdown("### Multiple Choice Responses")
                        multiple_choice = df[df["type"] == "multiple_choice"]
                        if not multiple_choice.empty:
                            for question in multiple_choice["question"].unique():
                                st.write(f"**{question}**")
                                data = multiple_choice[multiple_choice["question"] == question]["answer"]
                                fig, ax = plt.subplots()
                                sns.countplot(y=data, ax=ax)
                                ax.set_xlabel("Count")
                                st.pyplot(fig)

                        # Checkbox Responses
                        st.markdown("### Checkbox Responses")
                        checkbox_responses = df[df["type"] == "checkbox"]
                        if not checkbox_responses.empty:
                            for question in checkbox_responses["question"].unique():
                                st.write(f"**{question}**")
                                data = checkbox_responses[checkbox_responses["question"] == question]["answer"]
                                options = sum(data.tolist(), [])
                                fig, ax = plt.subplots()
                                sns.countplot(y=options, ax=ax)
                                ax.set_xlabel("Count")
                                st.pyplot(fig)

                        # Likert Scale Responses
                        st.markdown("### Likert Scale Responses")
                        likert_responses = df[df["type"] == "likert_scale"]
                        if not likert_responses.empty:
                            for question in likert_responses["question"].unique():
                                st.write(f"**{question}**")
                                data = likert_responses[likert_responses["question"] == question]["answer"]
                                fig, ax = plt.subplots()
                                sns.histplot(data, bins=5, kde=False, ax=ax)
                                ax.set_xlabel("Likert Scale")
                                st.pyplot(fig)

                        # Advanced Analytics for Open-Ended Questions
                        st.subheader("Advanced Open-Ended Question Analysis")
                        open_ended_responses = df[df["type"] == "open_ended"]

                        if not open_ended_responses.empty:
                            # Concatenate all open-ended responses for analysis
                            open_text = " ".join(open_ended_responses["answer"])

                            # Keyword Extraction
                            st.markdown("### Key Topics in Open-Ended Responses")
                            vectorizer = CountVectorizer(stop_words=stopwords.words('english'), max_features=10)
                            word_counts = vectorizer.fit_transform(open_ended_responses["answer"])
                            keywords = vectorizer.get_feature_names_out()

                            st.write("**Top Keywords**:")
                            for keyword in keywords:
                                st.write(f"- {keyword}")

                            # Sentiment Analysis
                            st.markdown("### Sentiment Analysis")
                            open_ended_responses["sentiment"] = open_ended_responses["answer"].apply(
                                lambda text: TextBlob(text).sentiment.polarity
                            )
                            avg_sentiment = open_ended_responses["sentiment"].mean()
                            st.write(f"**Average Sentiment Score**: {avg_sentiment:.2f}")
                            st.write("Scores closer to -1 indicate negative sentiment, while scores closer to +1 indicate positive sentiment.")

                            # Word Cloud for Visualization of Keywords
                            st.markdown("### Word Cloud")
                            wordcloud = WordCloud(width=800, height=400, stopwords=set(stopwords.words('english'))).generate(open_text)
                            fig, ax = plt.subplots()
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            st.pyplot(fig)

                            # Topic Modeling using LDA
                            st.markdown("### Topic Modeling")
                            lda = LatentDirichletAllocation(n_components=3, random_state=0)
                            lda.fit(word_counts)

                            # Display topics
                            for idx, topic in enumerate(lda.components_):
                                st.write(f"**Topic {idx + 1}**:")
                                st.write(", ".join([keywords[i] for i in topic.argsort()[-5:]]))

                    else:
                        st.info("No responses available for this survey.")
                else:
                    st.error("Survey data not found. Please check the Survey ID.")
        else:
            st.warning("Please enter a valid Survey ID.")

# Run the analytics dashboard
if __name__ == "__main__":
    show_survey_reports()