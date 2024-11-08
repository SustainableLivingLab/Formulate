import json
import csv
import pandas as pd
from openai import OpenAI, OpenAIError
from app import app
import os
import time
import requests
import base64
from PIL import Image
from io import BytesIO
import random
from tqdm import tqdm
from .model_function import function_intro, function_tech_domain, function_software, function_other_subject, function_other_software, function_summary, function_key_concept, function_prior_knowledge, function_objectives, function_outcomes, function_application, function_overview, function_preparation, function_troubleshooting, function_assessment, opening_activity_description, function_opening, main_activity_description, function_main, closing_activity_description, function_closing, function_content_opening_gen, function_content_main_gen, function_content_closing_gen, function_finding_coding, function_finding_non_coding, function_challenge, function_requirements

client = OpenAI(api_key=app.config['OPENAI_API_KEY'])

freepik_api_key=app.config['FREEPIK_API_KEY']

def generate_intro(topic, subject, grade, student_profile, tech_domain, software, gen_tech_domain, recommendations, LP, domain_list):
    def read_data_from_csv(file_path):
        data = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row["software recommendation"] = row["software recommendation"].split(", ")
                data.append(row)
        return data
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "app_data_eddy - postpro.csv")
    grade_file_path = os.path.join(script_dir, "app_data_eddy - byGrade.csv")
    subject_file_path = os.path.join(script_dir, "app_data_eddy - bySubject.csv")
    tech_domain_file_path = os.path.join(script_dir, "app_data_eddy - byTech.csv")
    grade_df = pd.read_csv(grade_file_path)
    subject_df = pd.read_csv(subject_file_path)
    tech_domain_df = pd.read_csv(tech_domain_file_path)
    data = read_data_from_csv(file_path)

    def get_recommendations(data, grade, subject_to_search, tech_domain):
        recommendations = []
        for entry in data:
            if entry["grade"] == grade and entry["subject"] == subject_to_search and entry["tech domain"] == tech_domain:
                recommendations.extend(entry["software recommendation"])
        return recommendations

    def filter_software_other_subject(tech_domain, grade, subject):
        filtered_software = tech_domain_df[tech_domain_df['tech_domain'] == tech_domain]['software']
        subject_software = subject_df[subject_df['subject'] == subject]['software'].tolist()
        agnostic_software = subject_df[subject_df['subject'] == 'Subject Agnostic']['software'].tolist()
        subject_software.extend(agnostic_software)
        filtered_software = filtered_software[filtered_software.isin(subject_software)]
        filtered_software = filtered_software[filtered_software.isin(grade_df[grade_df['grade'] == grade]['software'])]

        return filtered_software.tolist()

    def filter_software_design_simulation(data, grade, subject):
        recommendations = []
        tech_domains = ["Design & Simulation (2D Design)", "Design & Simulation (3D Design)"]
        for entry in data:
            if entry["grade"] == grade and entry["subject"] == subject and entry["tech domain"] in tech_domains:
                recommendations.extend(entry["software recommendation"])
        return recommendations

    def determine_tech_domain(subject, grade, topic, domain_list):
        function_tech_domain = [
            {
                "name": "select_tech_domain",
                "description": "Act as a teacher, you need to determine appropriate tech domain for your lesson plan",
                "parameters": {
                "type": "object",
                "properties": {
                    "tech domain": {
                    "type": "string",
                    "description": f"Select appropriate tech domain for the given topic and grade. SHOULD be one from this list (DO NOT choose outside of given list): {domain_list}"
                    },
                },
                "required": [
                    "tech domain"
                ]
            }
            }]

        domainCompletion = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
            messages=[
                {
                    "role": "system",
                    "content": f"Act as a {subject} teacher for {grade} teaching about {topic}. You need to determine appropriate tech domain for your lesson plan. Your answer should be in JSON"
                },
                {
                    "role": "user",
                    "content": f"You are a {subject} teacher for {grade} student. You are teaching about {topic}. Determine what tech domain appropriate for this topic. CHOOSE ONE TECH DOMAIN FROM THIS LIST: {domain_list}",
                },
            ],
            response_format={ "type": "json_object" },
            functions=function_tech_domain,
            max_tokens=800,
            temperature=0.2,
            presence_penalty=0.6,
            top_p=0.8
        )

        output_domain = domainCompletion.choices[0].message.function_call.arguments
        tech_domain = json.loads(output_domain).get('tech domain', {})
        return tech_domain

    def determine_software(subject, grade, topic, gen_tech_domain, recommendations):
        softwareCompletion = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
            messages=[
                {
                    "role": "system",
                    "content": f"Act as a {subject} teacher for {grade} teaching about {topic}. Choose one softwware from the list. Your answer should be in JSON"
                },
                {
                    "role": "user",
                    "content": f"You are a {subject} teacher for {grade} student. You are teaching about {topic}, this lesson focusing on {gen_tech_domain}. These are available softwares to be used in this lesson: {recommendations}. CHOOSE ONE most relevant software to be used in this lesson, based on its relevance to the given tech domain, topic, subject, and grade.",
                },
            ],
            response_format={ "type": "json_object" },
            functions=function_software,
            max_tokens=800,
            temperature=0.6,
            presence_penalty=0.6,
            top_p=0.8
            )

        output_software = softwareCompletion.choices[0].message.function_call.arguments
        software = json.loads(output_software).get('software', {})
        return software

    if subject == 'ELA':
        subject = 'English'

    user_grade = grade

    if user_grade in ["1st Grade", "2nd Grade", "3rd Grade"]:
        grade = "Lower Elementary"
    elif user_grade in ["4th Grade", "5th Grade", "6th Grade"]:
        grade =  "Upper Elementary"
    elif user_grade in ["7th Grade", "8th Grade", "9th Grade"]:
        grade = "Middle School"

    # --------------------------------------------------------------
    # Determine Other Subject
    # --------------------------------------------------------------

    if subject == 'Other':
        subjectCompletion = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
            messages=[
                {
                    "role": "system",
                    "content": f"Act as a teacher for {grade} teaching about {topic}. Your answer should be in JSON"
                },
                {
                    "role": "user",
                    "content": f"You are a {grade} teacher. You are teaching about {topic}. Determine what subject name appropriate for this topic, e.g Art/Technology, Music, Physical Education, etc.",
                },
            ],
            response_format={ "type": "json_object" },
            functions=function_other_subject,
            max_tokens=1000,
            temperature=0.6,
            presence_penalty=0.6,
            top_p=0.8
        )

        output_subject = subjectCompletion.choices[0].message.function_call.arguments
        subject = json.loads(output_subject).get('subject', {})


    # --------------------------------------------------------------
    # Determine Tech Domain
    # --------------------------------------------------------------

    if not tech_domain:
        if LP == 1:
            domain_list = ['App Development', 'Artificial Intelligence', 'Design & Simulation', 'Extended Reality (AR/VR/MR)', 'Multimedia and Animation', 'Programming & Coding']
    else:
        if LP == 1:
            domain_list = ['App Development', 'Artificial Intelligence', 'Design & Simulation', 'Extended Reality (AR/VR/MR)', 'Multimedia and Animation', 'Programming & Coding']


    if LP == 1:
        if not tech_domain:
            #domain_list = ['App Development', 'Artificial Intelligence', 'Design & Simulation', 'Extended Reality (AR/VR/MR)', 'Multimedia and Animation', 'Programming & Coding']
            gen_tech_domain = determine_tech_domain(subject, grade, topic, domain_list)
            domain_list = [domain for domain in domain_list if domain != gen_tech_domain]
        else:
            gen_tech_domain = tech_domain
    elif LP in [2, 3]:
        if not tech_domain:
            domain_list = [domain for domain in domain_list if domain != gen_tech_domain]
            gen_tech_domain = determine_tech_domain(subject, grade, topic, domain_list)
        else:
            gen_tech_domain = tech_domain

    print(f"gen_tech_domain: {gen_tech_domain}")
    # --------------------------------------------------------------
    # Determine Software Recommendations
    # --------------------------------------------------------------

    if LP == 1: # Software based on database
        if not software:
            if subject not in ['English', 'Science', 'Math', 'Social Studies']:
                subject_to_search = 'Other'
                if gen_tech_domain == 'Design & Simulation':
                    recommendations = filter_software_design_simulation(data, grade, subject_to_search)
                else:
                    recommendations = get_recommendations(data, grade, subject_to_search, gen_tech_domain)
            else:
                if gen_tech_domain == 'Design & Simulation':
                    recommendations = filter_software_design_simulation(data, grade, subject)
                else:
                    recommendations = get_recommendations(data, grade, subject, gen_tech_domain)

            print(f"Software recommendations LP{LP}:")
            for recommendation in recommendations:
                print("-", recommendation)

            if len(recommendations) > 1 or len(software) > 1:
                software = determine_software(subject, grade, topic, gen_tech_domain, recommendations)
                recommendations = [recommendation for recommendation in recommendations if recommendation not in software]
            else:
                software = recommendations
                recommendations = [recommendation for recommendation in recommendations if recommendation not in software]

    elif LP == 2: # Software based on database or GPT recommendation
        if not tech_domain:
            if subject not in ['English', 'Science', 'Math', 'Social Studies']:
                subject_to_search = 'Other'
                if gen_tech_domain == 'Design & Simulation':
                    recommendations = filter_software_design_simulation(data, grade, subject_to_search)
                else:
                    recommendations = get_recommendations(data, grade, subject_to_search, gen_tech_domain)
            else:
                if gen_tech_domain == 'Design & Simulation':
                    recommendations = filter_software_design_simulation(data, grade, subject)
                else:
                    recommendations = get_recommendations(data, grade, subject, gen_tech_domain)

            print(f"Software recommendations LP{LP} with tech domain:")
            for recommendation in recommendations:
                print("-", recommendation)

            if len(recommendations) > 1 or len(software) > 1:
                software = determine_software(subject, grade, topic, gen_tech_domain, recommendations)
                recommendations = [recommendation for recommendation in recommendations if recommendation not in software]
            else:
                software = recommendations
                recommendations = [recommendation for recommendation in recommendations if recommendation not in software]

        else:
            if len(recommendations) == 1:
                software = recommendations
            elif len(recommendations) > 1:
                software = determine_software(subject, grade, topic, gen_tech_domain, recommendations)
                print(f"Software recommendations LP{LP}:")
                for recommendation in recommendations:
                    print("-", recommendation)
                recommendations = [recommendation for recommendation in recommendations if recommendation not in software]
            else:
                recommenderCompletion = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a professional software specialist. You know what a perfect software used by {grade} student for {subject} lesson in topic of {topic}. Your answer should be in JSON"
                        },
                        {
                            "role": "user",
                            "content": f"I am a {grade} teacher, what software(s) suitable for a lesson about {topic} in {subject} class for {grade} student, this lesson categorize as {gen_tech_domain}. Please mind that my student is only {grade}, choose a relevant software to be used by this grade",
                        },
                    ],
                    response_format={ "type": "json_object" },
                    functions=function_other_software,
                    max_tokens=800,
                    temperature=0.4,
                    presence_penalty=0.6,
                    top_p=0.8
                )

                output_recsof = json.loads(recommenderCompletion.choices[0].message.function_call.arguments)
                if isinstance(output_recsof["software"], list):
                    recommendations.extend(output_recsof["software"])
                else:
                    recommendations.append(output_recsof["software"])

                print(f"AI-generated software recommendations LP{LP}:")
                for recommendation in recommendations:
                    print("-", recommendation)

                if len(recommendations) > 1:
                    software = determine_software(subject, grade, topic, gen_tech_domain, recommendations)
                    recommendations = [recommendation for recommendation in recommendations if recommendation not in software]
                else:
                    software = recommendations
                    recommendations = [recommendation for recommendation in recommendations if recommendation not in software]

    elif LP == 3: # Software based on database or GPT recommendation
        thirdRecommendations = []
        recommenderCompletion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional software specialist. You know what a perfect software used by {grade} student for {subject} lesson in topic of {topic}. Your answer should be in JSON"
                },
                {
                    "role": "user",
                    "content": f"I am a {grade} teacher, what software(s) suitable for a lesson about {topic} in {subject} class for {grade} student, this lesson categorize as {gen_tech_domain}. Please mind that my student is only {grade}, choose a relevant software to be used by this grade",
                },
            ],
            response_format={ "type": "json_object" },
            functions=function_other_software,
            max_tokens=800,
            temperature=0.4,
            presence_penalty=0.6,
            top_p=0.8
        )

        output_recsof = json.loads(recommenderCompletion.choices[0].message.function_call.arguments)
        if isinstance(output_recsof["software"], list):
            thirdRecommendations.extend(output_recsof["software"])
        else:
            thirdRecommendations.append(output_recsof["software"])

        thirdRecommendations = [recommendation for recommendation in thirdRecommendations if recommendation not in recommendations]
        print(f"AI-generated software recommendations LP{LP}:")
        for recommendation in thirdRecommendations:
            print("-", recommendation)

        if len(thirdRecommendations) > 1:
            software = determine_software(subject, grade, topic, gen_tech_domain, thirdRecommendations)
        else:
            software = thirdRecommendations

    if not tech_domain:
        recommendations = []

    if not isinstance(software, list):
        software = [software]

    # For user prompt
    if tech_domain and student_profile:
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. Incorporate {tech_domain} tech domain. I have {student_profile} in my class. In this lesson, you are using {software}. Create an engaging and exciting lesson title. You can be creative with the title"
    elif tech_domain:
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. Incorporate {tech_domain} tech domain. In this lesson, you are using {software}. Create an engaging and exciting lesson title. You can be creative with the title"
    elif student_profile.strip() != "":
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. I have {student_profile} student in my class. In this lesson, you are using {software}. Create an engaging and exciting lesson title. You can be creative with the title"
    else:
        user_prompt = f"Act as a {grade} teacher, I would like to teach a lesson on {topic} for {grade} school grade {subject} subject. In this lesson, you are using {software}. Create an engaging and exciting lesson title. You can be creative with the title"

    # For system prompt
    if student_profile:
        system_prompt = f"You are a friendly {subject} teacher for {grade} student with {student_profile} special needs. Create a lesson plan based on user queries for your students into output JSON. Adjust your tone and notes according to your student grade."
    else:
        system_prompt = f"You are a friendly {subject} teacher for {grade} student. Create a lesson plan based on user queries for your students into output JSON. Adjust your tone according to your student grade"


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
        functions=function_intro,
        max_tokens=2000,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    if subject == 'English':
        subject = 'ELA'

    grade = user_grade

    output_content = completion.choices[0].message.function_call.arguments
    topic = json.loads(output_content).get('topic',{})
    title = json.loads(output_content).get('title', {})
    output_content_json = json.loads(output_content)
    output_content_json['subject'] = subject
    output_content_json['grade'] = user_grade
    output_content_json['tech domain'] = gen_tech_domain
    output_content_json['software'] = software
    if not software:
        recommendations = [recommendation for recommendation in recommendations if recommendation not in software]
    else:
        recommendations = []

    return topic, software, gen_tech_domain, system_prompt, subject, title, recommendations, gen_tech_domain, LP, domain_list

