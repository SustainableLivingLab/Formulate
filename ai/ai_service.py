from typing import Dict, Any
from ai.system_content import system_content_prompt, SYSTEM_PROMPT2, SYSTEM_PROMPT3
from ai.generate import surveyQuestions, analysis_Trainee_Response, SlideDeckGenerator

import json
import streamlit as st


# CODE TO GENERATE SURVEY QUESTIONS
def generate_survey_questions(survey_data: Dict[Any, Any]) -> Dict[str, Any]:
    SYSTEM_PROMPT = system_content_prompt(survey_data)
    try:

        surveyQuestion = surveyQuestions(
            SYSTEM_PROMPT=SYSTEM_PROMPT, survey_data=survey_data
        )
        # creating another function

        surveyQuestion = surveyQuestions(
            SYSTEM_PROMPT=SYSTEM_PROMPT, survey_data=survey_data
        )

        # store the ai result into json format
        return surveyQuestion

    except Exception as e:
        print(e)


# CODE TO GENERATE AI SUMMARY
def generate_AI_summarisation(survey_data: str):
    try:
        AI_summarastion = analysis_Trainee_Response(
            SYSTEM_PROMPT=SYSTEM_PROMPT2, survey_responses=survey_data
        )

        print(f"DEBUG : AI summarisation result {AI_summarastion}")
        return AI_summarastion

    # TO DO, in where this code will be executed?
    except Exception as e:
        print(e)


# CODE TO GENERATE SLIDE DECK GENERATOR FOR LESSON CONTENT
def generate_slide_deck(ai_summary: str):
    try:
        Slide_deck = SlideDeckGenerator(
            SYSTEM_PROMPT=SYSTEM_PROMPT3, AI_Summary=ai_summary
        )

        print(f"DEBUG : AI Lesson Content Result {Slide_deck}")

        return Slide_deck

    except Exception as e:
        print(e)
