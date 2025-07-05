import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import DatabaseManager
from core.api import APIManager
from core.scraping import EnhancedScholarshipScraper
from core.application import ApplicationGenerator
from core.profile import CVExtractor
from core.cv_templates import CVTemplateGenerator
from core.country_config import COUNTRY_CONFIG, get_gpa_input_config, get_country_config, convert_gpa_to_standard

# Configure page for mobile with favicon
st.set_page_config(
    page_title="📚 Scholarship Hunter",
    page_icon="🎓",  # This acts as favicon in Streamlit
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom favicon reference
st.markdown("""
<head>
    <link rel="icon" type="image/svg+xml" href="./favicon.svg">
    <link rel="apple-touch-icon" href="./favicon.svg">
</head>
""", unsafe_allow_html=True)

# Load mobile CSS
def load_css():
    try:
        css_path = os.path.join(os.path.dirname(__file__), 'mobile_styles.css')
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # CSS file not found, continue without custom styles

load_css()
# --- Session State Initialization ---
if 'user_id' not in st.session_state:
    import hashlib
    from datetime import datetime
    st.session_state.user_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = []
if 'user_goal' not in st.session_state:
    st.session_state.user_goal = 'student'
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = 'Uganda'  # Default to Uganda as requested

# --- Initialize Core Components ---
db_manager = DatabaseManager()
api_manager = APIManager()
scraper = EnhancedScholarshipScraper(db_manager)
cv_extractor = CVExtractor()
cv_generator = CVTemplateGenerator()

# Initialize scholarship cache and show stats
from core.scholarship_cache import ScholarshipCache
cache = ScholarshipCache()
cache_count = cache.get_scholarship_count()

# --- Sidebar: User Settings ---
st.sidebar.header("User Settings")

# Show cache status with more details
uganda_count = cache.get_scholarship_count_by_country('Uganda') if hasattr(cache, 'get_scholarship_count_by_country') else 0
st.sidebar.caption(f"📊 Database: {cache_count} total ({uganda_count} Uganda-specific)")
st.sidebar.caption("⚡ Instant results from shared database!")

# Country selection - prominently placed
st.session_state.selected_country = st.sidebar.selectbox(
    "🌍 Your Country", 
    options=list(COUNTRY_CONFIG.keys()),
    index=list(COUNTRY_CONFIG.keys()).index(st.session_state.selected_country) if st.session_state.selected_country in COUNTRY_CONFIG else 0,
    help="Select your country for localized GPA scale and requirements"
)

# Display country-specific info
country_config = get_country_config(st.session_state.selected_country)
gpa_config = get_gpa_input_config(st.session_state.selected_country)
st.sidebar.info(f"📊 GPA Scale: {gpa_config['help']}")

goal_options = ['student', 'entrepreneur', 'researcher', 'nonprofit', 'artist']
st.session_state.user_goal = st.sidebar.selectbox("Select your goal", goal_options, index=goal_options.index(st.session_state.user_goal))

# Enhanced API Key Input with Security Info
with st.sidebar.expander("🔐 API Key Settings (Optional)", expanded=False):
    st.success("✅ App works perfectly without an API key!")
    st.info("Add your API key only for enhanced AI letter generation features.")
    user_api_key = st.text_input("Your Gemini API Key (optional)", type="password", help="Get your free API key from https://makersuite.google.com/app/apikey")
    
    # Check if user has a saved key
    if api_manager.verify_user_api_key(st.session_state.user_id, user_api_key) and user_api_key:
        st.success("✅ Valid API key detected")
    elif user_api_key:
        st.info("🔄 New API key will be securely saved")

api_key, mode = api_manager.get_api_key(st.session_state.user_id, user_api_key)

usage_stats = api_manager.get_usage_stats()
if mode == 'user':
    st.sidebar.success("🚀 Using your personal API key - unlimited access!")
elif mode == 'server':
    st.sidebar.info(f"🆓 Free AI slots remaining: {usage_stats['remaining_slots']}/{usage_stats['total_users']}")
elif mode == 'basic':
    st.sidebar.warning("⚠️ Free AI slots are full. Provide your own API key for enhanced features.")

# --- Sidebar: CV Upload & Profile ---
st.sidebar.subheader("📄 Profile Setup")

# Profile method selection
profile_method = st.sidebar.radio(
    "Choose profile method:",
    ["📤 Upload CV/Resume", f"✏️ Manual Entry ({st.session_state.user_goal.title()})"],
    help="Upload your existing CV or create a profile manually"
)

if profile_method == "📤 Upload CV/Resume":
    cv_file = st.sidebar.file_uploader("Upload PDF or DOCX", type=['pdf', 'docx'])
    if cv_file:
        if cv_file.type == 'application/pdf':
            text = cv_extractor.extract_text_from_pdf(cv_file)
        else:
            text = cv_extractor.extract_text_from_docx(cv_file)
        profile = cv_extractor.extract_profile_info(text)
        if profile:
            st.session_state.user_profile.update(profile)
            db_manager.save_user_profile(st.session_state.user_id, st.session_state.user_profile)
            st.sidebar.success("✅ Profile extracted from CV!")

else:
    # Manual profile entry with role-specific fields
    st.sidebar.write(f"**Creating {st.session_state.user_goal} profile for {st.session_state.selected_country}:**")
    
    # Show simplified form in sidebar
    with st.sidebar.form(f"basic_profile_form_{st.session_state.user_goal}_{st.session_state.selected_country}"):
        current_profile = st.session_state.user_profile
        
        # Basic info (always needed)
        name = st.text_input("👤 Full Name", value=current_profile.get('name', ''))
        email = st.text_input("📧 Email", value=current_profile.get('email', ''))
        
        # Enhanced Country-specific GPA input for students
        gpa_value = None
        gpa_scale_type = None
        if st.session_state.user_goal == 'student':
            gpa_config = get_gpa_input_config(st.session_state.selected_country)
            
            # Enhanced GPA input with multiple scale support
            st.write("**📊 Academic Performance:**")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Let users choose their preferred input scale
                scale_options = ["Auto (Country Default)", "4.0 Scale", "5.0 Scale", "Percentage"]
                gpa_scale_type = st.selectbox(
                    "Input Scale", 
                    options=scale_options,
                    help="Choose how you want to input your GPA"
                )
            
            with col2:
                if gpa_scale_type == "Auto (Country Default)":
                    max_val = gpa_config['max_value']
                    help_text = gpa_config['help']
                elif gpa_scale_type == "4.0 Scale":
                    max_val = 4.0
                    help_text = "Standard 4.0 GPA scale (US/UK style)"
                elif gpa_scale_type == "5.0 Scale":
                    max_val = 5.0
                    help_text = "5.0 GPA scale (Uganda/Nigeria style)"
                else:  # Percentage
                    max_val = 100.0
                    help_text = "Enter as percentage (0-100%)"
                
                gpa_value = st.number_input(
                    f"GPA/Grade", 
                    min_value=0.0, 
                    max_value=max_val, 
                    value=float(current_profile.get('gpa', 0.0)),
                    step=0.1 if max_val <= 10 else 1.0,
                    help=help_text
                )
        
        # Role-specific key field
        if st.session_state.user_goal == 'student':
            key_field = st.text_input("📚 Major", value=current_profile.get('major', ''))
            key_field_name = 'major'
        elif st.session_state.user_goal == 'entrepreneur':
            key_field = st.text_input("🚀 Business Focus", value=current_profile.get('market_focus', ''))
            key_field_name = 'market_focus'
        elif st.session_state.user_goal == 'researcher':
            key_field = st.text_input("🔬 Research Area", value=current_profile.get('research_area', ''))
            key_field_name = 'research_area'
        elif st.session_state.user_goal == 'artist':
            key_field = st.text_input("🎨 Artistic Medium", value=current_profile.get('medium', ''))
            key_field_name = 'medium'
        else:  # nonprofit
            key_field = st.text_input("🎯 Mission Focus", value=current_profile.get('impact_area', ''))
            key_field_name = 'impact_area'
        
        if st.form_submit_button("💾 Save Basic Profile"):
            profile_update = {
                'name': name,
                'email': email,
                'country': st.session_state.selected_country,
                key_field_name: key_field
            }
            if gpa_value is not None and gpa_scale_type:
                # Convert GPA to standard 4.0 scale for storage while preserving original
                
                # Store both original and converted values
                profile_update['gpa'] = gpa_value
                profile_update['gpa_scale'] = gpa_scale_type
                
                # Convert for standardization if needed
                if gpa_scale_type != "4.0 Scale":
                    if gpa_scale_type == "5.0 Scale":
                        converted_gpa = convert_gpa_to_standard(gpa_value, '5.0', '4.0')
                    elif gpa_scale_type == "Percentage":
                        converted_gpa = convert_gpa_to_standard(gpa_value, 'percentage', '4.0')
                    else:
                        converted_gpa = gpa_value
                    profile_update['gpa_4_0'] = converted_gpa
                else:
                    profile_update['gpa_4_0'] = gpa_value
            
            st.session_state.user_profile.update(profile_update)
            db_manager.save_user_profile(st.session_state.user_id, st.session_state.user_profile)
            st.sidebar.success("✅ Enhanced profile saved with GPA conversion!")
    
    # Link to detailed profile
    if st.sidebar.button("📝 Complete Full Profile"):
        st.session_state.show_detailed_profile = True

# --- Sidebar: Custom Sites ---
st.sidebar.subheader("Add Custom Websites")
custom_url = st.sidebar.text_input("Enter website URL")
is_public = st.sidebar.checkbox("Share with other users")
if st.sidebar.button("Add Website"):
    if custom_url:
        success = db_manager.add_custom_site(custom_url, st.session_state.user_id, is_public)
        if success:
            st.sidebar.success("Website added for scraping!")
        else:
            st.sidebar.info("Website already exists, popularity increased!")
user_urls = db_manager.get_user_custom_urls(st.session_state.user_id)
if user_urls:
    st.sidebar.subheader("Your Added Websites")
    for url in user_urls:
        st.sidebar.write(f"{url['url']} (Popularity: {url['popularity']})")

# --- Main Content ---
# Add logo and title in a responsive layout
col_logo, col_title = st.columns([1, 4])
with col_logo:
    # Display logo using Streamlit's image component
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.svg')
    try:
        # Try using st.image for SVG
        st.image(logo_path, width=60)
    except Exception:
        try:
            # Fallback: Use base64 encoding
            import base64
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 80px;">
                <img src="data:image/svg+xml;base64,{logo_data}" 
                     style="width: 60px; height: 60px; object-fit: contain;" 
                     alt="Scholarship Hunter Logo">
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            # Final fallback emoji
            st.markdown("<div style='text-align: center; font-size: 3rem;'>🎓</div>", unsafe_allow_html=True)

with col_title:
    st.title("🎓 Scholarship Hunter")
    st.caption("Find opportunities and generate applications on-the-go")

# Compact search interface
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        keywords = st.text_input("🔍 Search keywords", placeholder="e.g., engineering, women, undergraduate")
    with col2:
        search_clicked = st.button("🚀 Search", use_container_width=True)

if search_clicked:
    keywords_list = [k.strip() for k in keywords.split(',')] if keywords else None
    custom_urls = [url['url'] for url in db_manager.get_custom_sites(st.session_state.user_id, include_public=False)]
    
    # Enhanced search with status updates
    with st.spinner("⚡ Searching scholarship database..."):
        st.info(f"🎯 Prioritizing {st.session_state.selected_country} + International opportunities")
        st.info("� Using intelligent caching for instant results")
        
        opportunities = scraper.search_by_goal(
            goal=st.session_state.user_goal,
            keywords=keywords_list,
            custom_sites=custom_urls,
            user_id=st.session_state.user_id,
            country=st.session_state.selected_country  # Pass country for country-specific sites
        )
        st.session_state.scraped_data = opportunities
        
        if opportunities:
            st.success(f"🎉 Found {len(opportunities)} scholarships instantly from database!")
        else:
            st.warning("⚠️ No scholarships found. Try different keywords or check back later.")
if st.session_state.scraped_data:
    st.header("📋 Found Opportunities")
    
    # Enhanced statistics display
    total_opps = len(st.session_state.scraped_data)
    country_specific = len([opp for opp in st.session_state.scraped_data if st.session_state.selected_country.lower() in opp.get('source', '').lower()])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Total Found", total_opps)
    with col2:
        st.metric(f"🌍 {st.session_state.selected_country}", country_specific)
    with col3:
        st.metric("🌐 International", total_opps - country_specific)
    
    # Mobile-optimized table display with enhanced columns
    import pandas as pd
    df = pd.DataFrame(st.session_state.scraped_data)
    
    # Create a clean, mobile-friendly table with more info
    display_df = df[['title', 'deadline', 'amount', 'category']].copy()
    display_df.columns = ['📚 Title', '⏰ Deadline', '💰 Amount', '🎯 Category']
    
    # Add priority indicators
    display_df['🔥 Priority'] = df.apply(lambda row: 
        '🔥🔥🔥' if st.session_state.selected_country.lower() in row.get('source', '').lower()
        else '🔥🔥' if 'africa' in row.get('source', '').lower()
        else '🔥', axis=1
    )
    
    # Add clickable row selection
    st.write("**Tap a row to select for application generation:**")
    st.caption("🔥🔥🔥 = Country-specific, 🔥🔥 = Regional, 🔥 = International")
    
    # Display the enhanced table
    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Handle row selection
    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        st.session_state.selected_opportunity = st.session_state.scraped_data[selected_idx]
        st.success(f"✅ Selected: **{st.session_state.selected_opportunity['title']}**")
    
    # Detailed view for selected opportunity
    if 'selected_opportunity' in st.session_state:
        with st.expander("📄 View Full Details", expanded=False):
            opp = st.session_state.selected_opportunity
            st.write(f"**Title:** {opp['title']}")
            st.write(f"**Deadline:** {opp.get('deadline', 'Check website')}")
            st.write(f"**Amount:** {opp.get('amount', 'Check website')}")
            st.write(f"**Category:** {opp.get('category', 'General')}")
            st.write(f"**Description:** {opp.get('description', 'No description available')}")
            st.write(f"**Source:** [Visit Website]({opp.get('source', '#')})")
    
    st.subheader("✍️ Generate Application Letter")
    
    # Use selected opportunity or dropdown fallback
    if 'selected_opportunity' in st.session_state:
        selected_opp = st.session_state.selected_opportunity
        selected_title = selected_opp['title']
        st.info(f"📝 Creating application for: **{selected_title}**")
    else:
        st.warning("👆 Please select an opportunity from the table above")
        selected_title = st.selectbox("Or select manually:", [opp['title'] for opp in st.session_state.scraped_data])
        selected_opp = next((opp for opp in st.session_state.scraped_data if opp['title'] == selected_title), None)
    with st.form(f"application_questions_{st.session_state.user_id}"):
        motivation = st.text_area("Why are you interested in this opportunity?")
        goals = st.text_area("What are your goals related to this opportunity?")
        challenges = st.text_area("What challenges have you overcome that make you a strong candidate?")
        if st.form_submit_button("Generate Application Letter"):
            if selected_opp and st.session_state.user_profile:
                user_answers = {
                    'motivation': motivation,
                    'goals': goals,
                    'challenges': challenges
                }
                app_generator = ApplicationGenerator(api_manager, st.session_state.user_id)
                with st.spinner("Generating application letter..."):
                    letter = app_generator.generate_application_letter(
                        st.session_state.user_profile,
                        selected_opp,
                        user_answers,
                        api_key=api_key,
                        mode=mode
                    )
                    st.subheader("Generated Application Letter")
                    st.text_area("Application Letter", letter, height=400)
                    st.download_button(
                        label="Download Letter",
                        data=letter,
                        file_name=f"application_{selected_opp['title']}.txt",
                        mime="text/plain"
                    )
            else:
                st.error("Please complete your profile and select an opportunity.")

# --- Detailed Profile Section ---
if st.session_state.get('show_detailed_profile', False):
    st.header(f"📋 Complete Your {st.session_state.user_goal.title()} Profile")
    
    # Generate role-specific form with country awareness
    detailed_profile = cv_extractor.get_role_specific_form(
        st.session_state.user_goal, 
        st.session_state.user_profile,
        country=st.session_state.selected_country
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Complete Profile", type="primary"):
            st.session_state.user_profile.update(detailed_profile)
            db_manager.save_user_profile(st.session_state.user_id, st.session_state.user_profile)
            st.success("✅ Complete profile saved!")
            st.session_state.show_detailed_profile = False
            st.experimental_rerun()
    
    with col2:
        if st.button("📄 Generate CV Template"):
            # Filter data for CV
            cv_data = cv_extractor.filter_profile_data(
                detailed_profile, 
                st.session_state.user_goal, 
                for_cv=True
            )
            
            # Generate CV
            cv_doc = cv_generator.generate_cv(cv_data, st.session_state.user_goal)
            cv_bytes = cv_generator.save_cv_to_bytes(cv_doc)
            
            st.download_button(
                label="📥 Download CV Template",
                data=cv_bytes.getvalue(),
                file_name=f"{st.session_state.user_goal}_cv_template.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            st.info("🎯 Your CV template is ready! The data has been optimized for your role.")

# Enhanced current profile summary
if st.session_state.user_profile:
    with st.sidebar.expander("👤 Current Profile", expanded=False):
        profile = st.session_state.user_profile
        for key, value in profile.items():
            if value and key not in ['gpa_4_0']:  # Don't show internal converted GPA
                display_key = key.replace('_', ' ').title()
                
                # Special handling for GPA display
                if key == 'gpa' and 'gpa_scale' in profile:
                    gpa_scale = profile.get('gpa_scale', 'Unknown')
                    converted_gpa = profile.get('gpa_4_0', 'N/A')
                    st.write(f"**📊 GPA:** {value} ({gpa_scale})")
                    if converted_gpa != 'N/A' and converted_gpa != value:
                        st.caption(f"   → 4.0 scale: {converted_gpa}")
                elif key != 'gpa_scale':  # Don't show the scale separately
                    display_value = str(value)[:50] + ('...' if len(str(value)) > 50 else '')
                    st.write(f"**{display_key}:** {display_value}")
        
        # Country-specific tips
        country_config = get_country_config(st.session_state.selected_country)
        if 'common_scholarships' in country_config:
            st.write("**💡 Common scholarship types in your country:**")
            for scholarship in country_config['common_scholarships'][:3]:  # Show top 3
                st.caption(f"• {scholarship}")
