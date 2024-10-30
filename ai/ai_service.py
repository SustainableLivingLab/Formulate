from typing import Dict, Any
from ai.generate import analysisTQ,multipleChoices,checkBoxes,likertS, openED
import asyncio
import json


async def generate_survey_questions(survey_data: Dict[Any, Any]) -> Dict[str, str]:
    analyse = await analysisTQ(survey_data)
    multipleChocies = await multipleChoices(data=survey_data, analysed_data=analyse)
    checkbox = await checkBoxes(data=survey_data, analysed_data=analyse)
    likert_scale = await likertS(data=survey_data, analysed_data=analyse)
    open_ended = await openED(data=survey_data, analysed_data=analyse)
    
    # Menggabungkan semua hasil menjadi satu daftar `survey_questions`
    survey_questions = []

    # Tambahkan setiap hasil dari fungsi ke dalam survey_questions
    survey_questions.append(multipleChocies)  # multiple_choice questions
    survey_questions.append(checkbox)          # checkbox questions
    survey_questions.append(likert_scale)      # likert scale questions
    survey_questions.append(open_ended)        # o
    
    return {"survey_questions": survey_questions}
    
