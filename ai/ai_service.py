from typing import Dict, Any
from ai.system_content import system_content_prompt, SYSTEM_PROMPT2
from ai.generate import surveyQuestions, analysisTQ

import json
import streamlit as st


def generate_survey_questions(survey_data: Dict[Any, Any]) -> Dict[str, str]:
    SYSTEM_PROMPT = system_content_prompt(survey_data)
    try:
        
        surveyQuestion = surveyQuestions(SYSTEM_PROMPT=SYSTEM_PROMPT,survey_data=survey_data)
        # creating another function
        
        surveyQuestion = surveyQuestions(
            SYSTEM_PROMPT=SYSTEM_PROMPT, survey_data=survey_data
        )

        # store the ai result into json format
        return surveyQuestion

    except Exception as e:
        print(e)
        
# Separated  function
def generate_analysed_questionare(survey_data: Dict[Any, Any]) -> Dict[str, str]:
    try:
        analysisTrainerQuestionare = analysisTQ(SYSTEM_PROMPT=SYSTEM_PROMPT2,survey_data=survey_data)
        return analysisTrainerQuestionare
    
    #TO DO, in where this code will be executed?
    except Exception as e:
        print(e)
        
