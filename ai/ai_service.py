from typing import Dict, Any
from ai.system_content import system_content_prompt, SYSTEM_PROMPT2, SYSTEM_PROMPT3
from ai.generate import surveyQuestions, analysisTQ, SlideDeckGenerator

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
def generate_analysed_questionare(survey_data: str):
    try:
        analysisTrainerQuestionare = analysisTQ(SYSTEM_PROMPT=SYSTEM_PROMPT2,survey_responses=survey_data)
        
        print(f"DEBUG : AI summarisation result {analysisTrainerQuestionare}")
        return analysisTrainerQuestionare
    
    #TO DO, in where this code will be executed?
    except Exception as e:
        print(e)
 
 
# For Slide Deck Generator        
def generate_slide_deck(ai_summary: str):
    Slide_deck = SlideDeckGenerator(SYSTEM_PROMPT=SYSTEM_PROMPT3, AI_Summary=ai_summary)
    return Slide_deck 
