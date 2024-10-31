import asyncio
import openai
import json

from ai.config import GptModels
from tenacity import retry, stop_after_attempt, wait_random_exponential
from aiocache import cached, Cache
from typing import Dict, Any

from ai.config import GptModels, client
from ai.system_content import SYSTEM_PROMPT, SYSTEM_PROMPT2, multiple_choice, checkbox, likert_scale, open_ended,analysed_data

model = GptModels.OPENAI_MODEL

@cached(ttl=3600)
@retry(wait=wait_random_exponential(min=1, max=50), stop=stop_after_attempt(5))
async def analysisTQ(data: Dict[Any, Any]) -> Dict[str, str]:
      
    section = "analysisTQ" 
        
    string_data = {str(key): str(value) for key, value in data.items()}    
    try:
        analysisTQ = await client.chat.completions.create(
            model = model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT2,
                },
                {
                    "role": "user",
                    "content": f"""
                    Generate an analysis report based on the Trainer Questionnaire, adhering to the following guidelines:

                    1. Examine and interpret the provided data in Trainer Questionnaire responses to identify insights regarding the context of the learning outcomes. Assess patterns or significant factors that may contribute to or challenge learning success.

                    2. Compose the report in formal British English, demonstrating advanced grammar, precision, and professionalism. Employ refined language with a seamless flow, reflecting the sophistication expected in high-level writing.

                    3. Structure the content into five distinct paragraphs, each synthesising key insights and observations from the data to provide a comprehensive and cohesive analysis.


                    Data To be analysed : {string_data}
                    
                 
                
                    The output should be in json format with the following structure:

                    {analysed_data}

                    Ensure the response in JSON format following the example structure above, with each question type clearly indicated.


                    IMPORTAN CONSTRAINT
                    1. do not provide any other output than in json formated structure question guidance


                """,
                },
                
            ],
            response_format={ "type": "json_object" },
            max_tokens=10000,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
            n=1  # Number of responses to generate at a time
            # seed=10
        )
        # Cek apakah output dari completion kosong atau null
        TQ_analysis = analysisTQ.choices[0].message.content.strip()
        if not TQ_analysis:  # if there is no output, do retry
            await asyncio.sleep(3)
            raise print("Chat Completion output in {section} is empty, retrying...")
                
        TQ_analysis = analysisTQ.choices[0].message.content
        print("{section} : OK")
        await asyncio.sleep(3)
        return TQ_analysis
    except openai.AuthenticationError as e:
        print(f"Your API key or token was invalid, expired, or revoked : {e}")
        await asyncio.sleep(3)
        raise
    except openai.BadRequestError as e:
        print(f"Your request was malformed or missing some required parameters, such as a token or an input in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.ConflictError as e:
        print(f"The resource was updated by another request in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.InternalServerError as e:
        print(f"Issue on our side while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.NotFoundError as e:
        print(f"Requested resource does not exist while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.APITimeoutError as e:
        print(f"Request timed out in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.UnprocessableEntityError as e:
        print(f"Unable to process the request despite the format being correct in {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.PermissionDeniedError as e:
        print(f"You don't have access to the requested resource while completing the {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error


@cached(ttl=3600)
@retry(wait=wait_random_exponential(min=1, max=50), stop=stop_after_attempt(5))
async def multipleChoices(data: Dict[Any, Any], analysed_data: str) -> Dict[str, str]:
    
    section = "multipleChoices"
    
    target_audience = str(data.get("targetAudience", ""))
    target_skill_level = str(data.get("targetSkillLevel", ""))
    number_questions = str(data.get("questionCount", ""))
           
    try:
        analysisTQ = await client.chat.completions.create(
            model = model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                "content": f"""

                Provide the Multiple choice Survey Questions Generation based on a comprehensive analysis, adhering to the following guidelines:      

                1. analyse the provided data Trainer Questionnaire Responses to need understand the context of the learning outcome.
                2. Ensure the the question text made in British English, the tone should be reflect on the {target_audience}.
                3. After analyzing the context ,formulate the question  difficulty based on the {target_skill_level}
                4. The total question should be reflect on the {number_questions}, ensure all the question in the multiple choice format.

                Data To be analysed : {analysed_data}

                structure question Guide each question in json format: 

                {multiple_choice}
                
                store all of the questions  in one JSON format.
                Ensure the response in JSON format following the example structure above, with each question type clearly indicated.


                IMPORTAN CONSTRAINT 
                1. do not provide any other output than in json formated structure question guidance

                """,
                },
                
            ],
            response_format={"type": "json_object"} ,
            max_tokens=10000,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
            n=1  # Number of responses to generate at a time
            # seed=10
        )
        # Cek apakah output dari completion kosong atau null
        mc_questions = multipleChoices.choices[0].message.content.strip()
        if not mc_questions:  # if there is no output, do retry
            await asyncio.sleep(3)
            raise print("Chat Completion output in {section} is empty, retrying...")
                
        mc_questions = analysisTQ.choices[0].message.content
        print("{section} : OK")
        await asyncio.sleep(3)
        return mc_questions
    except openai.AuthenticationError as e:
        print(f"Your API key or token was invalid, expired, or revoked : {e}")
        await asyncio.sleep(3)
        raise
    except openai.BadRequestError as e:
        print(f"Your request was malformed or missing some required parameters, such as a token or an input in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.ConflictError as e:
        print(f"The resource was updated by another request in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.InternalServerError as e:
        print(f"Issue on our side while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.NotFoundError as e:
        print(f"Requested resource does not exist while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.APITimeoutError as e:
        print(f"Request timed out in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.UnprocessableEntityError as e:
        print(f"Unable to process the request despite the format being correct in {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.PermissionDeniedError as e:
        print(f"You don't have access to the requested resource while completing the {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error



@cached(ttl=3600)
@retry(wait=wait_random_exponential(min=1, max=50), stop=stop_after_attempt(5))
async def checkBoxes(data: Dict[Any, Any], analysed_data: str) -> Dict[str, str]:
    
    section = "checkboxes"
    
    target_audience = str(data.get("targetAudience", ""))
    target_skill_level = str(data.get("targetSkillLevel", ""))
    number_questions = str(data.get("questionCount", ""))
           
    try:
        checkboxes = await client.chat.completions.create(
            model = model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                "content": f"""

                 Provide the Checkbox Survey Questions Generation based on a comprehensive analysis, adhering to the following guidelines:      

                1. analyse the provided data Trainer Questionnaire Responses to need understand the context of the learning outcome.
                2. Ensure the the question text made in British English, the tone should be reflect on the {target_audience}.
                3. After analyzing the context ,formulate the question  difficulty based on the {target_skill_level}
                4. The total question should be reflect on the {number_questions}, ensure all the question in the multiple choice format.

                Data To be analysed : {analysed_data}

                structure question Guide in json format: 

                {checkbox}

                store all of the questions  in one JSON format.
                Ensure the response in JSON format following the example structure above, with each question type clearly indicated.


                IMPORTAN CONSTRAINT 
                1. do not provide any other output than in json formated structure question guidance
                
                
                """,
                },
                
            ],
            response_format={ "type": "json_object" },
            max_tokens=10000,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
            n=1  # Number of responses to generate at a time
            # seed=10
        )
        # Cek apakah output dari completion kosong atau null
        CB_questions = checkboxes.choices[0].message.content.strip()
        if not CB_questions:  # if there is no output, do retry
            await asyncio.sleep(3)
            raise print("Chat Completion output in {section} is empty, retrying...")
                
        CB_questions = checkboxes.choices[0].message.content
        print("{section} : OK")
        await asyncio.sleep(3)
        return CB_questions
    except openai.AuthenticationError as e:
        print(f"Your API key or token was invalid, expired, or revoked : {e}")
        await asyncio.sleep(3)
        raise
    except openai.BadRequestError as e:
        print(f"Your request was malformed or missing some required parameters, such as a token or an input in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.ConflictError as e:
        print(f"The resource was updated by another request in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.InternalServerError as e:
        print(f"Issue on our side while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.NotFoundError as e:
        print(f"Requested resource does not exist while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.APITimeoutError as e:
        print(f"Request timed out in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.UnprocessableEntityError as e:
        print(f"Unable to process the request despite the format being correct in {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.PermissionDeniedError as e:
        print(f"You don't have access to the requested resource while completing the {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error



@cached(ttl=3600)
@retry(wait=wait_random_exponential(min=1, max=50), stop=stop_after_attempt(5))
async def likertS(data: Dict[Any, Any], analysed_data: str) -> Dict[str, str]:
    
    section = "likertS"
    
    target_audience = str(data.get("targetAudience", ""))
    target_skill_level = str(data.get("targetSkillLevel", ""))
    number_questions = str(data.get("questionCount", ""))
           
    try:
        likertS = await client.chat.completions.create(
            model = model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                "content": f"""

                 Provide the Likert Scale Survey Questions Generation based on a comprehensive analysis, adhering to the following guidelines:      

                1. analyse the provided data Trainer Questionnaire Responses to need understand the context of the learning outcome.
                2. Ensure the the question text made in British English, the tone should be reflect on the {target_audience}.
                3. After analyzing the context ,formulate the question  difficulty based on the {target_skill_level}
                4. The total question should be reflect on the {number_questions}, ensure all the question in the multiple choice format.

                Data To be analysed : {analysed_data}

                structure question Guide in json format: 

                {likert_scale}

                store all of the questions  in one JSON format.
                Ensure the response in JSON format following the example structure above, with each question type clearly indicated.


                IMPORTAN CONSTRAINT 
                1. do not provide any other output than in json formated structure question guidance
                
                
                """,
                },
                
            ],
            response_format={ "type": "json_object" },
            max_tokens=10000,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
            n=1  # Number of responses to generate at a time
            # seed=10
        )
        # Cek apakah output dari completion kosong atau null
        LS_questions = likertS.choices[0].message.content.strip()
        if not LS_questions:  # if there is no output, do retry
            await asyncio.sleep(3)
            raise print("Chat Completion output in {section} is empty, retrying...")
                
        LS_questions = likertS.choices[0].message.content
        print("{section} : OK")
        await asyncio.sleep(3)
        return LS_questions
    except openai.AuthenticationError as e:
        print(f"Your API key or token was invalid, expired, or revoked : {e}")
        await asyncio.sleep(3)
        raise
    except openai.BadRequestError as e:
        print(f"Your request was malformed or missing some required parameters, such as a token or an input in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.ConflictError as e:
        print(f"The resource was updated by another request in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.InternalServerError as e:
        print(f"Issue on our side while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.NotFoundError as e:
        print(f"Requested resource does not exist while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.APITimeoutError as e:
        print(f"Request timed out in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.UnprocessableEntityError as e:
        print(f"Unable to process the request despite the format being correct in {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.PermissionDeniedError as e:
        print(f"You don't have access to the requested resource while completing the {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit in {section}: {e}")
        await asyncio.sleep(3)
        
        
        
        
        raise #Lempar ulang error
@cached(ttl=3600)
@retry(wait=wait_random_exponential(min=1, max=50), stop=stop_after_attempt(5))
async def openED(data: Dict[Any, Any], analysed_data: str) -> Dict[str, str]:
    
    section = "openED"
    
    target_audience = str(data.get("targetAudience", ""))
    target_skill_level = str(data.get("targetSkillLevel", ""))
    number_questions = str(data.get("questionCount", ""))
           
    try:
        openED = await client.chat.completions.create(
            model = model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                "content": f"""

                 Provide the open ended Survey Questions Generation based on a comprehensive analysis, adhering to the following guidelines:      

                1. analyse the provided data Trainer Questionnaire Responses to need understand the context of the learning outcome.
                2. Ensure the the question text made in British English, the tone should be reflect on the {target_audience}.
                3. After analyzing the context ,formulate the question  difficulty based on the {target_skill_level}
                4. The total question should be reflect on the {number_questions}, ensure all the question in the multiple choice format.

                Data To be analysed : {analysed_data}

                structure question Guide in json format: 

                {open_ended}

                store all of the questions  in one JSON format.
                Ensure the response in JSON format following the example structure above, with each question type clearly indicated.


                IMPORTAN CONSTRAINT 
                1. do not provide any other output than in json formated structure question guidance
                
                
                """,
                },
                
            ],
            response_format={ "type": "json_object" },
            max_tokens=10000,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
            n=1  # Number of responses to generate at a time
            # seed=10
        )
        # Cek apakah output dari completion kosong atau null
        OE_questions = openED.choices[0].message.content.strip()
        if not OE_questions:  # if there is no output, do retry
            await asyncio.sleep(3)
            raise print("Chat Completion output in {section} is empty, retrying...")
                
        OE_questions = openED.choices[0].message.content
        print("{section} : OK")
        await asyncio.sleep(3)
        return OE_questions
    except openai.AuthenticationError as e:
        print(f"Your API key or token was invalid, expired, or revoked : {e}")
        await asyncio.sleep(3)
        raise
    except openai.BadRequestError as e:
        print(f"Your request was malformed or missing some required parameters, such as a token or an input in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.ConflictError as e:
        print(f"The resource was updated by another request in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.InternalServerError as e:
        print(f"Issue on our side while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.NotFoundError as e:
        print(f"Requested resource does not exist while completing in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.APITimeoutError as e:
        print(f"Request timed out in {section} : {e}")
        await asyncio.sleep(3)
        raise
    except openai.UnprocessableEntityError as e:
        print(f"Unable to process the request despite the format being correct in {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.PermissionDeniedError as e:
        print(f"You don't have access to the requested resource while completing the {section}: {e}")
        await asyncio.sleep(3)
        raise
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit in {section}: {e}")
        await asyncio.sleep(3)
        raise #Lempar ulang error
