import os
from openai import OpenAI
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

# Inisialisasi client dengan API key
client = OpenAI(
    api_key=api_key,
)


# Establish the database connection
conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_SECRET_KEY'),
    database=os.getenv('MYSQL_DATABASE')
)



class GptModels:
    OPENAI_MODEL = "gpt-4o-2024-08-06"










