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
    survey_results = {
    "analysed_data": [],
    "questions": []
}

    survey_results["analysed_data"].extend(json.loads(analyse)["analysed_data"])
    survey_results["questions"].extend(json.loads(multipleChocies)["questions"])
    survey_results["questions"].extend(json.loads(checkbox)["questions"])
    survey_results["questions"].extend(json.loads(likert_scale)["questions"])
    survey_results["questions"].extend(json.loads(open_ended)["questions"])
    
    return survey_results
    
