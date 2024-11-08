function_intro = [
      {
        "name": "create_lesson_intro",
        "description": "Act as a teacher, create a beginning of lesson plan based on user input requirements. Do not add or remove any section from this function",
        "parameters": {
          "type": "object",
          "properties": {
            "topic": {
              "type": "string",
              "description": "The topic of the lesson. You need to extract the topic for this lesson from the user input. This is NOT tech domain"
            },
            "title": {
                "type": "string",
                "description": '''Create title for your lesson regarding to the topic, software used, and adjust the tone based on your student grade.
                Example for lower elementary student: 'Fun with Multiplication: Discovering Math with Python in Lower Elementary',
                Example for upper elementary student: 'Exploring Multiplication with Python: A Math Adventure!',
                Example for middle school student: 'Exploring Math with Python: A Fun Introduction to Coding',
                Example for high school student: 'Mastering Multiplication with Python: Advanced Techniques for High School Math'
                '''
            },
        },
         "required": [
            "topic",
            "title"
        ]
      }
    }]

function_tech_domain = [
      {
        "name": "select_tech_domain",
        "description": "Act as a teacher, you need to determine appropriate tech domain for your lesson plan",
        "parameters": {
          "type": "object",
          "properties": {
            "tech domain": {
              "type": "string",
              "description": "Select appropriate tech domain for the given topic and grade."
            },
        },
         "required": [
            "tech domain"
        ]
      }
    }]

function_software = [
      {
        "name": "select_software",
        "description": "Act as a teacher, you need to determine appropriate software for your lesson plan",
        "parameters": {
          "type": "object",
          "properties": {
            "software": {
              "type": "string",
              "description": "Select only ONE appropriate software to use for the teaching given topic and grade. You need to select the software based on its relevance in this sequence logic: tech domain relevance, topic relevance, and subject relevance ",

            },
        },
         "required": [
            "software"
        ]
      }
    }]

function_other_subject = [
  {
    "name": "select_other_subject",
    "description": "Act as a teacher, you need to determine appropriate subject for your lesson plan",
    "parameters": {
      "type": "object",
      "properties": {
        "subject": {
          "type": "string",
          "description": "Select appropriate subject for the given topic and grade. e.g Music, Physical Education, etc."
        },
    },
      "required": [
        "subject"
    ]
  }
}]

function_other_software = [
  {
    "name": "select_other_subject",
    "description": "Determine appropriate software for your lesson plan",
    "parameters": {
      "type": "object",
      "properties": {
        "software": {
          "type": "array",
          "description": "Determine appropriate software(s) for the given topic, subject, and grade, e.g. Scratch, Python, Canva, Adobe Photoshop, etc. IMPORTANT: Search what relevant software(s) from your knowledge, NOT only from the given example.",
          "items": {
                "type": "string"
              }
        },
    },
      "required": [
        "software"
    ]
  }
}]

function_summary = [
      {
        "name": "create_lesson_summary",
        "description": "Act as a teacher, create a brief lesson summary based on the given lesson overview",
        "parameters": {
          "type": "object",
          "properties": {
            "summary": {
              "type": "string",
              "description": "Create brief summary of the lesson, e.g Learners will apply the concept of stress and conduct stress tests by simulating real-life conditions in 3D with Computer Aided Design software."
            },
        },
         "required": [
            "summary"
        ]
      }
    }]

function_key_concept= [{
        "name": "create_key_concepts",
        "description": "Act as a teacher, continue create 'key concepts' section for given lesson plan. Do not add or remove any section from this function",
        "parameters": {
          "type": "object",
          "properties": {
            "key concepts": {
              "type": "array",
              "description": "Some key concepts that student will learn in this lesson, e.g. Virtual Reality, Simulation. Key concepts are the ideas and understandings that we hope will remain with our students long after they have left school. Key concepts sit above context but find their way into every context.",
              "items": {
                "type": "string"
              }
            },
        },
         "required": [
            "key concepts"
        ]
      }
    }]