def generate_key_concepts(topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, title):
    # completion to generate the key concepts section of the lesson plan
    secondCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": f"Act as you are guiding students through an exciting journey of learning and discovery. Your explanations should be clear, engaging, and tailored to {grade}-level understanding. Write in JSON"
            },
            {
                "role": "user",
                "content": f"""Please act as you are a {subject} teacher for {grade} student, now you are teaching about {title}.
                Now generate key concepts that need to be teach to your {grade} students. You should NOT talk about the software first, this key concept is the THEORY for {grade} student to learn about {title}""",
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
    return key_concepts

def generate_prior_knowledge(topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts):
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
                "content": f"""You are a {grade} teacher, teaching {subject}, generate prior knowledge section for lesson plan with following criteria:
                topic: {topic},
                student profile: {student_profile},
                tech domain: {gen_tech_domain},
                software: {software},
                key concepts: {key_concepts}""",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_prior_knowledge,
        max_tokens=500,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8,
    )

    output_content = thirdCompletion.choices[0].message.function_call.arguments

    if 'prior knowledge' in json.loads(output_content):
        prior_knowledge = json.loads(output_content)['prior knowledge']
    elif 'priorKnowledge' in json.loads(output_content):
        prior_knowledge = json.loads(output_content)['priorKnowledge']
    elif 'prior_knowledge' in json.loads(output_content):
        prior_knowledge = json.loads(output_content)['prior_knowledge']

    return prior_knowledge

def generate_objectives(topic, subject, grade, student_profile, tech_domain, software, system_prompt, key_concepts, prior_knowledge):
    if student_profile:
        objectives_prompt = f"You are a {subject} teacher for {grade} student with {student_profile} special needs, create 'lesson objectives' section for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge}."
    else:
        objectives_prompt = f"You are a {subject} teacher for {grade} student, create 'lesson objectives' section for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge}."


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
        function_call={'name': 'create_lesson_objectives'},
        max_tokens=500,
        temperature=0.9,
        presence_penalty=0.6,
        top_p=0.8,
        #seed=4100
    )

    output_content = fourthCompletion.choices[0].message.function_call.arguments
    objectives = json.loads(output_content).get('objectives',{})
    split_objectives = []

    for objective in objectives:
        sentences = objective.split('. ')

        for sentence in sentences:
            parts = sentence.split('\n')
            split_objectives.extend(parts)

    split_objectives = [objective.strip() for objective in split_objectives if objective.strip()]
    objectives = split_objectives
    return objectives

def generate_outcomes(topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives):
    if student_profile:
        outcomes_prompt = f"You are a {subject} teacher for {grade} student with {student_profile} special needs, continue create comprehensive 'learning outcomes' section for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n lesson objectives: {objectives}. IMPORTANT: This section should be differs from 'lesson objectives' section"
    else:
        outcomes_prompt = f"You are a {subject} teacher for {grade} student, continue create comprehensive 'learning outcomes' section for the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n lesson objectives: {objectives}. IMPORTANT: This section should be differs from 'lesson objectives' section"

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
        top_p=1,
        #seed=5000
    )

    output_content = fifthCompletion.choices[0].message.function_call.arguments
    outcomes = json.loads(output_content).get('outcomes',{})
    if len(outcomes) < 2:
        new_outcomes = []
        for outcome in outcomes:
            new_outcomes.extend(outcome.split('\n'))
        outcomes = new_outcomes
    return outcomes

def generate_real_world_application(topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives, outcomes):
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
                "content": f"You are a {subject} teacher for {grade} student, create 'real world applications' section related to the lesson plan with following criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes}",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_application,
        #function_call={'name': 'create_real_world_application'},
        max_tokens=500,
        temperature=0.9,
        presence_penalty=0.6,
        top_p=0.8,
        #seed=6000
    )

    output_content = sixthCompletion.choices[0].message.function_call.arguments
    real_world_application = json.loads(output_content).get('real world application',{})
    return real_world_application

def generate_lesson_overview(topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives, outcomes, real_world_application):
    if student_profile:
        overview_prompt = f"You are a {subject} teacher for {grade} student with {student_profile} special needs, create 'lesson overview' for the following lesson plan criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software used: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes},\n real world application: {real_world_application}. IMPORTANT: Remember to use {software} in this learning session. "
    else:
        overview_prompt = f"You are a {subject} teacher for {grade} student, create 'lesson overview' for the following lesson plan criteria:\n topic: {topic},\n grade: {grade},\n subject: {subject},\n student profile: {student_profile},\n software used: {software},\n key concepts: {key_concepts},\n prior knowledge: {prior_knowledge},\n objectives: {objectives},\n outcomes: {outcomes},\n real world application: {real_world_application}. IMPORTANT: Remember to use {software} in this learning session."

    while True:
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
            response_format={"type": "json_object"},
            functions=function_overview,
            max_tokens=2000,
            temperature=0.4,
            presence_penalty=0.6,
            top_p=1
        )

        output_content = seventhCompletion.choices[0].message.function_call.arguments
        lesson_overview = json.loads(output_content).get('lesson overview',{})

        # Check if all six required outputs are present
        if all(key in lesson_overview for key in ['opening overview', 'opening objectives', 'main overview', 'main objectives', 'closing overview', 'closing objectives']):
            break
        else:
          print('Retrying...')

    lesson_overview_modified = {}

    for key, value in lesson_overview.items():
        modified_value = [item.strip() for sublist in value for item in sublist.split('\n')]
        lesson_overview_modified[key] = modified_value

    lesson_overview = lesson_overview_modified

    return lesson_overview

def generate_lesson_summary(subject, grade, system_prompt, lesson_overview, title):
    summaryCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"You are a {subject} teacher for {grade} student teaching about {title}. Create a MAXIMUM 2 SENTENCES lesson summary based on this lesson overview: {lesson_overview}; Important notes: The first sentence should summarize the content topics and objectives. The second sentence should mention the tech tool used, and what they will do with it.",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_summary,
        max_tokens=2000,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8,
    )

    output_content = summaryCompletion.choices[0].message.function_call.arguments
    summary = json.loads(output_content).get('summary',{})
    return summary

def generate_pre_lesson_preparation(topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, lesson_overview):
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
                "content": f"You are a {subject} teacher for {grade} student, create a DETAILED 'pre-lesson preparation' section, e.g. about preparing the {software} that will be used during lesson and its supporting devices. These are what students are going to do during the learning session: {lesson_overview}. ",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_preparation,
        max_tokens=1000,
        temperature=0.8,
        presence_penalty=0.6,
        top_p=1,
        #seed=78000
    )

    output_content = eightCompletion.choices[0].message.function_call.arguments
    pre_lesson_preparation = json.loads(output_content).get('pre-lesson preparation',{})

    if len(pre_lesson_preparation) < 2:
        split_preparation = []

        for preparation in pre_lesson_preparation:
            sentences = preparation.split('. ')

            for sentence in sentences:
                if sentence.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ', '10. ')):
                    split_preparation.append(sentence)
                else:
                    parts = sentence.split('\n')
                    split_preparation.extend(parts)
                
    split_preparation = [preparation.strip() for preparation in split_preparation if preparation.strip()]
    pre_lesson_preparation = split_preparation

    def correct_preparation_list(pre_lesson_preparation):
        corrected_list = []
        i = 0
        while i < len(pre_lesson_preparation):
            # Check if the string starts with a number
            if pre_lesson_preparation[i].strip().isdigit():
                # Merge the string with the next one
                merged_string = pre_lesson_preparation[i].strip() + ". " + pre_lesson_preparation[i + 1].strip()
                corrected_list.append(merged_string)
                # Skip the next string since it's already merged
                i += 1
            else:
                corrected_list.append(pre_lesson_preparation[i])
            i += 1
        return corrected_list

    pre_lesson_preparation = correct_preparation_list(pre_lesson_preparation)

    return pre_lesson_preparation

