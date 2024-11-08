import os
import json
from openai import OpenAI
from app import app
from .model_function import software_list, function_summary, function_key_concept, function_prior_knowledge, function_objectives, function_outcomes, function_application, function_overview, function_preparation, function_troubleshooting, function_assessment, opening_activity_description, function_opening, main_activity_description, function_main, closing_activity_description, function_closing, function_content_gen

client = OpenAI(api_key=app.config['OPENAI_API_KEY'])

def generate_response(topic, subject, grade, student_profile, tech_domain):

    function_content = function_content_gen(grade)

    # Check if tech_domain and student_profile are both selected
    if tech_domain and student_profile:
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. Incorporate {tech_domain} tech domain. I have {student_profile} in my class. Create the lesson plan summary"
    elif tech_domain:
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. Incorporate {tech_domain} tech domain. Create the lesson plan summary"
    elif student_profile.strip() != "":
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. I have {student_profile} student in my class. Create the lesson plan summary"
    else:
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. Create the lesson plan summary"

    # For system prompt
    if student_profile:
        system_prompt = f"You are a {grade} teacher for student with {student_profile} special needs. Create a lesson plan based on user queries for your students into output JSON. Adjust your tone and notes according to your student grade."
    else:
        system_prompt = f"You are a {grade} teacher. Create a lesson plan based on user queries for your students into output JSON. Adjust your tone according to your student grade"

    client = OpenAI(timeout=30)

    # each completion will generate specific section of the lesson plan
    # completion request to generate the principal section of the lesson plan
    completion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_summary,
        function_call={'name': 'create_lesson_summary'},
        max_tokens=2000,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8,
        seed=10
    )

    output_content = completion.choices[0].message.function_call.arguments
    topic = json.loads(output_content).get('topic',{})
    summary = json.loads(output_content).get('summary',{})
    tech_domain = json.loads(output_content).get('tech domain',{})
    software = json.loads(output_content).get('software', {})

    # completion to generate the key concepts section of the lesson plan
    secondCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""You are a {grade} teacher, generate key concepts for lesson plan with following criteria:
                topic: {topic},
                grade: {grade},
                subject: {subject},
                student profile: {student_profile},
                tech domain: {tech_domain},
                software: {software}""",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_key_concept,
        max_tokens=500,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8,
    )
    output_content = secondCompletion.choices[0].message.function_call.arguments
    key_concepts = json.loads(output_content).get('key concepts',{})

    # completion to generate the prior knowledge section of the lesson plan
    thirdCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""You are a {grade} teacher, generate prior knowledge section for lesson plan with following criteria:
                topic: {topic},
                grade: {grade},
                subject: {subject},
                student profile: {student_profile},
                tech domain: {tech_domain},
                software: {software},
                key concepts: {key_concepts}""",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_prior_knowledge,
        function_call="auto",
        max_tokens=500,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = thirdCompletion.choices[0].message.function_call.arguments

    if 'prior knowledge' in json.loads(output_content):
        prior_knowledge = json.loads(output_content)['prior knowledge']
    elif 'priorKnowledge' in json.loads(output_content):
        prior_knowledge = json.loads(output_content)['priorKnowledge']
    elif 'prior_knowledge' in json.loads(output_content):
        prior_knowledge = json.loads(output_content)['prior_knowledge']

    if student_profile:
        objectives_prompt = f"You are a {grade} teacher for student with {student_profile} special needs, create 'lesson objectives' for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge}."
    else:
        objectives_prompt = f"You are a {grade} teacher, create 'lesson objectives' for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge}."

    # completion to generate the key objectives section of the lesson plan
    fourthCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": objectives_prompt,
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_objectives,
        max_tokens=800,
        temperature=0.8,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = fourthCompletion.choices[0].message.function_call.arguments
    objectives = json.loads(output_content).get('objectives',{})

    if student_profile:
        outcomes_prompt = f"You are a {grade} teacher for student with {student_profile} special needs, continue create comprehensive 'learning outcomes' section for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n lesson objectives: {objectives}. IMPORTANT: This section should be differs from 'lesson objectives' section"
    else:
        outcomes_prompt = f"You are a {grade} teacher, continue create comprehensive 'learning outcomes' section for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n lesson objectives: {objectives}. IMPORTANT: This section should be differs from 'lesson objectives' section"

    # completion to generate the outcomes section of the lesson plan
    fifthCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": outcomes_prompt,
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_outcomes,
        max_tokens=1000,
        temperature=0.8,
        presence_penalty=0.6,
        top_p=1
    )

    output_content = fifthCompletion.choices[0].message.function_call.arguments
    outcomes = json.loads(output_content).get('outcomes',{})

    # completion to generate the real world application section of the lesson plan
    sixthCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"You are a {grade} teacher, create 'real world applications' section related to the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes}",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_application,
        max_tokens=500,
        temperature=0.9,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = sixthCompletion.choices[0].message.function_call.arguments
    real_world_application = json.loads(output_content).get('real world application',{})

    if student_profile:
        overview_prompt = f"You are a {grade} teacher for student with {student_profile} special needs, create 'lesson overview' section for the following lesson plan criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software used: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes},\n real world application: {real_world_application}. IMPORTANT: Remember to use {software} in this learning session."
    else:
        overview_prompt = f"You are a {grade} teacher, create 'lesson overview' section for the following lesson plan criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software used: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes},\n real world application: {real_world_application}. IMPORTANT: Remember to use {software} in this learning session."

    # completion to generate the lesson overview section of the lesson plan
    seventhCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": overview_prompt,
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_overview,
        max_tokens=2000,
        temperature=0.4,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = seventhCompletion.choices[0].message.function_call.arguments
    lesson_overview = json.loads(output_content).get('lesson overview',{})

    # completion to generate the pre lesson preparation section of the lesson plan
    eightCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"You are a {grade} teacher, create 'pre-lesson preparation' section, e.g. about preparing the {software} that will be used during lesson and its supporting devices. Please considering these following student activities to do during the learning session: {lesson_overview}. ",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_preparation,
        max_tokens=1000,
        temperature=1,
        presence_penalty=0.6,
        top_p=1,
    )

    output_content = eightCompletion.choices[0].message.function_call.arguments
    pre_lesson_preparation = json.loads(output_content).get('pre-lesson preparation',{})

    # completion to generate the troubleshooting section of the lesson plan
    ninthCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
            messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"You are a {grade} teacher, continue create 'troubleshooting' section for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes},\n real world application: {real_world_application},\n lesson overview: {lesson_overview},\n pre-lesson preparation: {pre_lesson_preparation}",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_troubleshooting,
        max_tokens=2000,
        temperature=0.5,
        presence_penalty=0.6,
        top_p=0.8,
    )

    output_content = ninthCompletion.choices[0].message.function_call.arguments
    troubleshooting = json.loads(output_content).get('troubleshooting',{})

    # completion to generate the assessment rubric section of the lesson plan
    tenthCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"You are a {grade} teacher, continue create 'assessment' section (ALWAYS include the assessment itself, and the criterias: emerging, developing, and proficient) for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes},\n real world application: {real_world_application},\n lesson overview: {lesson_overview},\n pre-lesson preparation: {pre_lesson_preparation}",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_assessment,
        max_tokens=2000,
        temperature=0.8,
        presence_penalty=0.6,
        top_p=0.8,
    )

    output_content = tenthCompletion.choices[0].message.function_call.arguments
    assessment_rubric = json.loads(output_content).get('assessment',{})

    try:
        emerging_data = assessment_rubric[0]['emerging']
        assessment_rubric = assessment_rubric
    except KeyError:
        assessment_rubric = []
        for item in assessment_rubric:
            content = item.get('assessment', '')
            if isinstance(content, list) and len(content) > 1:
                assessment_rubric.extend(content)
            else:
                split_keywords = ['Emerging:', 'Developing:', 'Proficient:', 'emerging:', 'developing:', 'proficient:']
                split_content = [content]
                for keyword in split_keywords:
                    temp_split_content = []
                    for part in split_content:
                        temp_split_content.extend(part.split(keyword))
                    split_content = temp_split_content

                emerging = [split_content[i].strip() for i in range(1, len(split_content), 3)]
                developing = [split_content[i].strip() for i in range(2, len(split_content), 3)]
                proficient = [split_content[i].strip() for i in range(3, len(split_content), 3)]

                assessment_dict = {'assessment': split_content[0].strip(), 'emerging': emerging, 'developing': developing, 'proficient': proficient}
                assessment_rubric.append(assessment_dict)

    # generate the slide accordingly when the student profile is provided and when its not
    if student_profile:
        system_slide = f"You are a {grade} teacher for students with {student_profile} special needs. You want to explain how to use certain software in your class for the lesson objectives, now write your slide into output JSON  while each slide should be in different object. Adjust your tone and notes according to your student profile."
    else:
        system_slide = f"You are a {grade} teacher who wants to explain how to use certain software in your class for the lesson objectives, now write your slide into output JSON while each slide should be in different object. Adjust your tone and notes according to your student profile."

    # completion to generate the opening activity section of the lesson plan
    opening_activity_complete = {'opening_activity': {'Slide 1': f"{topic}", 'Slide 2': 'Ground Rules: 1. Be respectful of one another; 2. Raise your hand if you have anything to share; 3. Listen attentively and follow instructions; 4. Complete tasks in given time', 'Slide 3': 'Team Roles: 1. Project Manager: Help your team members to stick to their tasks! Monitor what they are doing; 2. Resource Manager: Collect materials and tools from the teacher. Ensure team members are using them properly. Return when you are done!; Time Keeper: Keep track of time! Check the timer every few mins. Help team members to complete.'}}

    openingCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_slide
            },
            {
                "role": "user",
                "content": f"Generate keynotes for opening session presentation slides based on these objectives: {lesson_overview.get('opening objectives',{})};  Always starts from 'Slide 4'; This lesson topic is: {topic}, and using {software}. For more context, you can see this opening activity overview: {lesson_overview.get('opening overview',{})};",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_opening,
        max_tokens=4096,
        temperature=1,
        presence_penalty=0.6,
        top_p=0.8,
        seed=215000
    )

    output_content = openingCompletion.choices[0].message.function_call.arguments
    opening_activity_slides = {}
    last_slide_opening=""

    if 'opening_activity' in json.loads(output_content) or 'opening activity' in json.loads(output_content):
        opening_activity_data = json.loads(output_content).get('opening_activity') or json.loads(output_content).get('opening activity')
        opening_activity_slides = {}

        if isinstance(opening_activity_data, list):
            if len(opening_activity_data) == 1:
                slides = opening_activity_data[0]
                slide_parts = []

                if '. Slide' in slides:
                    slide_parts = slides.split('. ')
                elif '\nSlide ' in slides:
                    slide_parts = slides.split('\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]
                elif '\n\nSlide ' in slides:
                    slide_parts = slides.split('\n\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]
                elif '\\nSlide ' in slides:
                    slide_parts = slides.split('\\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]

                for part in slide_parts:
                    if part.strip():
                        slide_info = part.split(': ', 1)
                        if len(slide_info) == 2:
                            slide_number, slide_content = slide_info
                            slide_number = slide_number.strip()
                            if slide_number[0].isdigit():
                                slide_number = f"Slide {slide_number}"
                            slide_content = slide_content.strip()
                            opening_activity_slides[slide_number] = slide_content
                            last_slide_opening=slide_number

            else:
                for item in opening_activity_data:
                    slide_number, slide_content = item.split(': ', 1)
                    slide_number = slide_number.strip()
                    if slide_number[0].isdigit():
                        slide_number = f"Slide {slide_number}"
                    slide_content = slide_content.strip()
                    opening_activity_slides[slide_number] = slide_content
                    last_slide_opening=slide_number
        else:
            raise ValueError("Invalid format for opening_activity data")

    if last_slide_opening:
        last_slide_number = int(last_slide_opening.split()[1])
        next_slide_number = last_slide_number + 1
        next_slide = f"Slide {next_slide_number}"

    opening_activity = {'opening_activity': opening_activity_slides}
    opening_activity_complete['opening_activity'].update(opening_activity['opening_activity'])

    #next_slide = ""

    # completion to generate the main activity section of the lesson plan
    mainCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_slide
            },
            {
                "role": "user",
                "content": f"This is the main activity for learners in class to learn how to use the {software} for this lesson topic {topic} in {subject} subject. Generate keynotes for main session presentation slides based on these objectives: {lesson_overview.get('main objectives',{})}. Start slide from {next_slide}. Provide a comprehensive tutorial on using the {software} to achieve the lesson objectives.",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_main,
        max_tokens=4096,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = mainCompletion.choices[0].message.function_call.arguments
    main_activity_slides = {}
    last_slide_main = ""

    if 'main_activity' in json.loads(output_content) or 'main activity' in json.loads(output_content):
        main_activity_data = json.loads(output_content).get('main_activity') or json.loads(output_content).get('main activity')
        main_activity_slides = {}

        if isinstance(main_activity_data, list):
            if len(main_activity_data) == 1:
                slides = main_activity_data[0]
                slide_parts = []

                if '. Slide' in slides:
                    slide_parts = slides.split('. ')
                elif '\nSlide ' in slides:
                    slide_parts = slides.split('\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]
                elif '\n\nSlide ' in slides:
                    slide_parts = slides.split('\n\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]
                elif '\\nSlide ' in slides:
                    slide_parts = slides.split('\\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]

                for part in slide_parts:
                    if part.strip():
                        slide_info = part.split(': ', 1)
                        if len(slide_info) == 2:
                            slide_number, slide_content = slide_info
                            slide_number = slide_number.strip()
                            if slide_number[0].isdigit():
                                slide_number = f"Slide {slide_number}"
                            slide_content = slide_content.strip()
                            main_activity_slides[slide_number] = slide_content
                            last_slide_main = slide_number
            else:
                for item in main_activity_data:
                    slide_number, slide_content = item.split(': ', 1)
                    slide_number = slide_number.strip()
                    if slide_number[0].isdigit():
                        slide_number = f"Slide {slide_number}"
                    slide_content = slide_content.strip()
                    main_activity_slides[slide_number] = slide_content
                    last_slide_main = slide_number
        else:
            raise ValueError("Invalid format for main_activity data")

    if last_slide_main:
        last_slide_number = int(last_slide_main.split()[1])
        next_slide_number = last_slide_number + 1
        next_slide = f"Slide {next_slide_number}"

    main_activity = {'main_activity': main_activity_slides}

    # completion to generate the closing activity section of the lesson plan
    closingCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_slide
            },
            {
                "role": "user",
                "content": f"This the the closing session of your lesson about {topic} using {software}, this session should be wrap up from what student have learnt from previous session. Generate keynotes for closing session presentation slides based on these objectives: {lesson_overview.get('closing objectives',{})}; Start the slide from {next_slide}; For more context, you can see this opening activity overview: {lesson_overview.get('closing overview',{})}; Another context, here are previous session slide keynotes: {opening_activity}; {main_activity}"
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_closing,
        max_tokens=4096,
        temperature=0.6,
        presence_penalty=0.8,
        top_p=0.8
    )

    output_content = closingCompletion.choices[0].message.function_call.arguments
    closing_activity_slides = {}

    if 'closing_activity' in json.loads(output_content) or 'closing activity' in json.loads(output_content):
        closing_activity_data = json.loads(output_content).get('closing_activity') or json.loads(output_content).get('closing activity')
        closing_activity_slides = {}

        if isinstance(closing_activity_data, list):
            if len(closing_activity_data) == 1:
                slides = closing_activity_data[0]
                slide_parts = []

                if '. Slide' in slides:
                    slide_parts = slides.split('. ')
                elif '\nSlide ' in slides:
                    slide_parts = slides.split('\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]
                elif '\n\nSlide ' in slides:
                    slide_parts = slides.split('\n\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]
                elif '\\nSlide ' in slides:
                    slide_parts = slides.split('\\nSlide ')
                    if slide_parts[0] == '':
                        slide_parts = slide_parts[1:]

                for part in slide_parts:
                    if part.strip():
                        slide_info = part.split(': ', 1)
                        if len(slide_info) == 2:
                            slide_number, slide_content = slide_info
                            slide_number = slide_number.strip()
                            if slide_number[0].isdigit():
                                slide_number = f"Slide {slide_number}"
                            slide_content = slide_content.strip()
                            closing_activity_slides[slide_number] = slide_content
            else:
                for item in closing_activity_data:
                    slide_number, slide_content = item.split(': ', 1)
                    slide_number = slide_number.strip()
                    if slide_number[0].isdigit():
                        slide_number = f"Slide {slide_number}"
                    slide_content = slide_content.strip()
                    closing_activity_slides[slide_number] = slide_content
        else:
            raise ValueError("Invalid format for closing_activity data")

    closing_activity = {'closing_activity': closing_activity_slides}

    activities = {
        'opening_activity': opening_activity_complete,
        'main_activity': main_activity,
        'closing_activity': closing_activity
    }

    output_data = {}

    for activity_key, activity_data in activities.items():
        activity_slides = activity_data.get(activity_key, {})
        activity_output = {}
        for slide_number, slide_content in activity_slides.items():
            activity_overview = lesson_overview.get(f"{activity_key} overview", [])
            activity_objectives = lesson_overview.get(f"{activity_key} objectives", [])

            contentCompletion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system",
                        "content": system_slide
                    },
                    {
                        "role": "user",
                        "content": f"You are a {grade} teacher, teaching about {topic} for {subject} subject. Generate {slide_number} content for this given keypoints: {slide_content}. Should fulfil these slide overview: {activity_overview}, and these slide objectives: {activity_objectives}; Remember that 'Slide 1' is only the title of the presentation."
                    },
                ],
                response_format={ "type": "json_object" },
                functions=function_content,
                max_tokens=1000,
                temperature=0.8,
                presence_penalty=0.8,
                top_p=0.8,
                seed=990000
            )

            output_content = contentCompletion.choices[0].message.function_call.arguments
            slide_output = json.loads(output_content)
            activity_output[slide_number] = slide_output

        output_data[activity_key] = activity_output

    # store the main body and the slides of the lesson plan into a dictionary
    model_response_dict = {
        "test_volume_mounting" : "test run 87",
        "core": json.loads(completion.choices[0].message.function_call.arguments),
        "key_concepts": key_concepts,
        "prior_knowledge" : prior_knowledge,
        "objectives" : objectives,
        "outcomes" : outcomes,
        "real_world_application" : real_world_application,
        "lesson_overview" : lesson_overview,
        "pre_lesson_preparation" : pre_lesson_preparation,
        "troubleshooting" : troubleshooting,
        "assessment" : assessment_rubric,
        "detailed_slides" : output_data,
        "debug":activities
    }

    # return the dictionary that contains all the section of the lesson plan
    return model_response_dict
