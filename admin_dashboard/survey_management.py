import streamlit as st

def show_survey_management():
    st.header("📝 Survey Management")

    # Section for creating a new survey
    with st.expander("✨ Create New Survey"):
        
        # 1. Course Title
        st.write("**1. What is the title of the training course?**")
        course_title = st.text_input("Course Title", placeholder="e.g., Digital Literacy for Educators", label_visibility="collapsed")

        # 2. Target Audience
        st.write("**2. Who is the primary audience for this course? (e.g., middle school teachers, corporate managers, healthcare professionals)**")
        target_audience = st.text_input("Target Audience", placeholder="e.g., Middle school teachers", label_visibility="collapsed")

        # 3. Course Overview
        st.write("**3. Provide a brief overview of the course, describing its primary focus and goals.**")
        course_overview = st.text_area("Course Overview", placeholder="This course introduces essential digital literacy skills...", label_visibility="collapsed")

        # 4. Target Skill Level
        st.write("**4. What is the expected baseline skill level of the trainees? (Choose one)**")
        skill_level = st.selectbox("Target Skill Level", ["Beginner", "Intermediate", "Advanced", "Mixed Level"], label_visibility="collapsed")

        # 5. Key Competency Areas
        st.write("**5. List 3-5 key competencies that the course will cover, focusing on the primary skills or knowledge areas relevant to the course.**")
        competencies = st.text_area("Key Competency Areas", placeholder="e.g., Basic digital literacy concepts\nUse of digital tools in education\nDigital safety and responsible use", label_visibility="collapsed")

        # 6. Learning Outcome Goals
        st.write("**6. What are the primary learning outcomes for this course? List 2-3 specific goals that trainees should achieve by the end.**")
        learning_outcomes = st.text_area("Learning Outcome Goals", placeholder="e.g., Teachers should understand fundamental digital literacy concepts...", label_visibility="collapsed")

        # 7. Expected Application Level
        st.write("**7. Describe the level of understanding or practical application trainees are expected to achieve by the end of the course. (e.g., Familiarity, Understanding, Application, Mastery)**")
        application_level = st.text_input("Expected Application Level", placeholder="e.g., Understanding and Application", label_visibility="collapsed")

        # 8. Known Pain Points or Challenges
        st.write("**8. List any known challenges or pain points that trainees may face in relation to this course content (optional).**")
        pain_points = st.text_area("Known Pain Points or Challenges", placeholder="e.g., Teachers may feel overwhelmed by the fast pace of technology...", label_visibility="collapsed")

        # 9. Course Duration and Structure
        st.write("**9. Provide details about the course structure (e.g., number of sessions, duration per session).**")
        course_duration = st.text_input("Course Duration and Structure", placeholder="e.g., 3 sessions over 1 week, each session lasting 2 hours", label_visibility="collapsed")

        # 10. Number of Survey Questions
        st.write("**10. How many pre-survey questions would you like the AI to generate? (Specify a number)**")
        question_count = st.number_input("Number of Survey Questions", min_value=1, max_value=50, value=10, label_visibility="collapsed")

        # Generate Survey Questions Button
        if st.button("Generate Survey Questions"):
            if course_title and target_audience and course_overview and competencies and learning_outcomes and course_duration:
                # Prepare data for API call
                survey_data = {
                    "courseTitle": course_title,
                    "targetAudience": target_audience,
                    "courseOverview": course_overview,
                    "targetSkillLevel": skill_level,
                    "keyCompetencies": competencies.split("\n"),
                    "learningOutcomes": learning_outcomes.split("\n"),
                    "expectedApplicationLevel": application_level,
                    "knownPainPoints": pain_points.split("\n") if pain_points else None,
                    "courseDuration": course_duration,
                    "questionCount": question_count
                }
                
                questions = generate_survey_questions(survey_data)
                st.success("Survey questions generated successfully!")
                st.write("Generated Questions:")
                for i, question in enumerate(questions, 1):
                    st.write(f"{i}. {question['question']}")
            else:
                st.error("Please fill in all required fields to create a survey.")

    # Section for listing active surveys
    st.subheader("Active Surveys")
    active_surveys = list_active_surveys()  # Get active surveys from the API
    if not active_surveys:
        st.info("No active surveys at the moment.")
    else:
        for survey in active_surveys:
            with st.expander(survey['title']):
                st.write(f"**Context**: {survey['training_context']}")
                st.write(f"**Objectives**: {', '.join(survey['objectives'])}")
                st.write(f"**Target Audience**: {survey['target_audience']}")
                st.write(f"**Number of Questions**: {survey['question_count']}")
                st.write(f"**Status**: {survey['status']}")

                # Option to close survey
                if st.button(f"Close Survey - {survey['title']}"):
                    close_survey(survey['survey_id'])
                    st.success(f"Survey '{survey['title']}' has been closed.")
                    st.experimental_rerun()  # Refresh to update the list of surveys
