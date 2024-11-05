import asyncio
import openai
import json

from ai.config import GptModels
from typing import Dict, Any

from ai.config import GptModels, client
from ai.system_content import multiple_choice, checkbox, likert_scale, open_ended,analysed_data

model = GptModels.OPENAI_MODEL


def surveyQuestions(SYSTEM_PROMPT: str,survey_data: Dict[Any, Any]) -> Dict[str, str]:
      
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

                1. analyse and summarise the responses provided by professional education trainers to the recent survey question. Your analysis should cover two sections:

                    - Survey Outcome – Identify and evaluate the main insights shared by trainers. Examine any recurring themes, patterns, or significant points that illustrate common perspectives or diverging views. Interpret how these themes might influence the effectiveness of the learning objectives.
                    - Recommended Modifications to Learning Objectives – Recommend and justify specific adjustments to the learning objectives based on the feedback. Construct actionable modifications that could improve learners' ability to understand, apply, and master the objectives. Ensure these modifications aim to increase clarity, engagement, and measurable impact on learning outcomes/
                
                2. each section should be  provided  short explanations in highlight points.
                
                Data to be analysed : {survey_responses}
                
                respond in the following JSON format, filling in each section with a thorough yet concise analysis:

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
