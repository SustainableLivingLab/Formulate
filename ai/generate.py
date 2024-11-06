import asyncio
import openai
import json

from ai.config import GptModels
from typing import Dict, Any

from ai.config import GptModels, client
from ai.system_content import multiple_choice, checkbox, likert_scale, open_ended,analysed_data

model = GptModels.OPENAI_MODEL


def surveyQuestions(SYSTEM_PROMPT: str,survey_data: Dict[Any, Any]) -> Dict[str, str]:
    print(f"DEBUG: Received survey_data: {survey_data}")
    print(f"DEBUG: Question count from trainer: {survey_data.get('questionCount')}")
      
    section = "survey Questions" 
    
    try:
        surveyQuestions = client.chat.completions.create(
            model = model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"""
                     Provide the  Survey Questions Generation based on a comprehensive analysis ,adhering to the following guidelines:
                1. ensure the output in json structure
                2. Ensure the text in formal British English, ensuring advanced grammar, precision, and professionalism tone              
                3. Develop a set of {survey_data["questionCount"]} questions, ensuring a diverse range of question types, including multiple-choice, checkbox, Likert scale, and open-ended questions.

                Structure Guide as the reference : 

                1. Multiple Choice:
                    {multiple_choice}

                2. Checkbox (Select All That Apply):
                    {checkbox}

                3. Likert Scale (1–5):
                    {likert_scale}

                4. Open-Ended (Short Answer):
                    {open_ended}

                """
                
                ,
                },
                
            ],
            response_format = {"type": "json_object"} ,
            max_tokens=16384,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
            n=1  # Number of responses to generate at a time
        )
        # Cek apakah output dari completion kosong atau null
        surveyQuestionsResult = surveyQuestions.choices[0].message.content.strip()
        if not surveyQuestionsResult:  # if there is no output, do retry
             
            raise print("Chat Completion output in {section} is empty, retrying...")
                
        surveyQuestionsResult = surveyQuestions.choices[0].message.content
        print(f"{section} : OK")
         
        return surveyQuestionsResult
    except openai.AuthenticationError as e:
        print(f"Your API key or token was invalid, expired, or revoked : {e}")
         
        raise
    except openai.BadRequestError as e:
        print(f"Your request was malformed or missing some required parameters, such as a token or an input in {section} : {e}")
         
        raise
    except openai.ConflictError as e:
        print(f"The resource was updated by another request in {section} : {e}")
         
        raise
    except openai.InternalServerError as e:
        print(f"Issue on our side while completing in {section} : {e}")
         
        raise
    except openai.NotFoundError as e:
        print(f"Requested resource does not exist while completing in {section} : {e}")
         
        raise
    except openai.APITimeoutError as e:
        print(f"Request timed out in {section} : {e}")
         
        raise
    except openai.UnprocessableEntityError as e:
        print(f"Unable to process the request despite the format being correct in {section}: {e}")
         
        raise
    except openai.PermissionDeniedError as e:
        print(f"You don't have access to the requested resource while completing the {section}: {e}")
         
        raise
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error in {section}: {e}")
         
        raise #Lempar ulang error
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API in {section}: {e}")
         
        raise #Lempar ulang error
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit in {section}: {e}")
         
        raise #Lempar ulang error

def analysisTQ(SYSTEM_PROMPT: str,survey_responses: str):
    section = "Anlysed summarisation Trainer Questionare" 
    
    try:
        analysisTQ = client.chat.completions.create(
        model = model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"""

                1. Analyze and summarize the responses provided by professional education trainers to the recent questionnaire. The analysis should be presented in two main sections:

                  - **Survey Outcome** – Identify and evaluate the key insights shared by trainers. Focus on any recurring themes, patterns, or notable points that reflect common perspectives or diverging views. Additionally, interpret how these insights might impact the effectiveness of current learning objectives.

                  - **Recommended Modifications to Learning Objectives** – Based on the survey feedback, propose and justify specific, actionable changes to improve clarity, engagement, and measurable impact of the learning objectives. These modifications should aim to help learners better understand, apply, and master the content.

                2. Structure each section in short, highlighted bullet points to enhance clarity and readability.

                **Data for analysis**: {survey_responses}

                **Response Format (JSON)**:
                Provide a response strictly in JSON format, with each section following this structure:


                {analysed_data}

                Ensure the response in JSON format following the example structure above, with each question type clearly indicated.


                IMPORTANT CONSTRAINT

                1. do not provide any other output than in json formated structure question guidance



                """
                ,
                            },

                ],
                response_format = { "type": "json_object" } ,
                max_tokens=16384,
                temperature=0.5,
                presence_penalty=0.6,
                top_p=0.8,
                n=1  # Number of responses to generate at a time
                )

        # Cek apakah output dari completion kosong atau null
        TQ_analysis = analysisTQ.choices[0].message.content.strip()
        if not TQ_analysis:  # if there is no output, do retry
             
            raise print("Chat Completion output in {section} is empty, retrying...")
                
        TQ_analysis = analysisTQ.choices[0].message.content
        print(f"{section} : OK")
         
        return TQ_analysis
    except openai.AuthenticationError as e:
        print(f"Your API key or token was invalid, expired, or revoked : {e}")
         
        raise
    except openai.BadRequestError as e:
        print(f"Your request was malformed or missing some required parameters, such as a token or an input in {section} : {e}")
         
        raise
    except openai.ConflictError as e:
        print(f"The resource was updated by another request in {section} : {e}")
         
        raise
    except openai.InternalServerError as e:
        print(f"Issue on our side while completing in {section} : {e}")
         
        raise
    except openai.NotFoundError as e:
        print(f"Requested resource does not exist while completing in {section} : {e}")
         
        raise
    except openai.APITimeoutError as e:
        print(f"Request timed out in {section} : {e}")
         
        raise
    except openai.UnprocessableEntityError as e:
        print(f"Unable to process the request despite the format being correct in {section}: {e}")
         
        raise
    except openai.PermissionDeniedError as e:
        print(f"You don't have access to the requested resource while completing the {section}: {e}")
         
        raise
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error in {section}: {e}")
         
        raise #Lempar ulang error
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API in {section}: {e}")
         
        raise #Lempar ulang error
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit in {section}: {e}")
         
        raise #Lempar ulang error
