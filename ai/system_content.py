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
            "Summarisation" :[
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
            {
                  "slide_1": {
                    "title": "Introduction to [Lesson Topic]",
                    "content": "This lesson covers the fundamental concepts of [Topic]. By the end of this session, you will understand [key points or objectives]. Let's explore the core ideas that will guide us through this lesson."
                  },
                  "slide_2": {
                    "title": "Lesson Objectives",
                    "content": "1. Understand [main concept].\n2. Identify key components of [related topic].\n3. Demonstrate the ability to [skill or application].\n4. Analyze [specific case or problem]."
                  },
                  "slide_3": {
                    "title": "Background on [Topic]",
                    "content": "[Explain any historical context, prior knowledge required, or reasons why this topic is essential]. This sets the stage for a deeper exploration of [main concept]."
                  },
                  "slide_4": {
                    "title": "Understanding [Key Concept 1]",
                    "content": "[Brief explanation of the concept]. Learn how [Key Concept 1] affects or relates to [overall topic]."
                  },
                  "slide_5": {
                    "title": "In-depth Look at [Key Concept 1]",
                    "content": "Explore how [concept] is applied in [real-world example or specific field]. Analyze the steps involved in [process or method]."
                  },
                  "slide_6": {
                    "title": "Exploring [Key Concept 2]",
                    "content": "Discover the role of [Key Concept 2] and how it contributes to [larger topic]."
                  },
                  "slide_7": {
                    "title": "Practical Application of [Topic]",
                    "content": "See [how the concept is used in an industry/application]. Learn from a case study of [real-world example]."
                  },
                  "slide_8": {
                    "title": "Recap of Key Concepts",
                    "content": "- [Concept 1]\n- [Concept 2]\n- [Application/Case Study insight]\nThese key points will be essential for our concluding discussions and assessments."
                  },
                  "slide_9": {
                    "title": "Interactive Activity",
                    "content": "Try solving [problem statement or question]. Discuss your approach or answer with a peer/group."
                  },
                  "slide_10": {
                    "title": "Conclusion and What's Next",
                    "content": "In this lesson, you learned about [summary of the lesson]. Prepare for our next session by [assignment or preparation task]."
                  }
            }

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
  
# SYSTEM PROMPT FOR THE SLIDE DECK GENERATOR  
SYSTEM_PROMPT3 = """
        You are an assistant who made the slide deck generator based on the summary provided by professional education trainers. 
        Your task is to carefully review and synthesise the collected responses to generate a comprehensive lessons content.
  
  """
