from openai import AsyncOpenAI



api_key = "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"

# Inisialisasi client dengan API key
client = AsyncOpenAI(
    api_key=api_key,
)


class GptModels:
    OPENAI_MODEL = "gpt-4o-2024-08-06"