function_prior_knowledge= [{
        "name": "create_prior_knowledge",
        "description": "Act as a teacher, continue create 'prior knowlegde' section for given lesson plan.",
        "parameters": {
          "type": "object",
          "properties": {
            "prior knowledge": {
              "type": "array",
              "description": "This section outlines the required background skills and understanding that learners should possess before engaging with the subject or course, e.g., possess fundamental computer skills, understand the concept of facial filters.",
              "items": {
                "type": "string"
              }
            },
        },
         "required": [
            "prior knowledge"
        ]
      }
    },]

function_objectives= [{
        "name": "create_lesson_objectives",
        "description": "Act as a teacher, continue create 'lesson objectives' section for given lesson plan.",
        "parameters": {
          "type": "object",
          "properties": {
            "objectives": {
              "type": "array",
              "description": "Learning objectives for the lesson. Lesson objectives are what the lesson aims to do (at different stages of the lesson).",
              "items": {
                "type": "string"
              }
            },
        },
         "required": [
            "objectives"
        ]
      }
    }]

function_outcomes= [{
        "name": "create_learning_outcomes",
        "description": "Act as a teacher, continue create 'learning outcomes' section for given lesson plan.",
        "parameters": {
          "type": "object",
          "properties": {
            "outcomes": {
              "type": "array",
              "description": "Learning outcomes for the lesson gained by the students (please also mind if the students in the class have profile with special needs), Learning outcomes should indicate what students should be able to do. Use bloom's taxonomy verbs (create, analyze, etc.), e.g. By the end of this lesson, learners will be able to: Explain the connection between climate change and its effects on the studied regions in Social Studies.",
              "items": {
                "type": "string"
              }
            },
        },
         "required": [
            "outcomes"
        ]
      }
    }]

function_application= [{
        "name": "create_real_world_application",
        "description": "Act as a teacher, continue create 'real world application' section for given lesson plan.",
        "parameters": {
          "type": "object",
          "properties": {
            "real world application": {
              "type": "string",
              "description": "Real world application of this lesson, e.g. Force and motion are fundamental physics concepts used in engineering"
            },
        },
         "required": [
            "real world application"
        ]
      }
    }]


function_overview= [{
        "name": "create_lesson_overview",
        "description": "Act as a teacher, create lesson overview for given lesson plan based on the lesson summary. These overviews only consisting of opening objectives, main objectives, and closing objectives. Object name should be exactly the same as this function",
        "parameters": {
          "type": "object",
          "properties": {
            "lesson overview": {
              "type": "object",
              "description": "Sequence of activities planned for the lesson. It should be consists of Opening Activity, Main Activity, and Closing Activity. These activities should consider the student profile.",
              "properties": {
                "opening overview": {
                  "type": "array",
                  "description": "A brief overview or summary of the opening session of the lesson presentation. It can be an introduction of the topic and software used.",
                  "items": {
                      "type": "string"
                  }
                },
                "opening objectives": {
                  "type": "array",
                  "description": "Objectives of the opening session of the lesson presentation. Introduction of the topic and software used.",
                  "items": {
                      "type": "string"
                  }
                },
                "main overview": {
                  "type": "array",
                  "description": "A brief overview or summary of the main session of the lesson presentation. You should be talk more detailed in about the topic and how to use the software used.",
                  "items": {
                      "type": "string"
                  }
                },
                "main objectives": {
                  "type": "array",
                  "description": "Objectives of the main session of the lesson presentation. Should be talk more detailed in about the topic and the software used.",
                  "items": {
                      "type": "string"
                  }
                },
                "closing overview": {
                  "type": "array",
                  "description": "A brief overview or summary of the closing session of the lesson presentation.",
                  "items": {
                      "type": "string"
                  }
                },
                "closing objectives": {
                  "type": "array",
                  "description": "Objectives of the closing session of the lesson presentation. Should be summary of the lesson, or lesson recap, and lessson reflection",
                  "items": {
                      "type": "string"
                  }
                }
              },
              "required": [
                "opening overview",
                "opening objectives",
                "main overview",
                "main objectives",
                "closing overview",
                "closing objectives"
              ]
            }
        },
         "required": [
            "lesson overview"
        ]
      }
    }]

