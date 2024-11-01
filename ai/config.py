from openai import AsyncOpenAI



api_key = "OPENAI_API_KEY"

# Inisialisasi client dengan API key
client = AsyncOpenAI(
    api_key=api_key,
)


class GptModels:
    OPENAI_MODEL = "gpt-4o-2024-08-06"










