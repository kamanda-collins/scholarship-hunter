"""
Country-specific academic and cultural configurations
"""

COUNTRY_CONFIG = {
    'United States': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'US GPA scale (0.0-4.0)',
        'education_terms': ['High School', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+1 (XXX) XXX-XXXX',
        'common_scholarships': ['Pell Grant', 'Merit Scholarships', 'State Grants']
    },
    'United Kingdom': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'UK equivalent GPA (0.0-4.0) or enter First Class/Upper Second',
        'education_terms': ['A-Levels', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+44 XXXX XXXXXX',
        'grading_system': 'First Class/Upper Second/Lower Second/Third Class',
        'common_scholarships': ['Commonwealth Scholarships', 'Chevening']
    },
    'Canada': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Canadian GPA scale (0.0-4.0)',
        'education_terms': ['High School', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+1 (XXX) XXX-XXXX',
        'common_scholarships': ['OSAP', 'Provincial Grants', 'Merit Awards']
    },
    'Australia': {
        'gpa_scale': {'min': 0.0, 'max': 7.0, 'step': 0.1},
        'gpa_help': 'Australian GPA scale (0.0-7.0)',
        'education_terms': ['Year 12', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+61 XXX XXX XXX',
        'grading_system': 'High Distinction/Distinction/Credit/Pass',
        'common_scholarships': ['Australia Awards', 'University Scholarships']
    },
    'Germany': {
        'gpa_scale': {'min': 1.0, 'max': 4.0, 'step': 0.1, 'reverse': True},
        'gpa_help': 'German grade scale (1.0 = best, 4.0 = passing)',
        'education_terms': ['Abitur', 'Bachelor', 'Master', 'Doktor'],
        'phone_format': '+49 XXX XXXXXXX',
        'grading_system': 'sehr gut/gut/befriedigend/ausreichend',
        'common_scholarships': ['DAAD', 'Deutschlandstipendium']
    },
    'France': {
        'gpa_scale': {'min': 0.0, 'max': 20.0, 'step': 0.5},
        'gpa_help': 'French grading scale (0-20, 20 = best)',
        'education_terms': ['Baccalauréat', 'Licence', 'Master', 'Doctorat'],
        'phone_format': '+33 X XX XX XX XX',
        'grading_system': 'Très bien/Bien/Assez bien/Passable',
        'common_scholarships': ['Eiffel Excellence', 'Campus France']
    },
    'India': {
        'gpa_scale': {'min': 0.0, 'max': 10.0, 'step': 0.1},
        'gpa_help': 'Indian CGPA scale (0.0-10.0) or percentage',
        'education_terms': ['12th Standard', 'Bachelor\'s', 'Master\'s', 'PhD'],
        'phone_format': '+91 XXXXX XXXXX',
        'grading_system': 'CGPA/Percentage system',
        'common_scholarships': ['Merit Scholarships', 'Government Schemes']
    },
    'China': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Chinese GPA scale (0.0-4.0) or percentage',
        'education_terms': ['高中 (High School)', '学士 (Bachelor)', '硕士 (Master)', '博士 (PhD)'],
        'phone_format': '+86 XXX XXXX XXXX',
        'grading_system': '优秀/良好/中等/及格',
        'common_scholarships': ['Chinese Government Scholarship', 'Confucius Institute']
    },
    'Uganda': {
        'gpa_scale': {'min': 0.0, 'max': 5.0, 'step': 0.1},
        'gpa_help': 'Ugandan GPA scale (0.0-5.0, 5.0 = best)',
        'education_terms': ['A-Level', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+256 XXX XXXXXX',
        'grading_system': 'First Class/Upper Second/Lower Second/Pass',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'South Africa': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'South African GPA equivalent (0.0-4.0)',
        'education_terms': ['Matric', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+27 XX XXX XXXX',
        'grading_system': 'A/B/C/D/E grading system',
        'common_scholarships': ['NSFAS', 'Merit Bursaries']
    },
    'Nigeria': {
        'gpa_scale': {'min': 0.0, 'max': 5.0, 'step': 0.1},
        'gpa_help': 'Nigerian CGPA scale (0.0-5.0, 5.0 = best)',
        'education_terms': ['SSCE', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+234 XXX XXX XXXX',
        'grading_system': 'First Class/Second Class Upper/Second Class Lower/Third Class',
        'common_scholarships': ['Federal Government Scholarships', 'International Scholarships']
    },
    'Brazil': {
        'gpa_scale': {'min': 0.0, 'max': 10.0, 'step': 0.1},
        'gpa_help': 'Brazilian grading scale (0.0-10.0)',
        'education_terms': ['Ensino Médio', 'Bacharelado', 'Mestrado', 'Doutorado'],
        'phone_format': '+55 XX XXXXX XXXX',
        'grading_system': 'Conceito A/B/C/D system',
        'common_scholarships': ['CAPES', 'CNPq', 'FAPESP']
    },
    'Kenya': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Kenyan GPA scale (0.0-4.0) or percentage',
        'education_terms': ['KCSE', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+254 XXX XXXXXX',
        'grading_system': 'A/B/C/D/E grading system',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'Ghana': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Ghanaian GPA scale (0.0-4.0)',
        'education_terms': ['WASSCE', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+233 XXX XXX XXXX',
        'grading_system': 'First Class/Second Class/Third Class/Pass',
        'common_scholarships': ['GETFUND', 'International Scholarships']
    },
    'Tanzania': {
        'gpa_scale': {'min': 0.0, 'max': 5.0, 'step': 0.1},
        'gpa_help': 'Tanzanian GPA scale (0.0-5.0)',
        'education_terms': ['Form VI', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+255 XXX XXX XXXX',
        'grading_system': 'First Class/Second Class/Third Class/Pass',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'Rwanda': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Rwandan GPA scale (0.0-4.0)',
        'education_terms': ['A-Level', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+250 XXX XXX XXX',
        'grading_system': 'First Class/Second Class/Third Class/Pass',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'Ethiopia': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Ethiopian GPA scale (0.0-4.0)',
        'education_terms': ['Grade 12', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+251 XXX XXX XXXX',
        'grading_system': 'A/B/C/D/F grading system',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'Zambia': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Zambian GPA scale (0.0-4.0)',
        'education_terms': ['Grade 12', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+260 XXX XXX XXXX',
        'grading_system': 'A/B/C/D/E grading system',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'Zimbabwe': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Zimbabwean GPA scale (0.0-4.0)',
        'education_terms': ['A-Level', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+263 XXX XXX XXXX',
        'grading_system': 'A/B/C/D/E grading system',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'Bangladesh': {
        'gpa_scale': {'min': 0.0, 'max': 5.0, 'step': 0.1},
        'gpa_help': 'Bangladeshi CGPA scale (0.0-5.0)',
        'education_terms': ['HSC', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+880 XXXX XXXXXX',
        'grading_system': 'A+/A/A-/B+/B/B-/C+/C/D/F',
        'common_scholarships': ['Government Scholarships', 'International Scholarships']
    },
    'Pakistan': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Pakistani GPA scale (0.0-4.0) or percentage',
        'education_terms': ['Intermediate', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+92 XXX XXXXXXX',
        'grading_system': 'A+/A/B+/B/C+/C/D/F',
        'common_scholarships': ['HEC Scholarships', 'International Programs']
    },
    'Indonesia': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Indonesian GPA scale (0.0-4.0)',
        'education_terms': ['SMA', 'Sarjana (S1)', 'Magister (S2)', 'Doktor (S3)'],
        'phone_format': '+62 XXX XXXX XXXX',
        'grading_system': 'A/B+/B/C+/C/D+/D/E',
        'common_scholarships': ['LPDP', 'Beasiswa Indonesia']
    },
    'Philippines': {
        'gpa_scale': {'min': 1.0, 'max': 5.0, 'step': 0.1},
        'gpa_help': 'Philippine GPA scale (1.0-5.0, 1.0 = best)',
        'education_terms': ['Senior High School', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+63 XXX XXX XXXX',
        'grading_system': '1.00-5.00 scale (1.00 = highest)',
        'common_scholarships': ['CHED Scholarships', 'DOST Scholarships']
    },
    'Mexico': {
        'gpa_scale': {'min': 0.0, 'max': 10.0, 'step': 0.1},
        'gpa_help': 'Mexican grading scale (0.0-10.0)',
        'education_terms': ['Bachillerato', 'Licenciatura', 'Maestría', 'Doctorado'],
        'phone_format': '+52 XXX XXX XXXX',
        'grading_system': '10-point scale (10 = excellent)',
        'common_scholarships': ['CONACYT', 'Becas Benito Juárez']
    },
    'Egypt': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Egyptian GPA scale (0.0-4.0) or percentage',
        'education_terms': ['Thanawiya Amma', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'phone_format': '+20 XXX XXX XXXX',
        'grading_system': 'Excellent/Very Good/Good/Pass/Fail',
        'common_scholarships': ['Government Scholarships', 'International Programs']
    },
    'Turkey': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Turkish GPA scale (0.0-4.0)',
        'education_terms': ['Lise', 'Lisans', 'Yüksek Lisans', 'Doktora'],
        'phone_format': '+90 XXX XXX XXXX',
        'grading_system': 'AA/BA/BB/CB/CC/DC/DD/FD/FF',
        'common_scholarships': ['Türkiye Bursları', 'University Scholarships']
    },
    'Vietnam': {
        'gpa_scale': {'min': 0.0, 'max': 10.0, 'step': 0.1},
        'gpa_help': 'Vietnamese grading scale (0.0-10.0)',
        'education_terms': ['Tốt nghiệp THPT', 'Cử nhân', 'Thạc sĩ', 'Tiến sĩ'],
        'phone_format': '+84 XXX XXX XXXX',
        'grading_system': '10-point scale (10 = excellent)',
        'common_scholarships': ['Government Scholarships', 'VIED Programs']
    },
    'Other': {
        'gpa_scale': {'min': 0.0, 'max': 4.0, 'step': 0.1},
        'gpa_help': 'Please convert to 4.0 scale or enter as percentage',
        'education_terms': ['Secondary Education', 'Bachelor\'s', 'Master\'s', 'Doctorate'],
        'phone_format': '+XXX XXX XXX XXXX',
        'grading_system': 'Local grading system',
        'common_scholarships': ['International Scholarships', 'Merit Awards']
    }
}

def get_country_config(country):
    """Get configuration for a specific country"""
    return COUNTRY_CONFIG.get(country, COUNTRY_CONFIG['Other'])

def get_gpa_input_config(country):
    """Get GPA input configuration for a country with enhanced flexibility"""
    config = get_country_config(country)
    gpa_scale = config['gpa_scale']
    
    # Enhanced configuration with multiple scale support
    return {
        'min_value': gpa_scale['min'],
        'max_value': gpa_scale['max'],
        'step': gpa_scale['step'],
        'help': config['gpa_help'],
        'reverse_scale': gpa_scale.get('reverse', False),
        'supports_multiple_scales': True,  # Allow users to input in different scales
        'conversion_info': get_gpa_conversion_info(country)
    }

def get_gpa_conversion_info(country):
    """Get GPA conversion information for flexibility"""
    conversion_info = {
        'Uganda': {
            'primary_scale': '5.0',
            'alternative_scales': ['4.0', 'percentage'],
            'conversion_notes': 'Can input as 5.0 scale, 4.0 scale, or percentage'
        },
        'Nigeria': {
            'primary_scale': '5.0', 
            'alternative_scales': ['4.0', 'percentage'],
            'conversion_notes': 'CGPA typically on 5.0 scale, but 4.0 also accepted'
        },
        'United States': {
            'primary_scale': '4.0',
            'alternative_scales': ['percentage'],
            'conversion_notes': 'Standard 4.0 scale or percentage'
        },
        'Kenya': {
            'primary_scale': '4.0',
            'alternative_scales': ['percentage', 'letter_grade'],
            'conversion_notes': 'Can input as GPA or percentage'
        },
        'South Africa': {
            'primary_scale': '4.0',
            'alternative_scales': ['percentage', 'symbol_grade'],
            'conversion_notes': 'Convert from percentage or symbol grades'
        }
    }
    
    return conversion_info.get(country, {
        'primary_scale': '4.0',
        'alternative_scales': ['percentage'],
        'conversion_notes': 'Please convert to 4.0 scale or provide percentage'
    })

def convert_gpa_to_standard(gpa_value, input_scale, target_scale='4.0'):
    """Convert GPA between different scales"""
    if not gpa_value:
        return None
        
    try:
        gpa_float = float(gpa_value)
    except (ValueError, TypeError):
        return gpa_value  # Return as-is if can't convert
    
    # Conversion logic
    if input_scale == target_scale:
        return gpa_float
    
    # Convert to 4.0 scale (standard)
    if input_scale == '5.0' and target_scale == '4.0':
        return round((gpa_float / 5.0) * 4.0, 2)
    elif input_scale == '4.0' and target_scale == '5.0':
        return round((gpa_float / 4.0) * 5.0, 2)
    elif input_scale == 'percentage':
        if gpa_float > 4.0:  # Assume it's a percentage
            if target_scale == '4.0':
                return round((gpa_float / 100.0) * 4.0, 2)
            elif target_scale == '5.0':
                return round((gpa_float / 100.0) * 5.0, 2)
    
    return gpa_float

def format_gpa_display(gpa, country):
    """Format GPA for display based on country"""
    config = get_country_config(country)
    
    if country == 'Germany' and gpa:
        return f"{gpa} (German scale: 1.0 = best)"
    elif country in ['France'] and gpa:
        return f"{gpa}/20"
    elif country in ['India', 'Brazil'] and gpa:
        return f"{gpa}/10"
    elif country in ['Uganda', 'Nigeria'] and gpa:
        return f"{gpa}/5"
    elif country == 'Australia' and gpa:
        return f"{gpa}/7"
    else:
        return f"{gpa}/4.0"
