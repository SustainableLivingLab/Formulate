import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

# Inisialisasi client dengan API key
client = OpenAI(
    api_key=api_key,
)


class GptModels:
    OPENAI_MODEL = "gpt-4o-2024-08-06"