function_preparation= [{
        "name": "create_pre_lesson_preparation",
        "description": "Act as a teacher, continue create 'pre-lesson preparation' section for given lesson plan. e.g. 'Laptop, Desktop or Chromebook (Recommended: 2 learners per laptop). 1. Install Autodesk® Fusion 360 (Education License) program. 2. Download the three files, stresstestsample.f3d, stresstestchallenge.f3d, and stresstestchallenge2.f3d to the learner’s computers. 3. Other things to note: ▪ For hardware requirements, please refer to the minimum hardware requirements from the software provider.'",
        "parameters": {
          "type": "object",
          "properties": {
            "pre-lesson preparation": {
              "type": "array",
              "description": "List of things that need to be prepared before the lesson starts (including to prepare for the student with needs in the student profile), e.g. Devices (tablets/laptops/Chromebooks/computers), A stable wifi connection",
              "items": {
                "type": "string"
              }
            },
        },
         "required": [
            "pre-lesson preparation"
        ]
      }
    }]

function_troubleshooting= [{
        "name": "create_lesson_troubleshooting",
        "description": "Act as a teacher, continue create 'troubleshooting' section for given lesson plan.",
        "parameters": {
          "type": "object",
          "properties": {
            "troubleshooting": {
              "type": "object",
              "description": "Troubleshooting section for handling issues during lesson learning. IMPORTANT: DO NOT LEAVE THIS SECTION EMPTY",
              "properties": {
                "issues": {
                  "type": "array",
                  "description": "List of issues that can be encountered during lesson learning. Should be description of the issue, e.g. CoSpaces website is not responding.",
                  "items": {
                    "type": "object",
                    "properties": {
                      "issue": {
                        "type": "string",
                        "description": "Description of the issue, e.g. CoSpaces website is not responding."
                      },
                      "possible_reasons": {
                        "type": "array",
                        "description": "Possible reasons for the issue, e.g. Issues with web connectivity or a server issue has occurred.",
                        "items": {
                          "type": "string"
                        }
                      },
                      "resolution": {
                        "type": "array",
                        "description": "Resolutions to solve the issue, e.g. Restart the CoSpaces web browser",
                        "items": {
                          "type": "string"
                        }
                      }
                    },
                    "required": ["issue", "possible_reasons", "resolution"]
                  }
                }
              },
              "required": ["issues"]
            },
        },
         "required": [
            "troubleshooting"
        ]
      }
    }]

function_assessment= [{
        "name": "create_assessment",
        "description": "Act as a teacher, continue create 'assessment' section for given lesson plan.",
        "parameters": {
          "type": "object",
          "properties": {
            "assessment": {
              "type": "object",
              "description": "Assessment section to be given to learners. IMPORTANT: DO NOT LEAVE THIS SECTION EMPTY. Please craft the assessment according to the student profile",
              "properties": {
                "assessment": {
                  "type": "array",
                  "description": "Assessment objectives for evaluating student understanding, e.g. Understanding of climate change.",
                  "items": {
                    "type": "object",
                    "properties": {
                      "assessment": {
                        "type": "string",
                        "description": "The assessment objective to be achieved by learners, e.g. Create a map to show spatial distribution and varying severity of extreme weather events."
                      },
                      "emerging": {
                        "type": "string",
                        "description": "'Emerging' criteria description that fulfiled the assessment objective (Make it into array list), e.g. Showed poor understanding of climate change and its causes and impacts."
                      },
                      "developing": {
                        "type": "array",
                        "description": "'Developing' criteria description that fulfiled the assessment objective (Make it into array list), e.g. Able to explain sufficiently about climate change and its causes and impacts.",
                        "items": {
                          "type": "string"
                        }
                      },
                      "proficient": {
                        "type": "array",
                        "description": "'Proficient' criteria description that fulfiled the assessment objective (Make it into array list), e.g. Able to explain climate change and its causes and impacts in detail.",
                        "items": {
                          "type": "string"
                        }
                      }
                    },
                    "required": ["emerging", "developing", "proficient"]
                  }
                }
              },
              "required": ["assessment"]
            }
        },
         "required": [
            "assessment"
        ]
      }
    }]

