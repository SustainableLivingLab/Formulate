import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_PORT = os.getenv('APP_PORT')
    APP_DEBUG = os.getenv('APP_DEBUG')
    BASIC_AUTH_USERNAME = os.getenv('BASIC_AUTH_USERNAME')
    BASIC_AUTH_PASSWORD = os.getenv('BASIC_AUTH_PASSWORD')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    FREEPIK_API_KEY = os.getenv('FREEPIK_API_KEY')
