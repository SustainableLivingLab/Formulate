import json
from typing import Dict, Any

multiple_choice = """
            ```
            "questions": [
            {
              "type": "multiple_choice",
              "question_text": "Your question here",
              "options": ["Option 1", "Option 2", "Option 3"]
            }
            ]
            ```

"""

checkbox = """
            ```
             "questions": [
            {
              "type": "checkbox",
              "question_text": "Your question here",
              "options": ["Option 1", "Option 2", "Option 3"]
            }
            ]
            ```

"""

likert_scale = """
            ```
            "questions": [
            {
              "type": "likert_scale",
              "question_text": "Your question here",
              "scale": {
                "min_label": "Not comfortable",
                "max_label": "Very comfortable",
                "range": [1, 2, 3, 4, 5]
              }
            }
            ]
            ```

"""

open_ended = """
            ```
           "questions": [
            {
              "type": "open_ended",
              "question_text": "Your question here"
            }
            ]
            ```

"""


analysed_data = """
            ```
            "analysed_data" :[
                {
                    "Survey outcome": [
                          "key_insight_1",
                          "key_insight_2",
                          "key_insight_N"
                          ],
                    "Recommended Modification to learning Objectives" : [
                          "modification_1",
                          "modification_N",
                          ]
                }

            ```


  """
  
 #need to be improve again 
Slide_Deck_Output = """
            ```
            "Slide_Deck_Content" : [
              {
                    "Introduction": "Explain the lesson objectives, focusing on why they are important and what students will learn by the end of the lesson.",
                    "opening_activity": "Describe what students did in the previous lesson, highlighting any key concepts that will connect to today's lesson.",
                    "main_activity": "Provide a step-by-step overview of the main activities, ensuring they are interactive and encourage student participation.",
                    "closing_activity": "Suggest a brief closing activity that reinforces the main takeaways and allows students to reflect on what they've learned.",
                    "assessment": [
                      "Create a question that asks students to summarize the main ideas discussed today.",
                      "Develop a question that prompts students to apply today's lesson concepts to a real-life scenario.",
                      "Generate a critical thinking question related to the topic to assess deeper understanding."
                    ]
                  }
            ]
            
            ```

"""

SYSTEM_PROMPT2 = """

You are assisting in the analysis of responses provided by professional education trainers to survey questions regarding educational practices and objectives. Your task is to carefully review and synthesise the collected responses to generate a comprehensive summary.

This summary should be divided into two distinct sections:

1. Survey Outcome

2. Recommended Modifications to Learning Objectives
"""

def system_content_prompt(survey_data: Dict[Any, Any]) -> Dict[str, str]:

    # PROMPT FOR GENERATE SURVEY
    SYSTEM_PROMPT = f"""
          You are a Lead Corporate Trainer tasked with designing pre-survey questions to assess trainees’ skill levels, familiarity with key topics, and specific learning needs before starting a training course. This assessment will allow you to customize the training experience based on the group’s baseline knowledge and expectations.

          the survey title is {survey_data["surveyTitle"]} and you have to understand the survey context and what is the instructions
          
          - Survey Description : {survey_data["surveyDescription"]}
          - Survey Instruction : {survey_data["surveyInstructions"]}
          
          The training course is titled {survey_data["courseTitle"]} and is intended for {survey_data["targetAudience"]}. Below are the key course details, competencies, and learning outcomes, which should guide the survey question generation:

          Course Overview: {survey_data["courseOverview"]}

          Target Skill Level: {survey_data["targetSkillLevel"]}

          Key Competencies: Please assess trainee familiarity and comfort level in the following areas:
          {json.dumps(survey_data["keyCompetencies"], indent=4)}

          Learning Outcome Goals: By the end of the course, trainees should ideally achieve the following:
          {json.dumps(survey_data["learningOutcomes"], indent=4)}

          Expected Application Level: {survey_data["expectedApplicationLevel"]}

          Known Pain Points or Challenges: Based on past experiences, the following challenges may impact trainee understanding or engagement:
          {json.dumps(survey_data["knownPainPoints"], indent=4)}

          Course Duration and Structure: The course is structured as follows: {survey_data["courseDuration"]}
          This information is provided to help structure the depth and pacing of the questions.

          Objective: Generate {survey_data["questionCount"]} pre-survey questions in JSON format. Each question should follow the structure below:

          1. Multiple Choice:
              {multiple_choice}

          2. Checkbox (Select All That Apply):
              {checkbox}

          3. Likert Scale (1–5):
              {likert_scale}

          4. Open-Ended (Short Answer):
              {open_ended}

          Structure the survey questions around:
          - Trainees’ familiarity with the key competencies listed above.
          - Comfort level with relevant terminology and overall understanding.
          - Any specific concerns or learning needs related to the course topics that may impact their engagement or comprehension.

          Return the response in JSON format following the example structure above, with each question type clearly indicated.
      """

    return SYSTEM_PROMPT
  
  
SYSTEM_PROMPT3 = """
        bakal di isi secepatnya
  
  """