def generate_troubleshooting(topic, subject, grade, software, system_prompt, lesson_overview, title):
    # completion to generate the troubleshooting section of the lesson plan
    function_troubleshooting_issue= [{
            "name": "create_troubleshooting_issue",
            "description": "Act as a teacher, continue create 'troubleshooting' section for given lesson plan. Troubleshooting to focus on software/hardware issues.",
            "parameters": {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "description": "List of the software technical issues that can be encountered during lesson learning, e.g. CoSpaces website is not responding.",
                    "items": {
                    "type": "string"
                    }
                }
                },
                "required": ["issues"]
            }
        }]
        
    function_troubleshooting_reasons= [{
            "name": "create_troubleshooting_reasons",
            "description": "Act as a teacher, determine what possible reasons causing the software issue",
            "parameters": {
            "type": "object",
            "properties": {
                "possible_reasons": {
                    "type": "array",
                    "description": "Possible reasons for the issue, e.g. Issues with web connectivity or a server issue has occurred.",
                    "items": {
                    "type": "string"
                    }
                }
                },
                "required": ["possible_reasons"]
            }
        }]

    function_troubleshooting_resolution= [{
            "name": "create_troubleshooting_resolution",
            "description": "Act as a teacher, determine several ways to solve the issue",
            "parameters": {
            "type": "object",
            "properties": {
                "resolution": {
                    "type": "array",
                    "description": "Resolutions to solve the issue, e.g. Restart the CoSpaces web browser",
                    "items": {
                    "type": "string"
                    }
                }
                },
                "required": ["resolution"]
            }
        }]

    issueCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"You are a {subject} teacher for {grade} student, determine ONLY TECHNICAL issues about {software[0]} software/hardware during the lesson about '{title}' that will encountered by teachers. IMPORTANT: ONLY FOCUSING on troubleshooting detailed TECHNICAL software/hardware issues. For more context, here is the lesson overview: '{lesson_overview}'",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_troubleshooting_issue,
        max_tokens=4096,
        temperature=0.5,
        presence_penalty=0.6,
        top_p=0.8,
    )

    output_content = issueCompletion.choices[0].message.function_call.arguments
    issues = json.loads(output_content).get('issues',{})

    troubleshooting = {'issues': []}

    for issue in issues:
        # Generate possible reasons
        reasonsCompletion = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Determine what possible reasons regarding this {software[0]} issue: '{issue}'",
                },
            ],
            response_format={ "type": "json_object" },
            functions=function_troubleshooting_reasons,
            max_tokens=4096,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
        )

        output_content = reasonsCompletion.choices[0].message.function_call.arguments
        reasons = json.loads(output_content).get('possible_reasons',{})

        # Generate resolution
        resolutionCompletion = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Determine possible resolutions regarding this {software[0]} issue: '{issue}'. The possible reasons for this issue are: {reasons}",
                },
            ],
            response_format={"type": "json_object"},
            functions=function_troubleshooting_resolution,
            max_tokens=4096,
            temperature=0.5,
            presence_penalty=0.6,
            top_p=0.8,
        )

        output_content = resolutionCompletion.choices[0].message.function_call.arguments
        resolution = json.loads(output_content).get('resolution', [])
        
        # Append issue, possible reasons, and resolution to troubleshooting dictionary
        troubleshooting['issues'].append({
            'issue': issue,
            'possible_reasons': reasons,
            'resolution': resolution
        })

    return troubleshooting

