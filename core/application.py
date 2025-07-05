import json
from datetime import datetime
import google.generativeai as genai
import streamlit as st

class ApplicationGenerator:
    """Generates personalized application documents"""
    def __init__(self, api_manager, user_id):
        self.api_manager = api_manager
        self.user_id = user_id
        self.model = None

    def initialize_model(self, api_key):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            return True
        except Exception as e:
            st.error(f"Error initializing AI model: {str(e)}")
            return False

    def generate_application_letter(self, profile, opportunity, user_answers=None, api_key=None, mode='basic'):
        if mode in ['user', 'server'] and api_key:
            if not self.model:
                if not self.initialize_model(api_key):
                    return self.generate_basic_letter(profile, opportunity)
            try:
                prompt = f"""
                You are an expert application writer. Create a professional, tailored application letter for the following opportunity.
                Opportunity Details:
                - Title: {opportunity['title']}
                - Description: {opportunity['description']}
                - Category: {opportunity['category']}
                - Target Audience: {opportunity['target_audience']}
                Applicant Profile:
                - Name: {profile.get('name', 'Applicant')}
                - Education: {profile.get('education', 'Not provided')}
                - GPA: {profile.get('gpa', 'Not provided')}
                - Skills: {profile.get('skills', 'Not provided')}
                - Experience: {profile.get('experience', 'Not provided')}
                - Achievements: {profile.get('achievements', 'Not provided')}
                - Field of Study: {profile.get('field_of_study', 'Not provided')}
                Additional User Answers:
                {json.dumps(user_answers, indent=2) if user_answers else 'None provided'}
                Guidelines:
                - Address the letter to "Selection Committee" unless specified otherwise
                - Highlight how the applicant's background aligns with the opportunity
                - Use a professional tone and structure (header, salutation, body, closing)
                - Keep it concise (300-500 words)
                - Incorporate specific details from the opportunity and profile
                - If user answers are provided, weave them into the narrative
                - Make it compelling and unique
                """
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                st.error(f"Error generating application letter: {str(e)}")
                return self.generate_basic_letter(profile, opportunity)
        else:
            return self.generate_basic_letter(profile, opportunity)

    def generate_basic_letter(self, profile, opportunity):
        name = profile.get('name', 'Applicant')
        date = datetime.now().strftime("%B %d, %Y")
        letter = f"""
        {name}
        {profile.get('email', '')}
        {profile.get('phone', '')}
        {date}
        Selection Committee
        {opportunity['title']}
        Dear Selection Committee,
        I am writing to apply for the {opportunity['title']}. As a {profile.get('field_of_study', 'dedicated individual')}, 
        I am excited about this opportunity to further my goals in {opportunity['category']}.
        My background includes {profile.get('education', 'relevant education')}. 
        I have developed skills in {profile.get('skills', 'various areas')} and have experience 
        in {profile.get('experience', 'relevant fields')}. My achievements include 
        {profile.get('achievements', 'consistent dedication to my goals')}.
        I believe this opportunity aligns with my aspirations to contribute to {opportunity['target_audience']} 
        and make a positive impact. Thank you for considering my application. I look forward to the possibility 
        of contributing to your program.
        Sincerely,
        {name}
        """
        return letter
