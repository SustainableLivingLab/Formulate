import streamlit as st
from openai import OpenAI

# Get API key directly from Streamlit secrets
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    print("DEBUG: OpenAI API key loaded from Streamlit secrets")
except Exception as e:
    print(f"DEBUG: Error loading OpenAI API key from Streamlit secrets: {e}")
    raise Exception("OpenAI API key not found in Streamlit secrets. Please add it in the Streamlit dashboard.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

class GptModels:
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"