def generate_assessment(topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives, outcomes, real_world_application, lesson_overview, pre_lesson_preparation, title, requirements, tech_concept):
    # completion to generate the assessment rubric section of the lesson plan
    function_assessment_content= [{
        "name": "create_assessment_content",
        "description": "Act as a teacher, continue create 'assessment' related to content knowledge (e.g. decimals, narrative writing, life cycles…)",
        "parameters": {
        "type": "object",
        "properties": {
            "assessment": {
                "type": "string",
                "description": "The assessment objective to be achieved by learners in ONE SHORT SENTENCE without mentioning the software used in the lesson, e.g. Create a map to show spatial distribution and varying severity of extreme weather events. IMPORTANT: This objective should be phrases that concisely describe what is being evaluated (not a long sentence). This assessment should related to content knowledge (e.g. decimals, narrative writing)"
            },
            "emerging": {
                "type": "array",
                "description": "'Emerging' criteria description that fulfiled the assessment objective (Make it into array list), e.g. Showed poor understanding of climate change and its causes and impacts.",
                "items": {
                "type": "string"
                }
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
            "required": ["assessment", "emerging", "developing", "proficient"]
        }
        }
    ]

    function_assessment_tech= [{
        "name": "create_assessment_tech",
        "description": "Act as a teacher, continue create 'assessment' related to tech skill knowledge (e.g. code writing, app design, etc.)",
        "parameters": {
        "type": "object",
        "properties": {
            "assessment": {
                "type": "string",
                "description": "The assessment objective to be achieved by learners in ONE SHORT SENTENCE, e.g. Create a map to show spatial distribution and varying severity of extreme weather events.  IMPORTANT: This objective should be phrases that concisely describe what is being evaluated (not a long sentence). This assessment should related to tech skill knowledge (e.g. code writing, app design, etc.)"
            },
            "emerging": {
                "type": "array",
                "description": "'Emerging' criteria description that fulfiled the assessment objective (Make it into array list), e.g. Showed poor understanding of climate change and its causes and impacts.",
                "items": {
                "type": "string"
                }
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
            "required": ["assessment", "emerging", "developing", "proficient"]
        }
        }
        ]
    if len(requirements) == 1:
        requirement_string = requirements[0]
    elif len(requirements) == 2:
        requirement_string = f"{requirements[0]} and {requirements[1]}"
    else:
        requirement_string = ', '.join(requirements[:-1]) + f", and {requirements[-1]}"

    assessment_content_user_prompt = f"""You are teaching about {topic} in a {subject} class for {grade} student. Create MAXIMUM 2 assessments RELATED to the fundamental theories in this lesson, here are the fundamental theories: {requirement_string}.
    REMEMBER TO GENERATE: assessment, emerging, proficient, developing."""

    assessment_content_system_prompt = f"You are a professional {subject} teacher for {grade} student. Now you are teaching about {title}. Create maximum 2 assessments related to fundamental theories of the lesson (e.g. decimals, narrative writing, life cycles). Answer in JSON"

    assessment_tech_user_prompt = f"""REMEMBER TO GENERATE: assessment, emerging, proficient, developing. You are a {subject} teacher for {grade} student, generate MAXIMUM 2 assessments related to tech skill knowledge (e.g. code writing, app design, etc.) for your lesson plan with following criteria:
                        lesson title: {title},
                        topic: {topic},
                        grade: {grade},
                        subject: {subject},
                        student profile: {student_profile},
                        software used in this lesson: {software},
                        key concepts: {key_concepts},
                        lesson objectives: {objectives},
                        learning outcomes: {outcomes},
                        lesson overview: {lesson_overview}"""

    assessment_tech_system_prompt = f"You are a professional {subject} teacher for {grade} student. Now you are teaching about {title}. Create maximum 2 assessments related to tech skill knowledge (e.g. code writing, app design, etc.). Answer in JSON"

    def split_assessment(assessment):
        # Keywords to identify and split the categories
        split_keywords = ['Emerging:', 'Developing:', 'Proficient:', '\nEmerging:', '\nDeveloping:', '\nProficient:', 'emerging:', 'developing:', 'proficient:', '\nemerging:', '\ndeveloping:', '\nproficient:']
        for keyword in split_keywords:
            if keyword in assessment:
                parts = assessment.split(keyword)
                # Assuming the first part is always the assessment description
                assessment_desc = parts[0].strip()
                categories = {keyword[:-1].lower(): part.strip() for keyword, part in zip(split_keywords, parts[1:])}
                return assessment_desc, categories
        # Return the original assessment and empty categories if splitting is not applicable
        return assessment, {}

    def is_rubric_valid(rubric):
        # Check if the rubric has all the required fields
        return all(key in rubric for key in ['assessment', 'emerging', 'developing', 'proficient'])

    def fetch_assessment_rubric(client, system_prompt, user_prompt, function_assessment, max_retries=5, model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd"):
        retries = 0
        while retries < max_retries:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                functions=function_assessment,
                max_tokens=4096,
                temperature=0.8,
                presence_penalty=0.6,
                top_p=0.8,
            )

            output_content = completion.choices[0].message.function_call.arguments
            assessment = {'assessment': [json.loads(output_content)]}
            assessment_rubric = assessment.get('assessment', [])

            for item in assessment_rubric:
                # Check and potentially split the assessment into separate categories
                assessment_desc, categories = split_assessment(item.get('assessment', ''))
                item['assessment'] = assessment_desc
                for category, content in categories.items():
                    item[category] = [content]  # Assuming each category content is a single string to be put into a list

            if all(is_rubric_valid(item) for item in assessment_rubric):
                return assessment_rubric, completion

            retries += 1
            print(f"Retrying API call ({retries}/{max_retries}) due to incomplete assessment rubric data...")

        print("Max retries reached without obtaining a complete assessment rubric.")

        return []

    # Usage
    assessment_rubric_content, assContCompletion = fetch_assessment_rubric(client, assessment_content_system_prompt, assessment_content_user_prompt, function_assessment_content)
    assessment_rubric_tech, assTechCompletion = fetch_assessment_rubric(client, assessment_tech_system_prompt, assessment_tech_user_prompt, function_assessment_tech)

    # Combine the rubrics
    assessment_rubric = assessment_rubric_content + assessment_rubric_tech
    return assessment_rubric

def generate_opening(topic, subject, grade, student_profile, gen_tech_domain, software, lesson_overview, key_concepts, title):
    # generate the slide accordingly when the student profile is provided and when its not
    if student_profile:
        system_slide = f"You are a {subject} teacher for {grade} student with {student_profile} special needs. You want to explain about {topic} and how to use {software} for this topic, now write your slide into output JSON."
    else:
        system_slide = f"You are a {subject} teacher for {grade} student, you want to explain about {topic} and how to use {software} for this topic. Now write your slide into output JSON."

    next_prompt_system = f"You are a {subject} teacher for {grade} student who currently making an opening presentation slide about: {lesson_overview.get('opening overview',{})}. Your objectives are: {lesson_overview.get('opening objectives',{})}. You can talk more about the {topic} in subject of {subject}. Write in JSON format"


    challengeCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": next_prompt_system
            },
            {
                "role": "user",
                "content": f"""Imagine three different experts are answering this challenge.
                        All experts will write down 1 step of their thinking,
                        then share it with the group.
                        Then all experts will go on to the next step, etc.
                        If any expert realises they're wrong at any point then they leave.
                        The challenge is to make a design challenge that will be faced by {grade} student during the {subject} lesson about {title}, using {software}. Design challenge is the project that the students need to complete in this lesson. For more context, here is the overview of your lesson: {lesson_overview.get('opening overview',{})}; {lesson_overview.get('main overview',{})}; {lesson_overview.get('closing overview',{})}""",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_challenge,
        max_tokens=4000,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = challengeCompletion.choices[0].message.function_call.arguments
    challenge = json.loads(output_content).get('challenge',{})
    design_objectives = json.loads(output_content).get('artifacts',{}).lower()
    print(f"Design Challenge: {challenge}")
    print(f"Design artifacts: {design_objectives}")

    requirementsCompletion = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:eddy4teachers:ft-batch2:8uYKkYpd",
        messages=[
            {
                "role": "system",
                "content": next_prompt_system
            },
            {
                "role": "user",
                "content": f"You are teaching about {title} to a {grade} student in {subject} subject. Determine MAXIMUM 3 {subject} fundamental theories for student to execute this design challenge: {challenge}",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_requirements,
        max_tokens=4096,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = requirementsCompletion.choices[0].message.function_call.arguments
    requirements = json.loads(output_content).get('requirements',{})

    # Split each requirement into separate strings
    split_requirements = []
    for req in requirements:
        split_reqs = req.split('\n')
        for split_req in split_reqs:
            split_req = split_req.strip()
            if split_req:
                split_requirements.append(split_req)

    requirements = split_requirements

    # Split each requirement into separate strings
    split_requirements = []
    for req in requirements:
        split_reqs = req.split('\n')
        for split_req in split_reqs:
            split_req = split_req.strip()
            if split_req:
                split_requirements.append(split_req)

    requirements = split_requirements
    
    opening_activity_complete = {
        'opening_activity': {
            'Slide 1': f"{title}",
            'Slide 2': f"This slide is an overview on what student will learn. In the slide content, you will write 3 pointer sentences, where each pointer is a summarization from each activity overview in a tone like you are talking to your student. These are the lesson overviews for each activities: '{lesson_overview.get('opening overview',{})}'; '{lesson_overview.get('main overview',{})}'; '{lesson_overview.get('closing overview',{})}'; IMPORTANT: Write this slide in a tone as you are writing to your {grade} student. ",
            'Slide 3': f"""Trigger activity to hook the students in the lesson, it is a provocative question to get students excited about the topic ({title}). The trigger activity could possibly also hint at the technology (NOT MENTIONING THE SOFTWARE) that will be introduced later on - this often helps to excite students.
            Trigger activity should only focus on introducing the {topic} with a simple question that gets learners to wonder and participate in a simple discussion.
            This slide title should be in form of a engaging and triggering question.
            """,
        }
    }

    # Get the current slide number
    current_slide_number = len(opening_activity_complete['opening_activity'])

    # Adding slides for each requirement
    for requirement in requirements:
        current_slide_number += 1
        opening_activity_complete['opening_activity'][f'Slide {current_slide_number}'] = f"This slide reviews the topic about {requirement} in 3-4 bullet points. Make sure the review aligns with the {subject} subject for {grade} student, in topic of {topic}. In this slide, student will listening to teacher as their teacher is reviewing the content."
        current_slide_number += 1
        opening_activity_complete['opening_activity'][f'Slide {current_slide_number}'] = f"This slide checks for student understanding about the {requirement} by asking 1-2 assessment questions (can be multiple choice question) inside the SLIDE CONTENT. The slide title and slide content should be written in a tone as you are talking to your student."

    # Modify the content of 'Slide 2'
    opening_activity_complete['opening_activity']['Slide 2'] = f"""This slide is the overview of the lesson, THE SLIDE CONTENT SHOULD GENERATE ALL OF THESE 3 BULLET POINTS:
    1. A SHORT summarization of the fundamental theories in this lesson, which are: {requirements}. For example: 'Understand fractions and identify fractions in shapes';
    2. A SHORT summarization of what students will learn from the {software[0]} during this lesson. For example: 'Train a machine to recognize fractions using Google Teachable Machine';
    3. A SHORT summarization of the design challenge, which is: {challenge}; For example: 'Test and evaluate the AI model'.;
    IMPORTANT: WRITE THE SLIDE CONTENT in tone as you are writing for your student."""

    # Print the updated opening_activity_complete
    last_slide_number = len(opening_activity_complete['opening_activity'])
    next_slide_number = last_slide_number + 1
    next_slide_main = f"Slide {next_slide_number}"

    return opening_activity_complete, system_slide, next_slide_main, challenge, requirements, design_objectives

def generate_main(topic, subject, grade, software, next_slide_main, title, challenge, design_objectives, lesson_overview):
    function_skillset= [{
            "name": "determine_tech_concept",
            "description": "Determine relevant tech skillsets or tech concept for the given softwar. Tech concept is not tech domain",
            "parameters": {
                "type": "object",
                "properties": {
                    "skillset": {
                        "type": "string",
                        "description": '''Generate a couple of possible tech skillsets or concepts for given software used in the lesson.
                        These skillsets should be suitable for K-12 level, meaning they should be accessible by naive but intelligent layman.
                        Follow this example logics:
                        Blender:
                        Basic 3D animation principles,
                        Introduction to digital sculpting and modeling,

                        Food Chain Simulator:
                        Ecosystem dynamics and food web construction,
                        Basic simulation and modeling concepts,

                        Python:
                        Introductory programming and problem-solving,
                        Data structures and simple data analysis,

                        Unity:
                        Basics of game design and development,
                        Introduction to coding with C# for interactive applications,

                        Infinite Drum Machine:
                        Introduction to digital music creation,
                        Basics of sound sampling and looping,

                        Fusion 360:
                        Fundamentals of CAD (Computer-Aided Design),
                        Introduction to mechanical design and engineering,

                        Assemblr Edu:
                        Augmented Reality (AR) projects in education,
                        Basic 3D modeling and animation for AR,

                        Roller Coaster Tycoon 2:
                        Basics of economic management and strategy,
                        Principles of physics through roller coaster design,

                        Ansys 3D:
                        Introduction to engineering simulation and analysis,
                        Basic concepts of finite element analysis (FEA),

                        Arduino:
                        Introduction to electronics and microcontrollers,
                        Basics of coding for hardware projects,

                        Mecabricks:
                        Digital LEGO modeling and design,
                        Introduction to spatial reasoning and architecture,

                        Tinkercad Circuits:
                        Basics of electronic circuits and prototyping,
                        Introduction to simple programming for electronic projects.

                        Autodesk CFD 2021:
                        Introduction to computational fluid dynamics (CFD),
                        Basic principles of fluid mechanics and simulation,

                        Google Arts and Culture:
                        Digital exploration of art and cultural heritage,
                        Introduction to art history and curation,

                        StoryMap JS:
                        Basics of digital storytelling and journalism,
                        Introduction to geographic information systems (GIS) concepts,

                        QGIS:
                        Introduction to geographic information systems (GIS) and mapping,
                        Basic data visualization and spatial analysis,

                        CoSpaces:
                        Virtual Reality (VR) and 3D world creation,
                        Basic coding for interactive experiences in VR'''
                    }
                },
                "required": ["skillset"],
            }
        }]

    function_tech_concepts= [{
            "name": "determine_tech_concept",
            "description": "Determine relevant tech skillsets or tech concept for the given software. Tech concept is not tech domain",
            "parameters": {
                "type": "object",
                "properties": {
                    "tech concept": {
                        "type": "string",
                        "description":"Take one word related to tech concept from the given sentence, e.g. 'game design principles', 'programming'",
                    }
                },
                "required": ["tech concept"],
            }
        }]

    skillsetCompletion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": f"You are a professional tech person and a teacher. You need to determine what tech concept used in {software[0]} that used for your lesson in class. Answer in JSON"
            },
            {
                "role": "user",
                "content": f"Determine possible tech skillsets for {software[0]}, this skillsets should match the topic of the lesson which is {topic} in {subject} subject for {grade} student. DO NOT MENTION THE SOFTWARE NAME. These skillsets should be suitable for K-12 level, meaning they should be accessible by naive but intelligent layman.",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_skillset,
        max_tokens=2000,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = skillsetCompletion.choices[0].message.function_call.arguments
    skillset = json.loads(output_content).get('skillset',{})

    techconceptsCompletion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": f"You are a professional tech person and a teacher. Extract valuable words from given sentence."
            },
            {
                "role": "user",
                "content": f"""Imagine three different experts are answering this question.
                          All experts will write down 1 step of their thinking,
                          then share it with the group.
                          Then all experts will go on to the next step, etc.
                          If any expert realises they're wrong at any point then they leave.
                          The question is to extract ONLY 1-2 TECH RELATED WORDS that represent this skillset that will learnt by student: {skillset}""",
            },
        ],
        #response_format={ "type": "json_object" },
        functions=function_tech_concepts,
        max_tokens=1000,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = techconceptsCompletion.choices[0].message.function_call.arguments
    tech_concept = json.loads(output_content).get('tech concept',{})

    print(f"Skillset: {skillset}")
    print(f"Tech concept: {tech_concept}")

    slide_number_tech = f"Slide {int(next_slide_main.split()[1]) + 1}"
    slide_number_exploration1 = f"Slide {int(slide_number_tech.split()[1]) + 1}"
    slide_number_exploration2 = f"Slide {int(slide_number_exploration1.split()[1]) + 1}"
    slide_number_design = f"Slide {int(slide_number_exploration2.split()[1]) + 1}"
    slide_number_software_intro = f"Slide {int(slide_number_design.split()[1]) + 1}"
    slide_number_software_interface = f"Slide {int(slide_number_software_intro.split()[1]) + 1}"
    slide_number_software_features = f"Slide {int(slide_number_software_interface.split()[1]) + 1}"
    slide_number_tutorial = f"Slide {int(slide_number_design.split()[1]) + 1}"

    main_activity_complete = {
    'main_activity':
        {f"{next_slide_main}": f"ONLY GENERATE SLIDE TITLE FOR THIS SLIDE, NO SLIDE CONTENT. Slide title for this slide should be like this 'Today, we are going to use {tech_concept} to help us understand more about {topic}'. There is no slide content in this slide. NOTE FOR SLIDE TITLE: Incorporate the overview of covered topics into initial slides of the opening activity, rather than the main activity. Ensure continuity between the opening and main activities, avoiding a disjointed approach. Establish a seamless transition between the opening and main activities. For context, this is the overview of the opening activity: '{lesson_overview['opening overview']}'",
        f"{slide_number_tech}": f"Slide title should be:  'What is {tech_concept}?'; The slide content need to explain in one sentence about the definition of {tech_concept}, ALSO INCLUDE this: 'Let’s watch the following video! [insert video URL]'. You can put relevant YouTube URL about {tech_concept}",
        f"{slide_number_exploration1}": f"For this slide content, use analogies and examples to help {grade} students convey how the {tech_concept} works, adjust the slide title to engaging title. Unpack the tech concept in a way that is age appropriate for students. Write the slide content about analogies and examples to help convey students how the {tech_concept} works. IMPORTANT TO Write this slide content in tone as you are writing for your students, e.g 'How can a machine tell the difference between an apple and a banana?'. IMPORTANT NOTES: Ensure slide title matches content accurately. Specify the experimentation activity involving game mechanics and physics simulations clearly if the topic is about design and simulation. Introduce relevant terms and functions. Ensure slide serves a purpose, possibly by including a stop-motion or claymation video demonstration. Maintain coherence and flow in the presentation.",
        f"{slide_number_exploration2}": f"Continue further explanation of {tech_concept} from previous slide, you need to give example about {tech_concept} in daily life, and adjust the slide title to engaging title for {grade} students. Write the slide content to help convey students how the {tech_concept} works, also give example. IMPORTANT TO write this slide content in tone as you are writing for your {grade} students. IMPORTANT NOTES: Ensure slide title matches content accurately. Maintain coherence and flow in the presentation.",
        f"{slide_number_design}": f"THIS SLIDE TITLE SHOULD BE: 'Using your understanding of {topic} and {tech_concept}, you will use {software[0]} to {design_objectives}'. IMPORTANT: THERE IS NO SLIDE CONTENT, REMEMBER THIS. Ensure the design challenge is specific rather than open-ended.",
        f"{slide_number_software_intro}": f"Introduce the {software[0]}, slide title can be: 'Introduction to {software[0]}'. Summarize it in 3-4 bullet points, focusing on what the software does and What it can be used for. FOR SLIDE CONTENT, IMPORTANT TO Write this slide content in tone as you are writing for your students",
        f"{slide_number_software_interface}": f"Introduce students to the {software[0]} interface, the slide title can be: '{software[0]} Interface'. In the slide content, explain the main toolbars and regions of the interface, and how to navigate it. You should help student to understand the {software[0]} interface. FOR SLIDE CONTENT, IMPORTANT TO Write this slide content in tone as you are writing for your students",
    }}

    function_software_features= [{
            "name": "determine_software_features",
            "description": "Determine relevant features in the given software related to the lesson.",
            "parameters": {
                "type": "object",
                "properties": {
                    "features": {
                        "type": "array",
                        "description":"List of the relevant features (MAXIMUM 3 FEATURES) of the software needed for student to accomplish the lesson design challenge",
                        "items": {
                        "type": "string"
                    }
                    }
                },
                "required": ["features"],
            }
        }]

    featuresCompletion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": f"You are a professional {software[0]} specialist. You need to determine what key features used in {software[0]} will be useful for student to complete their design challenge. Answer in JSON"
            },
            {
                "role": "user",
                "content": f"In this {subject} class, {grade} student learning about {title}, using {software[0]}. Student will have design challenge about: {challenge}; Determine MAXIMUM 3 {software[0]} key features that will be used by student to working their design challenge.",
            },
        ],
        response_format={ "type": "json_object" },
        functions=function_software_features,
        max_tokens=2000,
        temperature=0.6,
        presence_penalty=0.6,
        top_p=0.8
    )

    output_content = featuresCompletion.choices[0].message.function_call.arguments
    features = json.loads(output_content).get('features',{})

    # Get the current slide number
    current_slide_number = int(slide_number_software_features.split()[1])-1

    for feature in features:
        current_slide_number += 1
        main_activity_complete['main_activity'][f'Slide {current_slide_number}'] = f"In this slide, summarize (in 3-4 bullet points) the {feature} feature in {software[0]} that will be used by student during this lesson about {title}. This lesson is tailored for {subject} in {grade} student, therefore IMPORTANT TO WRITE this slide content as you are writing for your students. Ensure each point provides sufficient detail. Include examples illustrating where features can be applied. Refine the challenge statement to be specific and actionable, guiding students on what to find or do. Avoid generic content and repetition. Provide more information on feature scaling and its relevance"

    main_activity_individual = {'main_activity':
    {f"Slide {current_slide_number}": f"This slide is for giving student an example of how to use the {software[0]} to create a very simple response to the design challenge. The slide title can be: '{software[0]} in action'. The slide content can be: 'Let’s take a look at how we can use {software[0]} to [summarize the design challenge objectives]'. For context, the design challenge is: '{challenge}'.",
    f"Slide {current_slide_number + 1}": f"This slide is to revisit the design challenge in this lesson, which is: {challenge}. Slide title should be like “Your design challenge today…”. Provide details about the design challenge, i.e. the task that students need to accomplish. Include details on how students are supposed to submit their work, e.g. if its CoSpaces, students can submit using their class code; if its Google teachable machine they will need to email their teacher, etc."}
    }
    slide_model_example = f"Slide {current_slide_number}"
    next_slide_number = current_slide_number + 2
    next_slide_closing = f"Slide {next_slide_number}"

    main_activity_complete['main_activity'].update(main_activity_individual['main_activity'])
    return main_activity_complete, next_slide_closing, tech_concept, slide_number_design, next_slide_main, slide_model_example,  slide_number_exploration1, slide_number_exploration2, slide_number_software_intro, slide_model_example, slide_number_tech

def generate_closing(next_slide_closing, grade, software, topic, challenge, tech_concept):
    next_slide_number = int(next_slide_closing.split()[1]) + 1
    slide_number_reflection = f"Slide {next_slide_number}"
    next_slide_number = int(slide_number_reflection.split()[1]) + 1
    slide_number_consolidation = f"Slide {next_slide_number}"

    closing_activity = {'closing_activity':
    {f"{next_slide_closing}": f"""In this slide content, you should using the tone as you are giving cheerful instruction for your {grade} students. This slide is for sharing of creations, get students to share their creations with each other. For slide title, it should be started like 'Sharing your xxx' words, referencing to their given project.
    In order for student to sharing their creations, you should choose ONE method of sharing: 'through a gallery walk', or 'pair students up to show each other'. SELECT ONE METHOD according to their {software[0]} project and the topic {topic}.
    Include some suggested questions or actions that students should take when viewing other student work - e.g. give constructive feedback. IMPORTANT: Give details about how to present should be included. Also provide guidance on what constructive feedback looks like.
    For context, in this lesson student has already done a project about: {challenge}.""",
    f"{slide_number_reflection}": f"""Write this slide using the tone as you are writing for your {grade} students. In this slide, facilitate whole-class reflection on the activity.
    There are two types of reflections: 1. Reflection questions that teachers pose to students directly and students respond; OR 2. Thinking routines where students following a structured way of reflecting.
    CHOOSE ONLY ONE REFLECTION TYPE THAT WILL BE SHOWN IN THIS SLIDE.
    IMPORTANT:
    IF YOU ARE CHOOSING 'Thinking routines', here is the slide content guidelines you can follow: ''Think about what you have learned about {tech_concept}. Complete the sentence 'I used to think…. Now I think…'''. Then, ALWAYS PROVIDE THE ANSWER, e.g. 'e.g. I used to think {tech_concept} is complicated. Now I think it is easier'.
    IF YOU ARE CHOOSING 'reflection questions', write MAXIMUM 3 REFLECTION QUESTIONS following these criterions:
    Content Understanding and Integration, Skills Development, Application and Real-world Relevance, Critical Thinking and Problem-solving, Collaboration and Teamwork, Technology Integration, Personal Growth and Self-reflection, Feedback and Future Improvements""",
    f"{slide_number_consolidation}": f"""Using the tone as you are writing for your {grade} students. Summarize the lesson in terms of what students have learnt and accomplished. The slide title should be: 'What have we learned today?'.
    You should also affirm students for their hard work.
    You should also summarize about the design challenge that student has faced, for context, this is the challenge given to student: '{challenge}'""",
    }}

    return closing_activity, slide_number_consolidation, slide_number_reflection

def generate_detailed_slide(opening_activity_complete, main_activity_complete, closing_activity, lesson_overview, grade, system_slide, topic, subject, student_profile, title, software, slide_number_design, next_slide_main, slide_number_consolidation, slide_number_reflection, tech_concept,  slide_number_exploration1, slide_number_exploration2, slide_number_software_intro, slide_model_example, slide_number_tech, challenge):
    if student_profile:
        notes_description = f"""For this slide presentation notes, you want to introduce {topic} topic to {grade} learners with special needs: {student_profile} (provide additional notes regarding {student_profile} needs). This notes for teacher, therefore your tone should be teacher-facing. Write some slide notes to engage teacher to ask guiding questions to learners with no knowledge of {topic} at all.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow. Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Ask students to identify the three design principles for effective visual communication.'
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology.'"""
        notes_description_no_question = f"""For this slide presentation notes, you want to introduce {topic} topic to {grade} learners with special needs: {student_profile} (provide additional notes regarding {student_profile} needs). This notes for teacher, therefore your tone should be teacher-facing.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow. Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology.'"""
    else:
        notes_description = f"""For this slide presentation notes, you want to introduce {topic} topic to {grade} learners. This notes for teacher, therefore your tone should be teacher-facing. Write some slide notes to engage teacher to ask guiding questions to learners with no knowledge of {topic} at all.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow.  Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Ask students to identify the three design principles for effective visual communication.'
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology."""
        notes_description_no_question = f"""For this slide presentation notes, you want to introduce {topic} topic to {grade} learners. This notes for teacher, therefore your tone should be teacher-facing.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow.  Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology."""

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
                    This content should be in manners of student-facing, therefore IMPORTANT to adjust your tone as you are WRITING A CONTENT to a {grade} student. Act as you are guiding students through an exciting journey of learning and discovery. Your explanations should be clear, engaging, and tailored to {grade}-level understanding. You can put equations for student better understanding.
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

    function_notes = [{
        "name": "create_slide_notes",
        "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content",
        "parameters": {
            "type": "object",
            "properties": {
                "slideNotes": {
                    "type": "array",
                    "description": notes_description,
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "slideNotes"
            ]
        }
    }]

    function_notes_no_question = [{
        "name": "create_slide_notes",
        "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content",
        "parameters": {
            "type": "object",
            "properties": {
                "slideNotes": {
                    "type": "array",
                    "description": notes_description_no_question,
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "slideNotes"
            ]
        }
    }]

    function_notes_trigger = [{
        "name": "create_slide_notes",
        "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content",
        "parameters": {
            "type": "object",
            "properties": {
                "slideNotes": {
                    "type": "array",
                    "description": """Generate notes for teacher regarding the trigger activity with following requirements:
                    1. Give student adequate think time to respond to the trigger question.
                    2. Facilitate a discussion around the trigger question. Allow students to provide responses to the trigger question.
                    3. Probe students responses to promote deeper thinking. For example, if students say “One hamburger is an example of a fraction as it represents one whole”, teacher might respond by asking “OK, so what happens if you divide the hamburger equally between four friends?”
                    IMPORTANT TO REMEMBER to put example question from student to teachers and possible answer from teacher.
                    4. Use a thinking routine like Think Pair Share or Claim, Support, Question to allow students to discuss the trigger question.
                    """,
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "slideNotes"
            ]
        }
    }]

    function_question = [{
        "name": "create_slide_notes",
        "description": f"You are an advisor for {subject} teacher for {grade} student, determine is the given slide content suitable for teacher to ask a question to student.",
        "parameters": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": f"Answer only 'Yes' or 'No'. You need to realize that your judgement must be logically accurate for {grade} student, do not ask unecessary question.",
                }
            },
            "required": [
                "response"
            ]
        }
    }]

    function_bloom = [{
        "name": "determine_bloom_verb",
        "description": f"You are an advisor for {subject} teacher for {grade} student, determine ONE suitable bloom verb for the given slide content. ANSWER IN ONE WORD",
        "parameters": {
            "type": "object",
            "properties": {
                "bloom": {
                    "type": "string",
                    "description": f"""Determine the suitable bloom verb for {grade} student from the given slide content, e.g. 'explain', 'summarise', etc.
                    ONLY ANSWER IN ONE WORD OF THE SELECTED BLOOM VERB FROM THIS LIST: recognise, recall, interpret, exemplify, classify, summarise, infer, compare, explain, apply, execute, implement, analyze, differentiate, organize, attribute, evaluate, check, critique, create, generate, plan, produce""",
                }
            },
            "required": [
                "bloom"
            ]
        }
    }]

    function_content_trigger = [{
        "name": "create_slide_content",
        "description": f"You are an assistant for {subject} teacher for {grade} student, create the 'opening' presentation content and materials for given slide keypoints.",
        "parameters": {
            "type": "object",
            "properties": {
                "slideTitle": {
                    "type": "string",
                    "description": """This slide title should be one question that will serve as the trigger question. Write as you are asking to your students.
                    The trigger question SHOULD: Allow students to relate the topic to their personal experiences, or Tap on students’ prior understanding of the topic."""
                },
                "slideContent": {
                    "type": "array",
                    "description": f'''
                    This content should be in manners of student-facing, therefore IMPORTANT to adjust your tone as you are WRITING A CONTENT to a {grade} student. Act as you are guiding students through an exciting journey of learning and discovery. Your explanations should be clear, engaging, and tailored to {grade}-level understanding.
                    Write concisely, not too wordy.''',
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
                    This content should be in manners of student-facing, therefore IMPORTANT to adjust your tone as you are WRITING A CONTENT to a {grade} student. Act as you are guiding students through an exciting journey of {software} tutorial. Gives a very well detailed tutorial.
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
                    "description": f'''This content should be in manners of student-facing, therefore IMPORTANT to adjust your tone as you are WRITING A CONTENT to a {grade} student. Act as you are guiding students through an exciting journey of learning and discovery.
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

    if student_profile:
        notes_description = f"""MAKE SURE THESE NOTES IS DIFFERENT FROM THE SLIDE CONTENT. MAXIMUM 50 WORDS. For this slide presentation notes, you want to introduce {topic} topic to {grade} learners with special needs: {student_profile} (provide additional notes regarding {student_profile} needs). This notes for teacher, therefore your tone should be teacher-facing. Write some slide notes to engage teacher to ask guiding questions to learners with no knowledge of {topic} at all.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow. Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Ask students to identify the three design principles for effective visual communication.'
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology.'"""
        notes_description_no_question = f"""MAKE SURE THESE NOTES IS DIFFERENT FROM THE SLIDE CONTENT. MAXIMUM 50 WORDS. For this slide presentation notes, you want to introduce {topic} topic to {grade} learners with special needs: {student_profile} (provide additional notes regarding {student_profile} needs). This notes for teacher, therefore your tone should be teacher-facing.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow. Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology.'"""
    else:
        notes_description = f"""MAKE SURE THESE NOTES IS DIFFERENT FROM THE SLIDE CONTENT. MAXIMUM 50 WORDS. For this slide presentation notes, you want to introduce {topic} topic to {grade} learners. This notes for teacher, therefore your tone should be teacher-facing. Write some slide notes to engage teacher to ask guiding questions to learners with no knowledge of {topic} at all.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow.  Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Ask students to identify the three design principles for effective visual communication.'
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology."""
        notes_description_no_question = f"""MAKE SURE THESE NOTES IS DIFFERENT FROM THE SLIDE CONTENT. MAXIMUM 50 WORDS. For this slide presentation notes, you want to introduce {topic} topic to {grade} learners. This notes for teacher, therefore your tone should be teacher-facing.
        Teacher notes should be SHORT BRIEF SENTENCES and presented in bullet points, providing facilitating instructions rather than a verbatim script for the teacher to follow.  Each point SHOULD start with a verb (‘tell’, ‘introduce’, ‘inform’, etc.) describing what the teacher should be doing as they are on that particular slide.
        For example:
        'Introduce students to the trigger question. Accept different responses from students.',
        'Tell students that today, we will be exploring how to bring storybook characters to life with the help of technology."""

    activities = {
        'opening_activity': opening_activity_complete,
        'main_activity': main_activity_complete,
        'closing_activity': closing_activity
    }

    output_data = {}
    content_prompt = 0
    content_completion = 0
    max_words = '50'

    for activity_key, activity_data in activities.items():
        activity_slides = activity_data.get(activity_key, {})
        activity_output = {}

        for slide_number, slide_content in activity_slides.items():
            if slide_number == 'Slide 1':
                continue

            activity_overview = lesson_overview.get(f"{activity_key} overview", [])
            activity_objectives = lesson_overview.get(f"{activity_key} objectives", [])
            if slide_number == 'Slide 3':
                function_content = function_content_trigger
            else:
                if activity_key == 'opening_activity':
                    function_content = function_content_opening
                elif activity_key == 'main_activity':
                    function_content = function_content_main
                elif activity_key == 'closing_activity':
                    function_content = function_content_closing

            # Flag to indicate if the output is empty
            output_empty = True

            print(f"Generating content for {slide_number}...")

            while output_empty:
                contentCompletion = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {
                            "role": "system",
                            "content": f"Act as a {subject} teacher for {grade} student. Adjust your tone as you are guiding students through an exciting journey of learning and discovery. Your explanations should be clear, engaging, and tailored to {grade}-level understanding. Answer in JSON"
                        },
                        {
                            "role": "user",
                            "content": f"""Imagine three different experts are answering this question.
                            All experts will write down 1 step of their thinking,
                            then share it with the group.
                            Then all experts will go on to the next step, etc.
                            If any expert realises they're wrong at any point then they leave.
                            The question is to generate presentation slide content with MAXIMUM {max_words} words for presentation {slide_number} with these keypoints: '{slide_content}'. Remember, this slide should fulfil these lesson overview: '{activity_overview}', and these lesson objectives: '{activity_objectives}'."""
                        },
                    ],
                    response_format={ "type": "json_object" },
                    functions=function_content,
                    max_tokens=4096,
                    temperature=0.9,
                    presence_penalty=0.8,
                    top_p=0.8
                )

                output_content = contentCompletion.choices[0].message.function_call.arguments
                slide_output = json.loads(output_content)

                # Check if the 'slideContent' field is empty
                if slide_number in ['Slide 1', slide_number_design, next_slide_main]:
                    output_empty = False
                else:
                    if slide_output.get('slideContent', []) or slide_output.get('slideNotes', []):
                        output_empty = False
                    else:
                        print(f"Output: {slide_output}")
                        print(f"Output is empty. Rerunning completion for slide {slide_number}...")

            activity_output[slide_number] = slide_output
            content_prompt += contentCompletion.usage.prompt_tokens
            content_completion += contentCompletion.usage.completion_tokens

        output_data[activity_key] = activity_output

    for slide in output_data['opening_activity'].values():
        if not slide['slideContent']:
            slide['slideContent'] = [' ']

    # New slide data for 'Slide 1'
    slide_1_data = {
        'Slide 1': {
            'slideTitle': f"{title}",
            'slideContent': []
        }
    }

    # Copy the existing slides to a new dictionary
    existing_slides = output_data['opening_activity'].copy()

    # Clear the existing slides in the output_data
    output_data['opening_activity'].clear()

    # Update the output_data with 'Slide 1' followed by existing slides
    output_data['opening_activity'].update(slide_1_data)
    output_data['opening_activity'].update(existing_slides)

    # Iterate through each activity in output_data
    for activity_key, activity_data in output_data.items():
        # Iterate through each slide in the activity
        for slide_number, slide_content in activity_data.items():
            # Add an empty 'slideNotes' field if it doesn't exist
            slide_content.setdefault('slideNotes', [])

    # Check the structure of the slides
    def check_and_update_slides(output_data):
        for activity_type, activity_data in output_data.items():
            for slide_name, slide_data in activity_data.items():
                # Check if slide contains 'slideTitle', 'slideContent', and 'slideNotes'
                if 'slideTitle' not in slide_data:
                    slide_data['slideTitle'] = ''
                if 'slideContent' not in slide_data:
                    slide_data['slideContent'] = []
                if 'slideNotes' not in slide_data:
                    slide_data['slideNotes'] = []
                # Remove unwanted keys
                slide_data.pop('slideOverview', None)
                slide_data.pop('slideObjectives', None)

    check_and_update_slides(output_data)

    selected_slides = []  # Initialize a list to store selected slide numbers

    # Iterate through each activity in output_data
    for activity_key, activity_data in output_data.items():
        # Iterate through each slide in the activity
        for slide_number, slide_content in activity_data.items():
            print(f"Checking for {slide_number}...")
            # Run code to determine if a question should be given for the slide
            questionCompletion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system",
                        "content": f"Act as an advisor for {subject} teacher {grade} student. You need to determine which slide is suitable for the teacher to ask a question to students. Answer only 'Yes' or 'No. Answer in JSON"
                    },
                    {
                        "role": "user",
                        "content": f"Your client is a {subject} teacher for {grade} student, teaching about {title} for {subject} subject. Answer only 'Yes' or 'No. Determine if this slide content should be given a question for students to ask their understanding. Here is the slide content: {slide_content}"
                    },
                ],
                response_format={"type": "json_object"},
                functions=function_question,
                max_tokens=4096,
                temperature=0.9,
                presence_penalty=0.8,
                top_p=0.8
            )

            # Extract the response indicating if a question should be given
            response = json.loads(questionCompletion.choices[0].message.function_call.arguments)
            content_prompt += questionCompletion.usage.prompt_tokens
            content_completion += questionCompletion.usage.completion_tokens
            print(response['response'])

            # Check if the response is 'Yes', then store the slide number
            if response['response'] == 'Yes':
                selected_slides.append(slide_number)

    # Print the selected slide numbers
    print("Selected slides for questions:", selected_slides)

    # Iterate through each activity in output_data
    for activity_key, activity_data in output_data.items():
        # Iterate through each slide in the activity
        for slide_number, slide_content in activity_data.items():
            # Skip Slide 1
            if slide_number == 'Slide 1':
                continue

            bloom_result = None
            max_bloom_retry = 5
            retry = 0
            while True:
                if slide_number in ['Slide 1', next_slide_main]:
                    break
                bloomCompletion = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {
                            "role": "system",
                            "content": f"Act as an advisor for {subject} teacher {grade} student. Summarize the given slide content and determine the appropriate bloom verb. Answer in JSON"
                        },
                        {
                            "role": "user",
                            "content": f"""Imagine three different experts are answering this question.
                            All experts will write down 1 step of their thinking,
                            then share it with the group.
                            Then all experts will go on to the next step, etc.
                            If any expert realises they're wrong at any point then they leave.
                            The question is to determine ONE appropriate bloom taxonomy verb for this given slide content. ONLY ANSWER ONLY IN ONE WORD OF THE VERB OF THE BLOOM TAXONOMY FROM THE VERB LIST. Here is the slide content: '{slide_content}'"""
                        },
                    ],
                    response_format={"type": "json_object"},
                    functions=function_bloom,
                    max_tokens=4096,
                    temperature=0.9,
                    presence_penalty=0.8,
                    top_p=0.8
                )

                # Extract the response indicating if a question should be given
                bloom = json.loads(bloomCompletion.choices[0].message.function_call.arguments)
                bloom_result = bloom.get('bloom', '')
                if len(bloom_result.split()) > 1:
                    if retry <= max_bloom_retry:
                        print("Bloom result is longer than one word, rerunning completion...")
                        retry += 1
                    else:
                        bloom_result = 'explain'
                        print(f"Bloom verb for {slide_number}: {bloom_result}")
                        break
                else:
                    print(f"Bloom verb for {slide_number}: {bloom_result}")
                    break

            # Slide notes prompt for each slide
            prompt_question = f"utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a short brief notes to help your client delivers slide content like this: '{slide_content}'; IMPORTANT: INCLUDE EXAMPLE QUESTIONS. SLIDE NOTES SHOULD BE DIFFERENT FROM THE SLIDE CONTENT. Your client is a {subject} teacher for {grade} student, teaching about {title} for {subject} subject."
            prompt_non_question = f"utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a short brief notes to help your client delivers slide content like this: '{slide_content}'; IMPORTANT: SLIDE NOTES SHOULD BE DIFFERENT FROM THE SLIDE CONTENT. MAXIMUM {max_words} WORDS. Your client is a {subject} teacher for {grade} student, teaching about {title} for {subject} subject."
            prompt_trigger = f"utilizing '{bloom_result}' bloom taxonomy in your tone. Now, please generate a detailed notes (SHOULD BE DIFFERENT FROM THE SLIDE CONTENT) to help your client delivers this slide content: '{slide_content}'; IMPORTANT: In one point among the notes, there should be the probing section, where it should include some sample of question for teacher to ask the students ALSO example question from student to teachers AND possible answer from teacher. So, pretend as you are a student asking further explanation to the teacher. MAXIMUM {max_words} WORDS. Your client is a {subject} teacher for {grade} student, teaching about {title} for {subject} subject."
            prompt_main_intro = f"utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a short brief notes to help your client delivers slide content like this: '{slide_content['slideTitle']}'; ALWAYS INCLUDE THIS QUESTION IN THE NOTE: 'Have you heard of {tech_concept} before? What do you think it means?'. IMPORTANT NOTES: Focus on introducing either the tool or task. Include expected responses for questions. Eliminate repetition. Provide instructions for 'think, pair, share' activity. Introduce design challenge to initiate brainstorming. MAXIMUM {max_words} WORDS. Your client is a {subject} teacher for {grade} student, teaching about {title} for {subject} subject."
            prompt_tech_concept = f"utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a short brief notes to help your client delivers slide content like this: '{slide_content}'; IMPORTANT TO ALWAYS INCLUDE THIS NOTE: 'You may switch out the video here for another video that introduces {tech_concept}'. MAXIMUM {max_words} WORDS. Your client is a {subject} teacher for {grade} student, teaching about {title} for {subject} subject."
            prompt_tech_dive = f"""generate presentation notes for teacher to explaining what the {tech_concept} is, PLEASE Include several example questions for teacher to probing the student.
            Generate several example questions for teacher to ask to student with following guides:
            1. Using Blooms taxonomy 'Applying' in your tone, ask question about application to ask students how to apply the {tech_concept} to their lives.
            2. Using Blooms taxonomy 'Analyzing' in your tone, ask a question to check for understanding of the {tech_concept}, by asking questions where they will have to demonstrate their understanding, e.g. 'Why do we have to show a machine many different images in order to train it?'.
            3. Using Blooms taxonomy 'Applying' in your tone, ask a question which require student to apply what they have just learnt to a new context.
            IMPORTANT: ALWAYS INCLUDE THE EXAMPLE QUESTIONS.
            NOTES: Improve clarity and specificity in writing. Avoid generalizations and repetition. Specify different political scenarios. Provide precise instructions for teachers to guide students effectively. Ensure alignment between instructions and content. Introduce relevant terms and functions. Ensure slide content serves a purpose and is not generic. Include examples for clarity and guidance. Eliminate slides that do not contribute to the presentation's objectives."""
            prompt_software_intro = f"utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a short brief notes to help your client delivers this slide content: '{slide_content['slideTitle']}'. IMPORTANT TO INCLUDE: 'Possible questions to ask: 'What do you think we’re using this software to do today?''. Ensure alignment between teacher and slide notes. Increase specificity to match the lesson content. Ensure explanations match slide content. Avoid generic slides; provide specific details."
            prompt_software_features = f"""utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a short brief notes to help your client delivers this slide content: '{slide_content['slideTitle']}';
            PLEASE ALWAYS include several example questions for teacher to probing the students, like these:
            'Why do you think it’s important to have [the software feature] as part of the software?',
            'How do you think [the software feature] will help us in our design challenge today?'
            CHANGE THE FEATURE ACCORDING TO EACH SOFTWARE FEATURES PRESENTED IN THE SLIDE.
            IMPORTANT NOTES: Enhance clarity and accuracy in prompting students to create a wireframe for app planning, ensuring a clear understanding of the app's appearance and information flow.
            Address vagueness and scientific inaccuracies with improved wording. Provide more scaffolding throughout, particularly in the last point. Include specific examples and teacher notes to illustrate concepts effectively. Avoid generic content and repetition, instead offering precise instructions and examples. Provide detailed guidance on facilitating activities, including specific steps and suggestions for guiding students. Introduce scaffolding techniques such as storyboarding or guiding questions to aid learners in developing their ideas effectively.
            Offer a step-by-step guide for teachers to assist students in meeting the objectives."""
            prompt_model_example = f"explain this slide content to the students: '{slide_content['slideTitle']}'; PLEASE elaborate on what the teacher should do here, e.g. 'Teacher to open Google Teachable Machine in a browser window and model an example according to the following steps: <<insert detailed steps here>>.'. YOU NEED TO PROVIDE DETAILED STEPS."
            prompt_consolidation = f"utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a short brief notes (MAXIMUM 50 WORDS, SHOULD BE DIFFERENT FROM THE SLIDE CONTENT) to help your client delivers slide content like this: '{slide_content}'; PLEASE ALSO affirm students for their hard work in completing the project/design challenge."
            prompt_reflection = f"utilizing '{bloom_result}' bloom taxonomy in your tone, please generate a detailed notes (MAXIMUM 50 WORDS, SHOULD BE DIFFERENT FROM THE SLIDE CONTENT) to help your client delivers this slide content: '{slide_content}'; IMPORTANT: In one point among the notes, there should be the probing section, where it should include some sample of question for teacher to ask the students ALSO example question from student to teachers AND possible answer from teacher. So, pretend as you are a student asking further explanation to the teacher."
            prompt_design_challenge = f"utilizing '{bloom_result}' bloom taxonomy in your tone. Generate detailed slide notes to help your client delivers this slide content: '{slide_content['slideTitle']}. Ensure pointers are relevant to the design challenge. Provide specific details about the activity, including numerical problems for students to solve. For context, the design challenge is: '{challenge}'"

            if slide_number in selected_slides and slide_number not in ['Slide 3', next_slide_main, slide_number_tech, slide_number_consolidation, slide_number_reflection, slide_number_design, slide_number_exploration1, slide_number_exploration2, slide_number_software_intro, slide_model_example]:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content. Use the given bloom verb.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": description,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_question

            elif slide_number == slide_model_example:
                function_notes = [{
                    "name": "create_reflection_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": """This notes should elaborate on what the teacher should do here, e.g. 'Teacher to open Google Teachable Machine in a browser window and model an example according to the following steps: <<insert detailed steps here>>.'.
                                YOU NEED TO PROVIDE DETAILED STEPS. Write this notes as you are guiding the teacher on how to use the software, provide detailed steps.""",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_model_example

            elif slide_number == slide_number_reflection:
                function_notes = [{
                    "name": "create_reflection_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": """MAXIMUM 50 WORDS. This notes should facilitate a discussion around the reflections section. Allow students to provide responses to the reflection question.
                                IMPORTANT: PLEASE Include several example questions for teacher to probing the student responses, ALSO several possible questions FROM students asking the teacher regarding the teachers reflection questions, AND INCLUDE nclude the possible answer for that student question.""",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_reflection

            elif slide_number == slide_number_tech:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content. Use the given bloom verb.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": description,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_tech_concept

            elif slide_number == slide_number_design:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content. Use the given bloom verb.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": description,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_design_challenge
            elif slide_number == next_slide_main:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content. Use the given bloom verb.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": description,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_main_intro
            elif slide_number in [slide_number_exploration1, slide_number_exploration2]:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content. Use the given bloom verb. INCLUDE EXAMPLE QUESTIONS",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": description,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_tech_dive

            elif slide_number == slide_number_software_intro:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content. Use the given bloom verb.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": description,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_software_intro

            elif slide_number == slide_number_consolidation:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content. Use the given bloom verb.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": description,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_consolidation
            elif slide_number == 'Slide 3':
                function_notes = [{
                    "name": "create_trigger_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": """MAXIMUM 50 WORDS. This notes should facilitate a discussion around the trigger question. Allow students to provide responses to the trigger question.
                                IMPORTANT: PLEASE Include several example questions for teacher to probing the student responses, ALSO several possible questions FROM students asking the teacher regarding the teachers trigger questions, AND INCLUDE nclude the possible answer for that student question.
                                ONE OF THE NOTES SHOULD INCLUDE THIS KIND OF NOTES, ADJUST THE QUESTION ALIGN TO THE TOPIC, EXAMPLE: 'Probe students responses to promote deeper thinking. For example, if students say “One hamburger is an example of a fraction as it represents one whole”, teacher might respond by asking “OK, so what happens if you divide the hamburger equally between four friends?”'
                                """,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_trigger
            else:
                description = notes_description
                function_notes = [{
                    "name": "create_slide_notes",
                    "description": f"You are an assistant for {subject} teacher for {grade} student, create the notes for teacher regarding the given presentation slide content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "slideNotes": {
                                "type": "array",
                                "description": notes_description_no_question,
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "slideNotes"
                        ]
                    }
                }]
                prompt = prompt_non_question

            print(f"Generating notes for {slide_number}...")
            # Run code to generate notes for the slide
            notesCompletion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system",
                        "content": f"Act as an assistant for {subject} teacher {grade} student. USE BLOOM VERB: '{bloom_result}'. Help the teacher to deliver their presentation by giving ONLY IMPORTANT slide notes (MAXIMUM 3 NOTES). Answer in JSON"
                    },
                    {
                        "role": "user",
                        "content": f"""Imagine three different experts are answering this challenge.
                        All experts will write down 1 step of their thinking,
                        then share it with the group.
                        Then all experts will go on to the next step, etc.
                        If any expert realises they're wrong at any point then they leave.
                        The challenge is to {prompt}"""
                    },
                ],
                response_format={"type": "json_object"},
                functions=function_notes,
                max_tokens=4096,
                temperature=0.9,
                presence_penalty=0.8,
                top_p=0.8
            )

            # Extract the generated notes
            output_notes = notesCompletion.choices[0].message.function_call.arguments
            content_prompt += notesCompletion.usage.prompt_tokens
            content_completion += notesCompletion.usage.completion_tokens
            notes = json.loads(output_notes).get('slideNotes', {})

            # Append the generated notes to the corresponding slide's 'slideNotes' field
            slide_content['slideNotes'] = notes

    print("Done creating content and notes")

    return output_data

def generate_examples(software, output_data, gen_tech_domain, grade):
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

    function_code_example = [{
        "name": "generate_code_example",
        "description": "From given presentation slides, gives a sample code on to solve the slide problem.",
        "parameters": {
            "type": "object",
            "properties": {
                "example": {
                "type": "string",
                "description": """Write your sample code in CODE BLOCK FORMAT, which started with 3 backticks (```) and also ended with 3 backticks (```), therefore your code can be read as a CODE BLOCK. ONLY WRITE THE CODE.
                for example:
                    ```for (let i = 0; i < 5; i++) {\n  console.log('Hello, World!');\n} ```
                    """
                },
            },
            "required": [
                "example"
            ]
        }
    }]

    function_non_code_example = [{
        "name": "generate_code_example",
        "description": "From given presentation slides, gives a example on how to utilize the software to solve the problem.",
        "parameters": {
            "type": "object",
            "properties": {
                "example": {
                "type": "string",
                "description": "Write your example guide clear and systematically, so student can follow your instructions."
                },
            },
            "required": [
                "example"
            ]
        }
    }]

    # Mapping of tech domains to prompts
    coding_tech_domains = ["App Development", "Artificial Intelligence", "Programming & Coding"]
    non_coding_tech_domains = ["Design & Simulation", "Extended Reality (AR/VR/MR)", "Multimedia and Animation"]

    # Function to select appropriate prompts based on tech domain
    def select_functions(tech_domain):
        if gen_tech_domain in coding_tech_domains:
            return function_finding_coding
        elif gen_tech_domain in non_coding_tech_domains:
            return function_finding_non_coding
        else:
            raise ValueError("Invalid tech domain")

    function_finding = select_functions(gen_tech_domain)

    if gen_tech_domain in coding_tech_domains:
        slide_instruction = output_data['main_activity']
        tryCompletion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional education assessor. If the lesson is about programming, determine which given slides is worth to be given a code example. If the lesson is not about programming, determine which given slides is worth to be given example to use that software. Your output can be multiple slides, write the slides number exactly like this format, e.g. 'Slide 14', 'Slide 16'"
                    },
                    {
                        "role": "user",
                        "content": f"Which slide should be given code example from these slides: {slide_instruction}."
                    },
                ],
                functions=function_finding,
                max_tokens=4096,
                temperature=0.9,
                presence_penalty=0.8,
                top_p=0.8
            )

        selected_slides = tryCompletion.choices[0].message.function_call.arguments

    else:
        slide_instruction = output_data['main_activity']
        tryCompletion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional education assessor. If the lesson is about programming, determine which given slides is worth to be given a code example. If the lesson is not about programming, determine which given slides is worth to be given example to use that software. Your output can be multiple slides, write the slides number exactly like this format, e.g. 'Slide 14', 'Slide 16'"
                    },
                    {
                        "role": "user",
                        "content": f"Which slide should be given use case example from these slides: {slide_instruction}. It can be more than one slides"
                    },
                ],
                functions=function_finding,
                max_tokens=4096,
                temperature=0.9,
                presence_penalty=0.8,
                top_p=0.8
            )

        selected_slides = tryCompletion.choices[0].message.function_call.arguments

    def select_code_example_slides(main_activity_data, selected_slides):
        code_example_slides = []

        selected_slide = json.loads(selected_slides)['selected slide']
        if selected_slide in main_activity_data:
            code_example_slides.append(selected_slide)

        return code_example_slides

    selected_code_example_slides = select_code_example_slides(output_data['main_activity'], selected_slides)

    slide_content_back = output_data['main_activity'][selected_code_example_slides[0]]['slideContent']

    # Loop through selected slides and generate code examples
    for slide_number in selected_code_example_slides:
        output_data['main_activity'][slide_number]['slideContent'] = slide_content_back
        slide_data = output_data['main_activity'][slide_number]
        slide_instruction = slide_data['slideContent'] if slide_data['slideContent'] else slide_data['slideNotes']

        # Define prompts for each category
        system_prompt_coding = "You are a professional personal programming tutor in class. Write example code for given slide instructions to help students understand your topic. ANSWER DIRECTLY, do not add your response, avoid this: 'Sure! Here's a detailed example on how to operate the software according to the given instructions'"
        system_prompt_non_coding = "You are a professional instructor in class. Write detailed example on how to operate the software (creating design, etc.) for given slide instructions to help students understand your topic. ANSWER DIRECTLY, do not add your response, avoid this: 'Sure! Here's a detailed example on how to operate the software according to the given instructions'"
        user_prompt_coding = f"You are a {grade} programming teacher. Write the code example IN CODE BLOCK FORMAT (```) to solve this slide problem: '{slide_instruction}'. Remember to ONLY WRITE the code, not run it. REMEMBER TO ADD BACKTICK (```) IN YOUR CODE EXAMPLE. ANSWER DIRECTLY, do not add your response, avoid this kind of tone: 'Sure! Here's a detailed example on how to operate the software according to the given instructions'"
        user_prompt_non_coding = f"Write the detailed example on how to utilize the {software[0]} (creating design, etc.) to solve this slide problem: '{slide_instruction}'. ANSWER DIRECTLY, use tone as you are talking to your student. You example should be clearn and systematically"

        # Function to select appropriate prompts based on tech domain
        def select_prompts(gen_tech_domain):
            if gen_tech_domain in coding_tech_domains:
                return system_prompt_coding, user_prompt_coding, function_code_example
            elif gen_tech_domain in non_coding_tech_domains:
                return system_prompt_non_coding, user_prompt_non_coding, function_non_code_example
            else:
                raise ValueError("Invalid tech domain")

        # Determine tech domain and select prompts
        example_system_prompt, example_user_prompt, function_example = select_prompts(gen_tech_domain)

        codeCompletion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "system",
                    "content": example_system_prompt
                },
                {
                    "role": "user",
                    "content": example_user_prompt
                },
            ],
            functions=function_example,
            max_tokens=4096,
            temperature=1,
            presence_penalty=0.8,
            top_p=0.8
        )
        output_content = codeCompletion.choices[0].message.function_call.arguments
        output_code = json.loads(output_content).get('example',{})

        def add_empty_slide_example(output_data):
            for activity, slides in output_data.items():
                for slide, details in slides.items():
                    details['slideExample'] = ''

        add_empty_slide_example(output_data)

        def append_code_to_slides(output_data, selected_code_example_slides, output_code):
            for activity, slides in output_data.items():
                for slide, details in slides.items():
                    if slide in selected_code_example_slides:
                        details['slideExample'] = output_code
        append_code_to_slides(output_data, selected_code_example_slides, output_code)

    for activity_type, activity_data in output_data.items():
        for slide_name, slide_data in activity_data.items():
            if slide_name in selected_code_example_slides and 'slideExample' in slide_data and gen_tech_domain in coding_tech_domains:
                slide_example = slide_data['slideExample']
                if not slide_example.startswith("```") and not slide_example.endswith("```"):
                    slide_data['slideExample'] = f"```\n{slide_data['slideExample']}\n```"

    return output_data

def generate_images(subject, grade, software, output_data):
    image_prompt_tokens = 0
    image_completion_tokens = 0
    function_keywords = [
        {
            "name": "determine_keywords",
            "description": "Act as a professional DALL-E artist, you need to determine appropriate prompt to represent the presentation content into image.",
            "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                "type": "string",
                "description": "The prompt should be in instruction tone WITHOUT mentioning the software, e.g. 'Create an image illustrating students exploring statistics and probability concepts'. IMPORTANT: The prompt objective should be to generate object rather than activities."
                },
            },
            "required": [
                "keywords"
            ]
        }
        }]

    function_image = [{
        "name": "determine_slide_image",
        "description": f"You are an advisor for {subject} teacher for {grade} student, determine which slide is suitable to be given images. Answer only 'Yes' or 'No.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": f"Answer only 'Yes' or 'No'. Determine is the given slide content should be add some images for better student understanding",
                },
                "amount": {
                    "type": "string",
                    "description": f"Answer only the amount in integer. If the slide content is relevant for images, determine how many images could be shown in the slide. Please consider the length of the slide content, if the content is too long, therefore only give 1 image. MAXIMUM 3 IMAGES.",
                }
            },
            "required": [
                "answer", "amount"
            ]
        }
    }]

    def upload_image(image_data, slide_number):
        url = "https://builder-api.eddy4teachers.com/api/upload"
        files = {'file': (f'{slide_number}.png', image_data, 'image/png')}
        response = requests.post(url, files=files)
        if response.status_code == 200:
            return response.json().get('data')
        else:
            return None

    def generate_ai_image(prompt, negative_prompt=None, guidance_scale=10, width=1024, height=1024, size='square_hd', num_inference_steps=15, num_images=1, seed=30, freepik_api_key=None, retry=0):
        max_retry=3
        url = "https://api.freepik.com/v1/ai/text-to-image"

        headers = {
            'Accept-Language': 'en-US',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Freepik-API-Key': freepik_api_key
        }

        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "request_content_styling": {
                "guidance_scale": guidance_scale
            },
            "request_content_image": {}
        }

        if width:
            data["request_content_image"]["width"] = width
        if height:
            data["request_content_image"]["height"] = height
        if size:
            data["request_content_image"]["size"] = size
        if seed:
            data["seed"] = seed

        data["num_inference_steps"] = num_inference_steps
        data["num_images"] = num_images

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            if retry < max_retry:  # Check if retry is less than max_retry
                print("Rate limit exceeded. Waiting for 15 seconds before retrying...")
                for i in tqdm(range(15), desc="Waiting", unit="sec"):
                    time.sleep(1)
                new_num_inference_steps = random.randint(num_inference_steps, 50)
                new_seed = random.randint(0, 1000000)
                print(f"Retrying now with inference {new_num_inference_steps} and seed {new_seed}...")
                # Increment retry count and pass it to the recursive call
                retry += 1
                return generate_ai_image(prompt, negative_prompt, guidance_scale, width, height, size, new_num_inference_steps, num_images, new_seed, freepik_api_key, retry)
            else:
                print(f"Error: {response.status_code}. Rate limit exceeded, could not generate images.")
                return None
        else:
            print("Error:", response.status_code)
            return None

    def is_blank_image(image):
        """
        Check if the image is blank (completely black).
        """
        return image.getbbox() is None

    def add_empty_slide_image(output_data):
        for activity, slides in output_data.items():
            for slide, details in slides.items():
                details['slideImage'] = ['']

    add_empty_slide_image(output_data)

    # Assuming 'output_data' contains your slides' data
    for activity_key in ['opening_activity', 'main_activity', 'closing_activity']:
        max_retry_all = 3
        retry_all = 0
        
        if activity_key in output_data:  # Check if the key exists in output_data
            activity_data = output_data[activity_key]
            # Determine the first slide number for 'main_activity'
            first_slide_number = next((slide_number for slide_number in activity_data.keys() if slide_number != 'Slide 1'), None)
            # Get the rest of the first 4 slides in the main activity
            if first_slide_number is not None:
                main_activity_slide_numbers = [f"Slide {n}" for n in range(int(first_slide_number.split()[1]) + 1, int(first_slide_number.split()[1]) + 4)]
                
            for slide_number, slide_content in activity_data.items():
                start_time = time.time()
                print(f"Checking {slide_number}...")

                if slide_number == 'Slide 1':
                    response = {'answer': 'Yes', 'amount': '1'}
                elif slide_number in main_activity_slide_numbers or activity_key in ['opening_activity', 'closing_activity']:
                    imageCompletion = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        messages=[
                            {
                                "role": "system",
                                "content": f"Act as an advisor for {subject} teacher {grade} student. You need to determine which slide is suitable to be given images. Answer only 'Yes' or 'No. Answer in JSON"
                            },
                            {
                                "role": "user",
                                "content": f"Consider the following content for slide {slide_number}: '{slide_content}'; Given the length and complexity of this content, decide if images should be added to enhance the slide. If images are recommended, specify how many would be ideal (up to 3), considering that overly complex slides might not benefit from additional images. Yor answer example: 'answer': 'Yes','amount': '2'"
                            },
                        ],
                        response_format={"type": "json_object"},
                        functions=function_image,
                        max_tokens=4096,
                        temperature=0.9,
                        presence_penalty=0.8,
                        top_p=0.8
                    )

                    # Extract the response indicating if a question should be given
                    response = json.loads(imageCompletion.choices[0].message.function_call.arguments)
                    image_prompt_tokens += imageCompletion.usage.prompt_tokens
                    image_completion_tokens += imageCompletion.usage.completion_tokens
                else:
                    response = {'answer': 'No', 'amount': '0'}

                print(response)

                if response['answer'] == 'Yes':
                    # Determine keywords for the slide content here (use another OpenAI completion or your own logic)
                    if slide_number in ['Slide 1']:
                        slide_content = slide_content['slideTitle']
                    else:
                        slide_content = slide_content['slideContent']

                    if not slide_content:
                        continue

                    imageKeywordsCompletion = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a great DALL-E prompt artist. Determine prompt for DALL-E that represent the presentation content into images"
                            },
                            {
                                "role": "user",
                                "content": f"""Imagine three different experts are answering this challenge.
                            All experts will write down 1 step of their thinking,
                            then share it with the group.
                            Then all experts will go on to the next step, etc.
                            If any expert realises they're wrong at any point then they leave.
                            The challenge is to generate a playful DALL-E INSTRUCTION prompt that will produce an image to represent this presentation slide as an image: '{slide_content}'. IMPORTANT: AVOID MENTIONING {software[0]}. It is important to make sure the prompt tone is instructional""",
                            },
                        ],
                        functions=function_keywords,
                        max_tokens=4000,
                        temperature=0.5,
                        presence_penalty=0.6,
                        top_p=0.8,
                    )

                    output_content = imageKeywordsCompletion.choices[0].message.function_call.arguments
                    keywords = json.loads(output_content).get('keywords', {})
                    image_prompt_tokens += imageKeywordsCompletion.usage.prompt_tokens
                    image_completion_tokens += imageKeywordsCompletion.usage.completion_tokens

                    print(f'{slide_number} prompt: {keywords}')

                    # Example usage:
                    prompt = keywords
                    negative_prompt = "b&w, grayscale, disfigured, bad quality"

                    while True:
                        seed = random.randint(0, 1000000)
                        generated_image = generate_ai_image(prompt, negative_prompt, seed=seed, freepik_api_key=freepik_api_key)

                        if generated_image and 'data' in generated_image and generated_image['data']:
                            # Assuming only one image is generated
                            image_data_base64 = generated_image['data'][0]['base64']

                            # Decode base64 data
                            image_data = base64.b64decode(image_data_base64)

                            # Display the image using Matplotlib
                            img = Image.open(BytesIO(image_data))
                            if not is_blank_image(img):
                                image_name = f"{slide_number}".replace(' ', '_')
                                image_url = upload_image(image_data, image_name)
                                output_data[activity_key][slide_number]['slideImage'] = image_url
                                print(f"Image URL for {slide_number}: {image_url}")
                                break
                            else:
                                if retry_all <= max_retry_all:
                                    print("Generated image is blank. Retrying with a new seed.")
                                    retry_all += 1
                                else:
                                    print("Could not generate image at this time")
                                break
                        else:
                            if retry_all <= max_retry_all:
                                print("No image data found in the response. Retrying...")
                                retry_all += 1
                            else:
                                print("Could not generate image at this time")
                                break

                end_time = time.time()
                elapsed_time = end_time - start_time
                print("Time taken to generate image:", elapsed_time, "seconds")
    return output_data

def generate_response(topic, subject, grade, student_profile, gen_tech_domain, software, tech_domain, recommendations, LP, domain_list, max_retry=5):
    def retry_function(func, *args, **kwargs):
        for _ in range(max_retry):
            try:
                result = func(*args, **kwargs)
                print(f"{func.__name__} executed successfully.")
                return result
            except Exception as e:
                print(f"Error in {func.__name__}: {e}. Retrying...")
                continue
        raise RuntimeError(f"Maximum retries exceeded for {func.__name__}. Unable to generate response.")

    print(F"Generating LP{LP}...")
    topic, software, gen_tech_domain, system_prompt, subject, title, recommendations, gen_tech_domain, LP, domain_list = retry_function(generate_intro, topic, subject, grade, student_profile, tech_domain, software, gen_tech_domain, recommendations, LP, domain_list)
    print(f"Software used: {software[0]}")
    key_concepts = retry_function(generate_key_concepts, topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, title)
    prior_knowledge = retry_function(generate_prior_knowledge, topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts)
    objectives = retry_function(generate_objectives, topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge)
    outcomes = retry_function(generate_outcomes,topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives)
    real_world_application = retry_function(generate_real_world_application, topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives, outcomes)
    lesson_overview = retry_function(generate_lesson_overview, topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives, outcomes, real_world_application)
    summary = retry_function(generate_lesson_summary, subject, grade, system_prompt, lesson_overview, title)
    pre_lesson_preparation = retry_function(generate_pre_lesson_preparation,topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, lesson_overview)
    troubleshooting = retry_function(generate_troubleshooting,topic, subject, grade, software, system_prompt, lesson_overview, title)
    opening_activity_complete, system_slide, next_slide_main, challenge, requirements, design_objectives = retry_function(generate_opening,topic, subject, grade, student_profile, gen_tech_domain, software, lesson_overview, key_concepts, title)
    main_activity_complete, next_slide_closing, tech_concept, slide_number_design, next_slide_main, slide_model_example,  slide_number_exploration1, slide_number_exploration2, slide_number_software_intro, slide_model_example, slide_number_tech = retry_function(generate_main,topic, subject, grade, software, next_slide_main, title, challenge, design_objectives, lesson_overview)
    closing_activity, slide_number_consolidation, slide_number_reflection = retry_function(generate_closing,next_slide_closing, grade, software, topic, challenge, tech_concept)
    output_data = retry_function(generate_detailed_slide, opening_activity_complete, main_activity_complete, closing_activity, lesson_overview, grade, system_slide, topic, subject, student_profile, title, software, slide_number_design, next_slide_main, slide_number_consolidation, slide_number_reflection, tech_concept,  slide_number_exploration1, slide_number_exploration2, slide_number_software_intro, slide_model_example, slide_number_tech, challenge)
    complete_slide = retry_function(generate_examples, software, output_data, gen_tech_domain, grade)
    slide_with_image = retry_function(generate_images, subject, grade, software, complete_slide)
    assessment_rubric = retry_function(generate_assessment, topic, subject, grade, student_profile, gen_tech_domain, software, system_prompt, key_concepts, prior_knowledge, objectives, outcomes, real_world_application, lesson_overview, pre_lesson_preparation, title, requirements, tech_concept)
   
    # store the main body and the slides of the lesson plan into a dictionary
    model_response_dict = {
        "summary": summary,
        "topic": title,
        "grade": grade,
        "subject": subject,
        "tech_domain": gen_tech_domain,
        "software": software,
        "key_concepts": key_concepts,
        "prior_knowledge" : prior_knowledge,
        "objectives" : objectives,
        "outcomes" : outcomes,
        "real_world_application" : real_world_application,
        "lesson_overview" : lesson_overview,
        "pre_lesson_preparation" : pre_lesson_preparation,
        "troubleshooting" : troubleshooting,
        "assessment" : assessment_rubric,
        "detailed_slides" : slide_with_image,
    }
    
    # return the dictionary that contains all the section of the lesson plan
    return model_response_dict, recommendations, gen_tech_domain, domain_list
