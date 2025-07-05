import re
from docx import Document
import PyPDF2
import streamlit as st
from .country_config import get_country_config, get_gpa_input_config, COUNTRY_CONFIG

class CVExtractor:
    """Extracts information from uploaded CV/Resume files with role-specific optimization"""
    
    def __init__(self):
        self.role_specific_fields = {
            'student': {
                'required': ['name', 'email', 'education', 'gpa', 'major', 'graduation_year'],
                'optional': ['projects', 'internships', 'extracurricular', 'coursework', 'awards'],
                'cv_fields': ['education', 'projects', 'coursework', 'awards', 'extracurricular'],
                'app_fields': ['name', 'email', 'gpa', 'major', 'graduation_year', 'internships']
            },
            'entrepreneur': {
                'required': ['name', 'email', 'business_experience', 'ventures', 'skills'],
                'optional': ['funding_history', 'team_size', 'revenue', 'market_focus', 'achievements'],
                'cv_fields': ['business_experience', 'ventures', 'achievements', 'skills'],
                'app_fields': ['name', 'email', 'funding_history', 'team_size', 'revenue', 'market_focus']
            },
            'researcher': {
                'required': ['name', 'email', 'education', 'research_area', 'publications'],
                'optional': ['grants', 'conferences', 'collaborations', 'methodologies', 'impact_factor'],
                'cv_fields': ['education', 'publications', 'grants', 'conferences', 'research_area'],
                'app_fields': ['name', 'email', 'collaborations', 'methodologies', 'impact_factor']
            },
            'artist': {
                'required': ['name', 'email', 'medium', 'style', 'portfolio_url'],
                'optional': ['exhibitions', 'awards', 'collections', 'techniques', 'inspiration'],
                'cv_fields': ['exhibitions', 'awards', 'collections', 'portfolio_url'],
                'app_fields': ['name', 'email', 'medium', 'style', 'techniques', 'inspiration']
            },
            'nonprofit': {
                'required': ['name', 'email', 'organization', 'mission', 'impact_area'],
                'optional': ['beneficiaries', 'programs', 'partnerships', 'funding_sources', 'outcomes'],
                'cv_fields': ['organization', 'programs', 'partnerships', 'outcomes'],
                'app_fields': ['name', 'email', 'mission', 'impact_area', 'beneficiaries', 'funding_sources']
            }
        }
    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""

    def extract_text_from_docx(self, docx_file):
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""

    def extract_profile_info(self, text):
        profile = {}
        name_patterns = [
            r'^([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Name:?\s*([A-Z][a-z]+ [A-Z][a-z]+)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                profile['name'] = match.group(1)
                break
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            profile['email'] = email_match.group()
        phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{10,}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            profile['phone'] = phone_match.group()
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'diploma', 'certificate']
        education_text = []
        for line in text.split('\n'):
            if any(keyword in line.lower() for keyword in education_keywords):
                education_text.append(line.strip())
        profile['education'] = '\n'.join(education_text[:5])
        gpa_patterns = [
            r'GPA:?\s*([0-4]\.\d+)',
            r'Grade Point Average:?\s*([0-4]\.\d+)',
            r'CGPA:?\s*([0-4]\.\d+)'
        ]
        for pattern in gpa_patterns:
            gpa_match = re.search(pattern, text, re.IGNORECASE)
            if gpa_match:
                profile['gpa'] = gpa_match.group(1)
                break
        skills_section = re.search(r'(?:SKILLS?|TECHNICAL SKILLS|COMPETENCIES|PROFESSIONAL SKILLS)[\s:]*\n((?:.*\n){1,10})', text, re.IGNORECASE | re.MULTILINE)
        if skills_section:
            profile['skills'] = skills_section.group(1).strip()
        experience_keywords = ['experience', 'employment', 'work history', 'professional', 'internship']
        experience_text = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in experience_keywords):
                experience_text.extend(lines[i:i+3])
        profile['experience'] = '\n'.join(experience_text[:10])
        achievement_keywords = ['award', 'achievement', 'honor', 'recognition', 'certificate']
        achievement_text = []
        for line in text.split('\n'):
            if any(keyword in line.lower() for keyword in achievement_keywords):
                achievement_text.append(line.strip())
        profile['achievements'] = '\n'.join(achievement_text[:5])
        field_patterns = [
            r'(?:major|field|degree|study)(?:ed|ing)?\s*(?:in|of)?\s*:?\s*([^.]+)',
        ]
        
        field_of_study = "Not specified"
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                field_of_study = match.group(1).strip()
                break
        
        profile['field_of_study'] = field_of_study
        return profile

    def get_role_specific_form(self, role, existing_profile=None, country='United States'):
        """Generate role-specific profile form with country awareness"""
        if existing_profile is None:
            existing_profile = {}
            
        role_config = self.role_specific_fields.get(role, self.role_specific_fields['student'])
        country_config = get_country_config(country)
        profile_data = {}
        
        st.subheader(f"📝 {role.title()} Profile - {country}")
        st.write(f"Please fill out your {role} information below:")
        
        # Country selection
        profile_data['country'] = st.selectbox(
            "🌍 Country",
            options=list(COUNTRY_CONFIG.keys()),
            index=list(COUNTRY_CONFIG.keys()).index(country) if country in COUNTRY_CONFIG else 0,
            help="Select your country for localized requirements"
        )
        
        # Required fields
        st.write("**Required Information:**")
        for field in role_config['required']:
            field_label = field.replace('_', ' ').title()
            if field == 'email':
                profile_data[field] = st.text_input(
                    f"📧 {field_label}", 
                    value=existing_profile.get(field, ''),
                    placeholder="your.email@example.com"
                )
            elif field == 'gpa' and role == 'student':
                # Simple GPA scale selection
                col1, col2 = st.columns(2)
                
                with col1:
                    gpa_scale_type = st.selectbox(
                        "📊 GPA Scale", 
                        options=["4.0 Scale", "5.0 Scale", "Other"],
                        help="Select your country's GPA scale"
                    )
                
                with col2:
                    if gpa_scale_type == "4.0 Scale":
                        max_gpa, help_text = 4.0, "US/UK style GPA (0.0-4.0)"
                    elif gpa_scale_type == "5.0 Scale":
                        max_gpa, help_text = 5.0, "Uganda/Nigeria style GPA (0.0-5.0)"
                    else:
                        max_gpa, help_text = 10.0, "Other scale (0.0-10.0 or percentage)"
                    
                    profile_data[field] = st.number_input(
                        f"📊 {field_label}", 
                        min_value=0.0, 
                        max_value=max_gpa, 
                        value=float(existing_profile.get(field, 0.0)),
                        step=0.1,
                        help=help_text
                    )
                
                # Store the scale type for context
                profile_data['gpa_scale'] = gpa_scale_type
                    
            elif field == 'graduation_year' and role == 'student':
                profile_data[field] = st.number_input(
                    f"🎓 {field_label}", 
                    min_value=2020, max_value=2030,
                    value=int(existing_profile.get(field, 2025))
                )
            elif field == 'phone':
                phone_format = country_config.get('phone_format', '+XXX XXX XXX XXXX')
                profile_data[field] = st.text_input(
                    f"📱 {field_label}", 
                    value=existing_profile.get(field, ''),
                    placeholder=phone_format,
                    help=f"Format: {phone_format}"
                )
            elif field == 'portfolio_url' and role == 'artist':
                profile_data[field] = st.text_input(
                    f"🎨 {field_label}", 
                    value=existing_profile.get(field, ''),
                    placeholder="https://your-portfolio.com"
                )
            else:
                profile_data[field] = st.text_input(
                    f"✏️ {field_label}", 
                    value=existing_profile.get(field, ''),
                    help=self.get_field_help(field, role, country)
                )
        
        # Optional fields
        with st.expander("➕ Optional Information (Recommended)", expanded=False):
            for field in role_config['optional']:
                field_label = field.replace('_', ' ').title()
                if field in ['team_size', 'beneficiaries']:
                    profile_data[field] = st.number_input(
                        f"👥 {field_label}", 
                        min_value=0,
                        value=int(existing_profile.get(field, 0))
                    )
                elif field in ['revenue', 'funding_history']:
                    profile_data[field] = st.text_input(
                        f"💰 {field_label}", 
                        value=existing_profile.get(field, ''),
                        placeholder="e.g., $50,000 raised"
                    )
                else:
                    profile_data[field] = st.text_area(
                        f"📄 {field_label}", 
                        value=existing_profile.get(field, ''),
                        height=100,
                        help=self.get_field_help(field, role, country)
                    )
        
        # Show country-specific scholarship info
        if country != 'Other':
            with st.expander(f"💡 {country} Scholarship Tips", expanded=False):
                common_scholarships = country_config.get('common_scholarships', [])
                if common_scholarships:
                    st.write("**Common scholarship types in your country:**")
                    for scholarship in common_scholarships:
                        st.write(f"• {scholarship}")
        
        return profile_data
    
    def get_field_help(self, field, role, country='United States'):
        """Get help text for specific fields"""
        help_texts = {
            'student': {
                'major': 'Your field of study (e.g., Computer Science, Biology)',
                'projects': 'Academic or personal projects you\'ve worked on',
                'extracurricular': 'Clubs, sports, volunteer work, leadership roles',
                'coursework': 'Relevant courses that showcase your expertise'
            },
            'entrepreneur': {
                'ventures': 'Businesses or startups you\'ve founded or co-founded',
                'market_focus': 'Industries or markets you operate in',
                'achievements': 'Key milestones, awards, or recognition received'
            },
            'researcher': {
                'research_area': 'Your field of research and specialization',
                'methodologies': 'Research methods and techniques you use',
                'impact_factor': 'Citation count, h-index, or research impact metrics'
            },
            'artist': {
                'medium': 'Your artistic medium (painting, sculpture, digital, etc.)',
                'techniques': 'Specific artistic techniques or methods you use',
                'inspiration': 'What inspires your artistic work'
            },
            'nonprofit': {
                'impact_area': 'Social causes or areas your organization focuses on',
                'outcomes': 'Measurable results or impact of your work'
            }
        }
        
        return help_texts.get(role, {}).get(field, '')
    
    def filter_profile_data(self, profile_data, role, for_cv=True):
        """Filter profile data for CV or application use"""
        role_config = self.role_specific_fields.get(role, self.role_specific_fields['student'])
        
        if for_cv:
            # Data for CV template
            relevant_fields = role_config['cv_fields']
        else:
            # Data for application forms
            relevant_fields = role_config['app_fields']
        
        filtered_data = {}
        for field in relevant_fields:
            if field in profile_data and profile_data[field]:
                filtered_data[field] = profile_data[field]
        
        return filtered_data