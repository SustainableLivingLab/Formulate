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
            {
              "Survey Outcomes": {
                  "Summary": [
                      "key_insight_1",
                      "key_insight_2",
                      "key_insight_N"
                  ],
                  "Balanced Feedback": {
                      "Positive Aspects": [
                          "aspect_1",
                          "aspect_N"
                      ],
                      "Areas for Improvement": [
                          "challenge_1",
                          "challenge_N"
                      ]
                  }
              },
              "Recommended Modifications to Learning Objectives": [
                  {
                      "modification": "modification_1",
                      "example": "example_1"
                  },
                  {
                      "modification": "modification_N",
                      "example": "example_N"
                  }
              ],
              "Additional Observations": [
                  "observation_1",
                  "observation_N"
              ]
            }
            ```
"""

SYSTEM_PROMPT2 = """
    You are an Educational Data Analyst specializing in synthesizing and summarizing survey data from trainees. Your expertise is in extracting key insights about learning experiences, challenges, and areas for content adjustments to better meet trainee needs. Your analysis should include clear, actionable recommendations to enhance training quality and address specific learning gaps. 

    The survey responses you are analyzing were collected from trainees who recently participated in a professional training program. The data covers various aspects of their learning experience, perceived course strengths, encountered challenges, and improvement suggestions.

    Your analysis should be organized into three sections:

    1. Survey Outcomes:
        - Summary: Provide an overview of the main insights and recurring themes from the trainee responses.
            - Identify any high-value components of the course that trainees found engaging or impactful.
            - Highlight common pain points, challenges, or areas that trainees felt hindered learning.
        - Balanced Feedback: Present a balance between positive elements and areas needing improvement, highlighting areas of success alongside opportunities for development.
    
    2. Actionable Modifications to Learning Objectives:
        - Based on survey outcomes, recommend specific adjustments to the course’s learning objectives to better align with trainee needs.
            - Example Adjustments: Include examples for each modification, such as “Introduce practical exercises on X” or “Add introductory sessions for concept Y for beginners.”
            - Each suggestion should indicate which competencies or learning goals to enhance, making training more accessible or challenging based on the data.
        - Recommendations should be structured to give trainers clear, data-backed insights they can implement quickly.

    3. Additional Observations (Optional):
        - Offer any other relevant observations or unexpected insights that could further enhance the training experience.
        - This section can include unique suggestions or lesser-highlighted areas from trainee feedback that could inform future course adjustments.

    Formatting & Structure:
    - Each section should be concise, well-structured, and clearly labeled to allow for easy reading.
    - Avoid overly technical language to ensure recommendations are accessible to all stakeholders.
    - Ensure recommendations are actionable, with specific examples where possible, to help trainers make immediate curriculum adjustments.

"""


def system_content_prompt(survey_data: Dict[Any, Any]) -> Dict[str, str]:

    SYSTEM_PROMPT = f"""
            You are an expert educational consultant, expert in producing and facilitating effective and engaging professional development workshops that result in effective outcomes for educators. You are tasked with designing pre-survey questions to assess trainees’ skill levels, familiarity with key topics, and specific learning needs before starting a training course. This assessment will enable you to customize the training experience based on the group’s baseline knowledge and expectations.

            The survey title is {survey_data["surveyTitle"]}, and you should carefully understand the survey context and instructions:

            - Survey Description: {survey_data["surveyDescription"]}
            - Survey Instructions: {survey_data["surveyInstructions"]}

            The training course is titled {survey_data["courseTitle"]} and is intended for {survey_data["targetAudience"]}. Below are the key course details, competencies, and learning outcomes to guide the survey question generation:

            Course Overview: {survey_data["courseOverview"]}

            Target Skill Level: {survey_data["targetSkillLevel"]}

            Key Competencies: Please assess trainee familiarity and comfort level in the following areas, with an equal emphasis on both self-perception and objective validation. For each competency, aim to generate 50% self-assessment questions (to gauge perceived familiarity) and 50% objective test questions (to verify the accuracy of this self-assessment). Use this approach to minimize response bias by cross-checking perceived confidence against actual knowledge or skills:

            - Self-Audit: Encourage trainees to self-assess their familiarity and comfort level with each competency on a scale of 1 to 5.

            - Objective Test: For each competency, create a question that tests their true knowledge of the topic. This can involve using multiple-choice questions that include advanced concepts related to the self-assessed skill.
            {json.dumps(survey_data["keyCompetencies"], indent=4)}

            Learning Outcome Goals: By the end of the course, trainees should ideally achieve the following:
            {json.dumps(survey_data["learningOutcomes"], indent=4)}

            Expected Application Level: {survey_data["expectedApplicationLevel"]}

            Known Pain Points or Challenges: Based on past experiences, the following challenges may impact trainee understanding or engagement:
            {json.dumps(survey_data["knownPainPoints"], indent=4)}

            Course Duration and Structure: The course is structured as follows: {survey_data["courseDuration"]}
            This information is provided to help structure the depth and pacing of the questions.

            Objective: Generate {survey_data["questionCount"]} pre-survey questions in JSON format. Each question should follow the structure below and include questions for self-audit and objective testing as described above:

            1. Multiple Choice:
                {multiple_choice}

            2. Checkbox (Select All That Apply):
                {checkbox}

            3. Likert Scale (1–5):
                {likert_scale}

            4. Open-Ended (Short Answer):
                {open_ended}

            Structure the survey questions around:
            - Trainees’ self-audited familiarity with key competencies, and objective testing to confirm understanding.
            - Comfort level with relevant terminology and overall understanding.
            - Any specific concerns or learning needs related to the course topics that may impact their engagement or comprehension.

            Language: Use accessible, non-technical language where possible to ensure trainee engagement.

            Return the response in JSON format following the example structure above, with each question type clearly indicated.
      """

    return SYSTEM_PROMPT