#@title <b>Latest Functions for Opening Activity<b> {display-mode: "form"}
opening_activity_description = '''
This is the opening session of a lesson learning. To assist the teacher, generate key points for each presentation slide for the opening activity. Focus on objectives, concepts, and relevant software. Consider the tech-infused aspect of the lesson.
WARNING: Start from Slide 4.
Follow this example, then adjust accordingly:
'Slide 4': 'Introduce fractions using a pizza example. Explain that fractions represent parts of a whole. Ask learners to imagine having a whole pizza (6 slices). If they ate two slices, what fraction did they eat? (A: ⅓) Use visuals to aid understanding.'
'Slide 5': 'Discuss how learners arrived at the correct fraction. Revise definitions of numerator and denominator.'
Remember that the format is 'Slide X': 'xxx'
'''

function_slide_overview = [{
    "name": "opening_overview_slide",
    "description": "Create key points for opening session presentation slides talking about the overview of the lesson. Each slide key point should be written in the desired format as a separate JSON object.",
    "parameters": {
        "type": "object",
        "properties": {
            "slide_overview": {
                "type": "array",
                "description": "In this slide 2 is the overview of lesson that will be learn by student, can be objectives, what we will learn today. Write in this format: 'Slide 2': 'xxx'. ONLY GENERATE SLIDE 2",
                "items": {"type": "string"}
            }
        },
        "required": ["slide_overview"],
    }
}]

function_trigger_activity = [{
    "name": "trigger_activity_slide",
    "description": "Create key points for opening session presentation slides talking about the trigger activity before starting the lesson. Each slide key point should be written in the desired format as a separate JSON object.",
    "parameters": {
        "type": "object",
        "properties": {
            "trigger_activity": {
                "type": "array",
                "description": "Write in this format: 'Slide 3': 'xxx'. Trigger activity serves to hook the students in. This could be a video related to the content covered, a provocative question to get students excited about the topic, etc. The trigger activity could possibly also hint at the technology that will be introduced later on - this often helps to excite students",
                "items": {"type": "string"}
            }
        },
        "required": ["trigger_activity"],
    }
}]

function_challenge = [{
    "name": "create_design_challenge",
    "description": "Act as a teacher, create design challenge that will be faced by student in this lesson.",
    "parameters": {
        "type": "object",
        "properties": {
            "challenge": {
                "type": "string",
                "description": "Design challenge is the project that the students need to complete in this lesson, e.g. Your task is to use <<software>> to build a <<end artefact>>. Your design challenge should be detailed on what student will do, not only the overview.",
            },
            "artifacts": {
                "type": "string",
                "description": "Design that students will produce at the end of the design challenge, start with word 'Design...'. WRITE ONLY ONE SENTENCE (WITH MAXIMUM 4 WORDS), e.g. 'Design a simple ML app that can distinguish between different type of fractions'."
            }
        },
        "required": ["challenge", "artifacts"],
    }
}]

function_requirements = [{
    "name": "create_design_challenge_requirements",
    "description": "Act as a teacher, think of what fundamental theories that needed for student to execute the design challenge",
    "parameters": {
        "type": "object",
        "properties": {
            "requirements": {
                "type": "array",
                "description": """Identify the fundamental theories that students should understand in order to execute the ‘Design Challenge’. These content topics should align with the student grade and subject. It could be some fundamental theory.
                Your answer SHOULD only the brief name of the theory, and formatted in the LIST of the content topics, e.g. ['mean', 'mode', 'median'].

                Example: If lesson is Math, data visualization using Tableau, the design challenge needs students to apply what they know about: ['mean', 'mode', 'median']""",
                "items": {"type": "string"}
            }
        },
        "required": ["requirements"],
    }
}]

