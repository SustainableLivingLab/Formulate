from typing import Dict, Any
from ai.system_content import system_content_prompt
from ai.generate import surveyQuestions
import asyncio
import json


async def generate_survey_questions(survey_data: Dict[Any, Any]) -> Dict[str, str]:
    SYSTEM_PROMPT = system_content_prompt(survey_data)
    try:
        
        surveyQuestion = await surveyQuestions(SYSTEM_PROMPT=SYSTEM_PROMPT,survey_data=survey_data)
    
        # store the ai result into json format
        survey_results = {
            "questions": []
        }
        survey_results.extend(json.loads(surveyQuestion)["questions"])
        
        return survey_results  
    
    except Exception as e:
        print(e)
        
