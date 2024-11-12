from typing import Dict, Any
from ai.system_content import system_content_prompt, SYSTEM_PROMPT2
from ai.generate import surveyQuestions, analysis_Trainee_Response

import json
import streamlit as st


# CODE TO GENERATE SURVEY QUESTIONS
def generate_survey_questions(survey_data: Dict[Any, Any]) -> Dict[str, Any]:
    SYSTEM_PROMPT = system_content_prompt(survey_data)
    try:
        survey_question = surveyQuestions(
            SYSTEM_PROMPT=SYSTEM_PROMPT, survey_data=survey_data
        )

        # Store the AI-generated result in JSON format and return it
        return survey_question

    except Exception as e:
        print(f"Error generating survey questions: {e}")
        return {}


# CODE TO GENERATE AI SUMMARY
def generate_AI_summarisation(survey_data: str) -> Dict[str, Any]:
    try:
        ai_summarisation = analysis_Trainee_Response(
            SYSTEM_PROMPT=SYSTEM_PROMPT2, survey_responses=survey_data
        )

        print(f"DEBUG: AI summarisation result: {ai_summarisation}")
        return ai_summarisation

    except Exception as e:
        print(f"Error generating AI summarisation: {e}")
        return {}