function_opening = [{
    "name": "opening_activity_slide",
    "description": "Create key points for opening session presentation slides based on the given lesson overview. Each slide key point should be written in the desired format as a separate JSON object.",
    "parameters": {
        "type": "object",
        "properties": {
            "opening_activity": {
                "type": "array",
                "description": opening_activity_description,
                "items": {"type": "string"}
            }
        },
        "required": ["opening_activity"],
    }
}]




main_activity_description = '''
Generate presentation slides for the main activity. Focus on exploration of tutorial on using the software to achieve the lesson objectives.
No more talking about the key concepts of the topic, e.g. Understand Newton's First Law and its implications on inertia.
Include additional notes addressing potential special needs of students.

Example:
'main activity': ['Slide xx': 'Learn to navigate the Arduino IDE and write a simple program',
'Slide xx': 'Learn to navigate and use PhET Interactive Simulations for educational purposes.']

Remember, the writing format is: 'main activity': ['Slide xx': 'xxxx', 'Slide xx': 'xxxx', ...]
'''

function_main= [{
        "name": "main_activity_slide",
        "description": "Gives tutorial on how to use the software for this lesson, continue slide numbering from the previous opening session slides. Each slide should be written exactly like the desired format, where each slide is different json object. You will write a very long text, write completely.",
        "parameters": {
            "type": "object",
            "properties": {
                "main activity": {
                    "type": "array",
                    "description": "Make a detailed tutorial on how to use the software for this lesson to achieve the lesson objectives. Remember, the writing format is: 'main activity': ['Slide xx': 'xxxx', 'Slide xx': 'xxxx', ...]",
                    "items": {"type": "string"}
                }
            },
            "required": ["main activity"],
        }
      }]

closing_activity_description = '''
This is the closing session of a lesson learning. To assist the teacher, generate key points for one presentation slide for this closing activity. Provide a summary of key points covered in the lesson, encouraging reflection and discussion among learners.
Remember that the format is 'Slide X': 'xxx'

For example:
'closing activity': ['Slide xx':'Share a real-life example of solutions developed to manage pandemics.',
'Slide xx': 'Invite learners to test their model and complete page 2 on this worksheet in a group. Sample answers for two of the questions are given below:
Q. How would you improve the accuracy of your model even further?
Add more training data (more images). Use a more comprehensive data set (e.g., clearer images, blurry images, bright or dim lighting…)
Supervised learning - use models which allow for feedback to be given to improve the accuracy of the model'
'''

function_closing= [{
        "name": "closing_activity_slide",
        "description": "Create key points for one closing session presentation slide based on the given lesson overview.",
        "parameters": {
            "type": "object",
            "properties": {
                "closing activity": {
                    "type": "array",
                    "description": closing_activity_description,
                    "items": {"type": "string"}
                },
            },
            "required": ["closing activity"],
        }
      }]

def function_content_opening_gen(grade, subject):
  function_content_opening = [{
      "name": "create_slide_content",
      "description": f"You are an assistant for {subject} teacher for {grade} student, create the 'opening' presentation content and materials for given slide keypoints.",
      "parameters": {
          "type": "object",
          "properties": {
              "slideTitle": {
                  "type": "string",
                  "description": "Determine the appropriate title for the slide. Should be not more than 10 words. IMPORTANT: For slide 1, the slide title is exactly what given from keypoints. Your tone is presentation tone"
              },
              "slideContent": {
                  "type": "array",
                  "description": f'''
                  This content should be in manners of student-facing, therefore adjust your tone as you are presenting to a {grade} student. Act as you are guiding students through an exciting journey of learning and discovery. Your explanations should be clear, engaging, and tailored to {grade}-level understanding. You can put equations for student better understanding.
                  Write concisely, not too wordy. WARNING: DO NOT create more than 4 bullet points per slide.
                  [For slide 2, summarize the given lesson overview with teacher-tone; For slide 3, create a trigger activity to engage student for this lesson]
                  Example:
                  Introduction to Simulation and Modeling in Physics:
                  • Physicists use CAD (Computer Aided Design) to simulate the real world for their experiments.
                  • CAD began in the 1960s when there was a demand for accuracy and precision in product design.''',
                  "items": {
                      "type": "string"
                  }
              }
          },
          "required": [
              "slideTitle",
              "slideContent"
          ]
      }
  }]
  return function_content_opening

def function_content_main_gen(grade, subject, software):
  function_content_main = [{
      "name": "create_slide_content",
      "description": f"You are an assistant for {subject} teacher for {grade} student, create the 'main' presentation content and materials for given slide keypoints.",
      "parameters": {
          "type": "object",
          "properties": {
              "slideTitle": {
                  "type": "string",
                  "description": "Determine the appropriate title for the slide. Should be brief summary of the slide content. Should be not more than 10 words. Your tone is presentation tone"
              },
              "slideContent": {
                  "type": "array",
                  "description": f'''
                  This content should be in manners of student-facing, therefore adjust your tone as you are presenting to a {grade} student. Act as you are guiding students through an exciting journey of {software} tutorial. Gives a very well detailed tutorial.
                  IMPORTANT: INCLUDE EXAMPLE for each instructions. Write concisely, not too wordy. WARNING: DO NOT create more than 4 bullet points per slide. You can put equations for student better understanding. Not only KEYPOINTS, you need to give a brief EXPLANATION for each KEYPOINTS.
                  Example:
                  'Slide X':
                  '1. Open the chatbot software on your computer.
                  2. Click on 'Create New Project' to start a new project.
                  3. Name your project and choose a language for your chatbot (e.g., English, Spanish, etc.).
                  4. Select a template or start from scratch to design your chatbot's conversation flow.
                  5. Add training data to teach your chatbot how to respond to user inputs.
                  6. Test your chatbot by interacting with it and make adjustments as needed.''',
                  "items": {
                      "type": "string"
                  }
              }
          },
          "required": [
              "slideTitle",
              "slideContent"
          ]
      }
  }]
  return function_content_main

def function_content_closing_gen(subject, grade):
  function_content_closing = [{
      "name": "create_slide_content",
      "description": f"You are an assistant for {subject} teacher for {grade} student, create the 'closing' presentation content and materials for given slide keypoints.",
      "parameters": {
          "type": "object",
          "properties": {
              "slideTitle": {
                  "type": "string",
                  "description": "Determine the appropriate title for the slide. Should be brief summary of the slide content. Should be not more than 10 words. Your tone is presentation tone"
              },
              "slideContent": {
                  "type": "array",
                  "description": f'''This content should be in manners of student-facing, therefore adjust your tone as you are presenting to a {grade} student. Act as you are guiding students through an exciting journey of learning and discovery.
                  WARNING: DO NOT create more than 4 bullet points per slide. This 'closing' session is more like a wrap-up and reflection session about the lesson that has been taught.
                  Example:
                  'Slide X':
                  Q. How would you improve the accuracy of your model even further?
                  Add more training data (more images)
                  Use a more comprehensive data set (e.g., clearer images, blurry images, bright or dim lighting…)
                  Supervised learning - use models which allow for feedback to be given to improve the accuracy of the model''',
                  "items": {
                      "type": "string"
                  }
              }
          },
          "required": [
              "slideTitle",
              "slideContent"
          ]
      }
  }]
  return function_content_closing

function_finding_coding = [{
    "name": "find_code_worthy_slides",
    "description": "From given presentation slides, find which slides is worth to be given code example.",
    "parameters": {
        "type": "object",
        "properties": {
            "selected slide": {
              "type": "string",
              "description": "Choose the slides that needs code example for better understanding by student. Your respond should be in this format example: 'Slide 1', 'Slide 2', so on"
            },
        },
        "required": [
            "selected slide"
        ]
    }
}]

function_finding_non_coding = [{
    "name": "find_code_worthy_slides",
    "description": "From given presentation slides, find which slides is worth to be given use-case example.",
    "parameters": {
        "type": "object",
        "properties": {
            "selected slide": {
              "type": "string",
              "description": "Choose the slides that needs use-case example for better understanding by student. Your respond should be in this format example: 'Slide 1', 'Slide 2', so on"
            },
        },
        "required": [
            "selected slide"
        ]
    }
}]

