import requests
from bs4 import BeautifulSoup
import re
import time
import random
import streamlit as st
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import hashlib
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .config import (
    USER_AGENTS, MIN_DELAY, MAX_DELAY, RETRY_DELAY, 
    BROWSER_HEADERS, REFERRERS, MAX_REQUESTS_PER_DOMAIN, DOMAIN_COOLDOWN
)
from .scholarship_cache import ScholarshipCache

class EnhancedScholarshipScraper:
    """Enhanced scraper with advanced anti-bot measures and intelligent caching"""
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.cache = ScholarshipCache()  # Initialize intelligent cache
        self.session = requests.Session()
        # Advanced anti-bot state tracking
        self.domain_requests = {}  # Track requests per domain
        self.last_request_time = {}  # Track last request time per domain
        self.failed_domains = set()  # Track temporarily failed domains
        self.current_user_agent = random.choice(USER_AGENTS)
        
        # Enhanced session state to mimic real browsing
        self.session_persistence = {
            'cookies_cleared_count': 0,
            'user_agent_rotations': 0,
            'total_requests': 0,
            'session_start_time': datetime.now()
        }
        
        # Initialize session with realistic headers
        self.update_session_headers()
        
        # Enhanced country-specific scholarship sites with better coverage
        self.country_scholarship_sites = {
            'Uganda': [
                'https://www.makerere.ac.ug/scholarships',
                'https://www.mubs.ac.ug/scholarships', 
                'https://scholarships.gov.ug/',
                'https://www.opportunitiesforafricans.com/category/scholarships/uganda-scholarships/',
                'https://www.afterschoolafrica.com/scholarships/',
                'https://www.scholars4dev.com/category/scholarships/africa-scholarships/uganda-scholarships/',
                'https://www.studyportals.com/scholarships/uganda',
                'https://www.scholarshiproar.com/scholarships-in-uganda/'
            ],
            'Nigeria': [
                'https://www.scholarships.com.ng/',
                'https://opportunitiesforafricans.com/category/scholarships/nigeria-scholarships/',
                'https://www.afterschoolafrica.com/scholarships/',
                'https://www.scholars4dev.com/category/scholarships/africa-scholarships/nigeria-scholarships/',
                'https://www.studyportals.com/scholarships/nigeria',
                'https://www.scholarshiproar.com/scholarships-in-nigeria/',
                'https://www.studentfinance.ng/'
            ],
            'Kenya': [
                'https://www.opportunitiesforafricans.com/category/scholarships/kenya-scholarships/',
                'https://www.afterschoolafrica.com/scholarships/',
                'https://www.scholars4dev.com/category/scholarships/africa-scholarships/kenya-scholarships/',
                'https://www.studyportals.com/scholarships/kenya',
                'https://www.scholarshiproar.com/scholarships-in-kenya/',
                'https://www.helb.co.ke/'
            ],
            'Ghana': [
                'https://www.opportunitiesforafricans.com/category/scholarships/ghana-scholarships/',
                'https://www.afterschoolafrica.com/scholarships/',
                'https://www.scholars4dev.com/category/scholarships/africa-scholarships/ghana-scholarships/',
                'https://www.studyportals.com/scholarships/ghana',
                'https://www.scholarshiproar.com/scholarships-in-ghana/',
                'https://getfund.gov.gh/'
            ],
            'Tanzania': [
                'https://www.opportunitiesforafricans.com/category/scholarships/tanzania-scholarships/',
                'https://www.afterschoolafrica.com/scholarships/',
                'https://www.studyportals.com/scholarships/tanzania',
                'https://www.scholarshiproar.com/scholarships-in-tanzania/'
            ],
            'South Africa': [
                'https://www.nsfas.org.za/',
                'https://www.scholarshipportal.com/scholarships/south-africa',
                'https://www.opportunitiesforafricans.com/category/scholarships/south-africa-scholarships/',
                'https://www.afterschoolafrica.com/scholarships/',
                'https://www.studyportals.com/scholarships/south-africa',
                'https://www.scholarshiproar.com/scholarships-in-south-africa/'
            ],
            'International': [
                'https://www.scholarships.com/financial-aid/college-scholarships/',
                'https://www.fastweb.com/college-scholarships',
                'https://www.petersons.com/college-search/scholarship-search.aspx',
                'https://www.opportunitiesforafricans.com/',
                'https://www.scholars4dev.com/',
                'https://www.scholarshipportal.com/',
                'https://www.afterschoolafrica.com/scholarships/',
                'https://www.studyportals.com/scholarships',
                'https://www.scholarshiproar.com/',
                'https://www.findamasters.com/funding/',
                'https://www.phdportal.com/funding/'
            ]
        }
        # Add more realistic headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.scholarship_sites = {
            'student': [
                'https://www.scholarships.com/financial-aid/college-scholarships/',
                'https://www.fastweb.com/college-scholarships',
                'https://www.petersons.com/college-search/scholarship-search.aspx',
                'https://www.unigo.com/scholarships',
                'https://www.chegg.com/scholarships',
                'https://www.cappex.com/scholarships',
                'https://www.niche.com/colleges/scholarships/',
                'https://studentaid.gov/understand-aid/types/scholarships'
            ],
            # ...other goals omitted for brevity...
        }

    def extract_deadline_info(self, element):
        """Extract deadline information from an element"""
        deadline_patterns = [
            r'deadline[:\s]*([a-zA-Z]+\s+\d{1,2},?\s+\d{4})',
            r'due[:\s]*([a-zA-Z]+\s+\d{1,2},?\s+\d{4})',
            r'apply\s+by[:\s]*([a-zA-Z]+\s+\d{1,2},?\s+\d{4})',
            r'closes[:\s]*([a-zA-Z]+\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}\/\d{1,2}\/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        
        # Search in the element's text
        text = element.get_text()
        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Look for specific deadline-related elements
        deadline_selectors = [
            {'tag': ['span', 'div', 'p'], 'class': re.compile(r'deadline|due|closes', re.I)},
            {'tag': ['time']},
        ]
        
        for selector in deadline_selectors:
            deadline_elem = element.find(selector['tag'], class_=selector.get('class'))
            if deadline_elem:
                deadline_text = deadline_elem.get_text(strip=True)
                if deadline_text and len(deadline_text) < 50:
                    return deadline_text
        
        return 'Check website'

    def extract_amount_info(self, element):
        """Extract scholarship amount information"""
        amount_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'up to \$[\d,]+',
            r'[\d,]+ dollars?',
            r'full tuition',
            r'partial tuition',
        ]
        
        text = element.get_text()
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        return 'Check website'

    def enhance_title(self, title, element, url):
        """Make titles more descriptive by adding context"""
        if not title or len(title.strip()) < 5:
            return title
        
        # Look for additional context around the title
        context_keywords = []
        text = element.get_text().lower()
        
        # Check for scholarship type indicators
        if any(word in text for word in ['undergraduate', 'bachelor']):
            context_keywords.append('Undergraduate')
        elif any(word in text for word in ['graduate', 'master', 'phd', 'doctoral']):
            context_keywords.append('Graduate')
        
        # Check for field of study
        fields = ['engineering', 'medicine', 'business', 'arts', 'science', 'technology', 'law', 'education']
        for field in fields:
            if field in text:
                context_keywords.append(field.title())
                break
        
        # Check for demographic focus
        demographics = ['women', 'minority', 'international', 'veterans', 'first-generation']
        for demo in demographics:
            if demo in text:
                context_keywords.append(demo.title())
                break
        
        # Add context to title if found
        if context_keywords:
            enhanced_title = f"{title} ({', '.join(context_keywords[:2])})"
            return enhanced_title
        
        return title

    def rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        self.current_user_agent = random.choice(USER_AGENTS)
        self.session.headers.update({'User-Agent': self.current_user_agent})

    def can_request_domain(self, url):
        """Check if we can make a request to this domain (enhanced rate limiting)"""
        domain = urlparse(url).netloc
        current_time = datetime.now()
        
        # Check if domain is temporarily blocked
        if domain in self.failed_domains:
            return False
        
        # Check rate limiting
        if domain not in self.domain_requests:
            self.domain_requests[domain] = 0
            self.last_request_time[domain] = current_time
            return True
        
        # Check if enough time has passed since last request
        time_since_last = current_time - self.last_request_time[domain]
        if time_since_last.total_seconds() < DOMAIN_COOLDOWN:
            if self.domain_requests[domain] >= MAX_REQUESTS_PER_DOMAIN:
                return False
        else:
            # Reset counter if cooldown period has passed
            self.domain_requests[domain] = 0
        
        return True

    def track_domain_request(self, url, success=True):
        """Track domain requests for rate limiting"""
        domain = urlparse(url).netloc
        current_time = datetime.now()
        
        if domain not in self.domain_requests:
            self.domain_requests[domain] = 0
        
        self.domain_requests[domain] += 1
        self.last_request_time[domain] = current_time
        self.session_persistence['total_requests'] += 1
        
        if not success:
            # Add to failed domains temporarily
            self.failed_domains.add(domain)
            # Remove from failed domains after some time (in real implementation)

    def simulate_human_reading_pattern(self, content_length):
        """Simulate human reading patterns based on content length"""
        if content_length < 1000:
            reading_time = random.uniform(0.5, 2.0)  # Quick scan
        elif content_length < 5000:
            reading_time = random.uniform(2.0, 8.0)  # Normal reading
        else:
            reading_time = random.uniform(5.0, 15.0)  # Detailed reading
            
        # Add some variability
        reading_time *= random.uniform(0.7, 1.3)
        
        if random.random() < 0.3:  # 30% chance to actually wait
            st.info(f"📖 Reading content ({reading_time:.1f}s)")
            time.sleep(reading_time)
        
        return reading_time

    def random_delay(self):
        """Add random delay between requests (legacy method, uses intelligent_delay)"""
        return self.intelligent_delay()

    def enhanced_session_management(self):
        """Enhanced session management to mimic real browser behavior"""
        current_time = datetime.now()
        session_duration = (current_time - self.session_persistence['session_start_time']).total_seconds()
        
        # Clear cookies periodically (like a real browser session)
        if session_duration > 1800 and random.random() < 0.1:  # 30 minutes, 10% chance
            self.session.cookies.clear()
            self.session_persistence['cookies_cleared_count'] += 1
            st.info("🍪 Session refresh (cleared cookies)")
        
        # Rotate user agent based on session activity
        if self.session_persistence['total_requests'] % 15 == 0 and random.random() < 0.4:
            self.rotate_user_agent()
            self.session_persistence['user_agent_rotations'] += 1
            st.info("🔄 Browser identity rotation")
        
        # Simulate occasional network latency
        if random.random() < 0.05:  # 5% chance
            latency = random.uniform(0.5, 2.0)
            st.info(f"🌐 Network latency simulation ({latency:.1f}s)")
            time.sleep(latency)

    def make_request_with_retry(self, url, max_retries=3):
        """Make request with advanced retry logic and enhanced anti-bot measures"""
        if not self.can_request_domain(url):
            st.warning(f"⏱️ Rate limited for {urlparse(url).netloc}, skipping...")
            return None
            
        # Enhanced session management before each request
        self.enhanced_session_management()
            
        for attempt in range(max_retries):
            try:
                # Enhanced user agent rotation logic
                rotation_chance = 0.15 + (attempt * 0.25)  # 15% first try, 40% second, 65% third
                if random.random() < rotation_chance:
                    self.rotate_user_agent()
                    st.info(f"🔄 Switching browser identity for attempt {attempt + 1}")
                
                # Intelligent delay with human-like patterns
                if attempt > 0:
                    retry_delay = RETRY_DELAY * (attempt + 1) + random.uniform(2, 5)
                    st.info(f"⏱️ Smart retry delay: {retry_delay:.1f}s (attempt {attempt + 1})")
                    time.sleep(retry_delay)
                else:
                    self.intelligent_delay()
                
                # Add random pre-request behavior
                if random.random() < 0.2:  # 20% chance
                    self.mimic_pre_request_behavior()
                
                # Make the request with timeout variation
                timeout = random.uniform(15, 25)  # Variable timeout to seem more human
                response = self.session.get(url, timeout=timeout)
                
                if response.status_code == 200:
                    # Simulate human reading behavior
                    content_length = len(response.content)
                    self.simulate_human_reading_pattern(content_length)
                    
                    self.track_domain_request(url, success=True)
                    return response
                elif response.status_code == 403:
                    st.warning(f"🚫 Access denied on {url} (attempt {attempt + 1}) - Enhanced stealth mode")
                    self.activate_stealth_mode()
                    retry_delay = self.adaptive_retry_strategy(403, attempt)
                    time.sleep(retry_delay)
                elif response.status_code == 429:
                    retry_delay = self.adaptive_retry_strategy(429, attempt)
                    st.warning(f"⏱️ Rate limited on {url}, intelligent backoff: {retry_delay}s...")
                    time.sleep(retry_delay)
                elif response.status_code == 503:
                    retry_delay = self.adaptive_retry_strategy(503, attempt)
                    st.warning(f"🔧 Service unavailable on {url}, adaptive retry in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    st.warning(f"❓ HTTP {response.status_code} on {url}")
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                st.warning(f"⏰ Timeout on {url} (attempt {attempt + 1}) - Adjusting timeout")
                time.sleep(random.uniform(3, 10))
            except requests.exceptions.ConnectionError:
                st.warning(f"🔌 Connection error on {url} (attempt {attempt + 1}) - Network retry")
                time.sleep(random.uniform(5, 15))
            except requests.exceptions.RequestException as e:
                st.warning(f"⚠️ Request error on {url}: {str(e)}")
                if attempt == max_retries - 1:
                    self.track_domain_request(url, success=False)
                    return None
                time.sleep(random.uniform(3, 12))
        
        self.track_domain_request(url, success=False)
        st.error(f"❌ Failed to access {url} after {max_retries} enhanced attempts")
        return None

    def mimic_pre_request_behavior(self):
        """Mimic human pre-request behaviors"""
        behaviors = [
            ("🤔 Checking page...", random.uniform(0.5, 1.5)),
            ("🔍 Reading URL...", random.uniform(0.3, 1.0)),
            ("📱 Adjusting browser...", random.uniform(0.5, 2.0)),
        ]
        
        behavior, delay = random.choice(behaviors)
        st.info(behavior)
        time.sleep(delay)

    def activate_stealth_mode(self):
        """Activate enhanced stealth mode when blocked"""
        st.info("🥷 Activating stealth mode...")
        
        # Clear all cookies and session data
        self.session.cookies.clear()
        
        # Force user agent rotation
        self.rotate_user_agent()
        
        # Update headers with more realistic patterns
        self.update_session_headers()
        
        # Add a longer delay
        stealth_delay = random.uniform(10, 20)
        st.info(f"🔒 Stealth delay: {stealth_delay:.1f}s")
        time.sleep(stealth_delay)

    def scrape_site(self, url, goal="student"):
        try:
            response = self.make_request_with_retry(url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            opportunities = []
            for script in soup(["script", "style"]):
                script.decompose()
            selectors = [
                {'tag': ['div', 'article', 'section'], 'class': re.compile(r'scholarship|grant|award|funding|opportunity', re.I)},
                {'tag': ['div', 'article'], 'class': re.compile(r'result|item|card|listing|program', re.I)},
                {'tag': ['li'], 'class': re.compile(r'scholarship|grant|opportunity', re.I)},
            ]
            for selector in selectors:
                elements = soup.find_all(selector['tag'], class_=selector.get('class'))
                for element in elements[:20]:
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    enhanced_title = self.enhance_title(title, element, url)
                    desc_elem = element.find(['p', 'div', 'span'], string=re.compile(r'.{50,}'))
                    description = desc_elem.get_text(strip=True)[:400] if desc_elem else "No description available"
                    deadline = self.extract_deadline_info(element)
                    amount = self.extract_amount_info(element)
                    
                    opportunities.append({
                        'title': enhanced_title,
                        'description': description,
                        'deadline': deadline,
                        'amount': amount,
                        'source': url,
                        'category': goal,
                        'target_audience': goal,
                        'scraped_at': datetime.now().isoformat()
                    })
            return opportunities[:25]
        except Exception as e:
            st.error(f"Error scraping {url}: {str(e)}")
            return []

    def search_by_goal(self, goal="student", keywords=None, custom_sites=None, user_id=None, country=None):
        """Fast search using intelligent caching with background database updates"""
        
        # Step 1: Get cached scholarships immediately (fast response)
        st.info(f"🚀 Searching cached scholarships for {goal} opportunities{f' in {country}' if country else ''}...")
        
        cached_opportunities = self.cache.search_scholarships(
            goal=goal,
            keywords=keywords,
            country=country,
            limit=50
        )
        
        # Format cached data for consistency
        formatted_opportunities = []
        for opp in cached_opportunities:
            formatted_opportunities.append({
                'title': opp['title'],
                'description': opp['description'] or 'No description available',
                'amount': opp['amount'] or 'Amount not specified',
                'deadline': opp['deadline'] or 'Check website for deadline',
                'category': opp['category'] or 'General',
                'source': opp['source'] or '#',
                'goal_type': opp['goal_type'],
                'country': opp['country'],
                'priority': opp['priority']
            })
        
        st.success(f"✅ Found {len(formatted_opportunities)} scholarships from cache (instant results)")
        
        # Step 2: Start background database update (non-blocking)
        self._start_background_update(goal, keywords, country, user_id)
        
        # Step 3: Optional foreground refresh if cache is very sparse
        if len(formatted_opportunities) < 5:  # Only if very few results
            st.info("🔄 Limited cached results. Performing quick targeted search...")
            
            # Get fresh scholarships from a few reliable sources
            fresh_opportunities = self._perform_limited_scraping(goal, keywords, country)
            
            # Add fresh scholarships to cache
            if fresh_opportunities:
                self.cache.add_scholarships([{
                    'title': opp['title'],
                    'description': opp['description'],
                    'amount': opp['amount'],
                    'deadline': opp['deadline'],
                    'category': opp['category'],
                    'source': opp['source'],
                    'goal_type': goal,
                    'country': country or 'International',
                    'priority': 3  # Medium priority for new finds
                } for opp in fresh_opportunities])
                
                # Add to current results
                formatted_opportunities.extend(fresh_opportunities[:5])  # Limit to avoid overwhelming
                st.success(f"🆕 Added {len(fresh_opportunities)} fresh opportunities")
        
        return formatted_opportunities

    def _start_background_update(self, goal, keywords, country, user_id):
        """Start background scraping to update database (non-blocking)"""
        
        # Check if background update is needed (avoid too frequent updates)
        if self._should_run_background_update(country):
            
            # Show user that background update is happening
            with st.container():
                st.info("🔄 Background database update started - finding new scholarships...")
                
            # Start background thread
            def background_update():
                try:
                    self._perform_background_scraping(goal, keywords, country)
                except Exception as e:
                    print(f"Background update error: {e}")  # Log error but don't break UI
            
            # Run in background thread
            thread = threading.Thread(target=background_update, daemon=True)
            thread.start()
            
            # Update last background run time
            self._update_background_timestamp(country)
    
    def _should_run_background_update(self, country):
        """Check if background update should run based on timing and cache freshness"""
        
        # Check cache metadata for last update time
        cache_age = self.cache.get_cache_age(country)
        
        # ENHANCED: More aggressive background updating
        # Run background update if:
        # 1. Cache is older than 3 hours (reduced from 6), OR
        # 2. Cache has very few country-specific results, OR  
        # 3. This is the first search of the day, OR
        # 4. User has added custom sites recently
        
        if cache_age > 3:  # Hours - MORE AGGRESSIVE (was 6)
            return True
        
        if country:
            country_count = self.cache.get_scholarship_count_by_country(country)
            if country_count < 5:  # ENHANCED: Need at least 5 country-specific results (was 3)
                return True
        
        # ENHANCED: Always run if very few total scholarships
        total_count = self.cache.get_total_scholarship_count()
        if total_count < 20:  # NEW: Ensure minimum scholarship pool
            return True
        
        return False
    
    def _perform_background_scraping(self, goal, keywords, country):
        """ENHANCED: Perform comprehensive background scraping to update database"""
        
        print(f"🔄 Starting ENHANCED background scraping for {goal} in {country}")
        
        # ENHANCED: More comprehensive target sites
        target_sites = []
        
        # Add MORE country-specific sites (increased from 3 to 5)
        if country and country in self.country_scholarship_sites:
            target_sites.extend(self.country_scholarship_sites[country][:5])  # Top 5 for this country
        
        # Add MORE international sites (increased coverage)
        international_sites = [
            'https://www.scholars4dev.com/',
            'https://www.opportunitiesforafricans.com/',
            'https://www.afterschoolafrica.com/',
            'https://www.scholarshipportal.com/',
            'https://www.studyportals.com/',
            'https://www.scholarships.com/'
        ]
        target_sites.extend(international_sites[:4])  # Add 4 international sites
        
        # ENHANCED: Scrape custom user sites too
        try:
            custom_sites = self.db_manager.get_popular_custom_sites(limit=3)
            target_sites.extend([site['url'] for site in custom_sites])
        except Exception:
            pass
        
        # Scrape and update cache
        new_scholarships = []
        
        for i, site in enumerate(target_sites[:8]):  # ENHANCED: Up to 8 sites (was 5)
            try:
                print(f"📡 Background scraping ({i+1}/{min(len(target_sites), 8)}): {site}")
                
                # Use enhanced scraping with anti-bot measures
                site_scholarships = self._scrape_single_site_enhanced(site, goal, keywords)
                
                if site_scholarships:
                    new_scholarships.extend(site_scholarships)
                    print(f"✅ Found {len(site_scholarships)} scholarships from {site}")
                
                # ENHANCED: Shorter delays for background (was 2-5, now 1-3)
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"⚠️ Background scraping failed for {site}: {e}")
                continue
        
        # Add new scholarships to cache
        if new_scholarships:
            formatted_scholarships = [{
                'title': sch['title'],
                'description': sch['description'],
                'amount': sch['amount'],
                'deadline': sch['deadline'],
                'category': sch['category'],
                'source': sch['source'],
                'goal_type': goal,
                'country': country or 'International',
                'priority': 2  # Higher priority for background finds
            } for sch in new_scholarships]
            
            self.cache.add_scholarships(formatted_scholarships)
            print(f"🎉 ENHANCED background update complete: {len(new_scholarships)} new scholarships added")
        
        # ENHANCED: More thorough cleanup
        self.cache.cleanup_expired_scholarships(days_old=21)  # Remove older than 3 weeks
        self.cache.remove_duplicate_scholarships()  # NEW: Remove duplicates
        print("🧹 Enhanced cleanup: removed expired and duplicate scholarships")

    def _update_background_timestamp(self, country):
        """Update timestamp for last background update"""
        # Store in session state or cache metadata
        timestamp_key = f"bg_update_{country or 'global'}"
        if not hasattr(self, '_background_timestamps'):
            self._background_timestamps = {}
        self._background_timestamps[timestamp_key] = datetime.now()

    def _perform_limited_scraping(self, goal, keywords, country):
        """Perform limited scraping for immediate results"""
        try:
            # Quick scrape from 1-2 reliable sources
            target_sites = []
            
            if country and country in self.country_scholarship_sites:
                target_sites.append(self.country_scholarship_sites[country][0])  # First reliable site
            
            # Add one international source
            target_sites.append('https://www.scholars4dev.com/')
            
            results = []
            for site in target_sites[:2]:  # Limit to 2 sites for speed
                try:
                    site_results = self._scrape_single_site_enhanced(site, goal, keywords)
                    results.extend(site_results[:3])  # Max 3 per site
                except:
                    continue
            
            return results[:5]  # Max 5 total
        except:
            return []

    def scrape_single_site(self, url, goal="student", country=None, max_scholarships=10):
        """Immediately scrape a single website for scholarships"""
        try:
            st.info(f"🕷️ Scraping {url}...")
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Apply anti-bot measures
            self._apply_anti_bot_delay()
            self._rotate_user_agent()
            
            # Get the page content
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            scholarships = []
            
            # Generic scholarship extraction patterns
            scholarship_patterns = [
                # Look for common scholarship indicators
                {'tag': 'div', 'class_patterns': ['scholarship', 'opportunity', 'grant', 'funding']},
                {'tag': 'article', 'class_patterns': ['post', 'entry', 'item']},
                {'tag': 'li', 'class_patterns': ['scholarship', 'opportunity']},
                {'tag': 'h2', 'text_patterns': ['scholarship', 'grant', 'award']},
                {'tag': 'h3', 'text_patterns': ['scholarship', 'grant', 'award']},
            ]
            
            for pattern in scholarship_patterns:
                if len(scholarships) >= max_scholarships:
                    break
                    
                elements = self._find_elements_by_pattern(soup, pattern)
                for elem in elements[:5]:  # Limit per pattern
                    try:
                        scholarship = self._extract_scholarship_from_element(elem, url, goal, country)
                        if scholarship and scholarship not in scholarships:
                            scholarships.append(scholarship)
                    except Exception:
                        continue
            
            # Save to cache for future searches
            if scholarships:
                self.cache.add_scholarships([{
                    'title': s['title'],
                    'description': s['description'],
                    'amount': s['amount'],
                    'deadline': s['deadline'],
                    'category': s['category'],
                    'source': s['source'],
                    'goal_type': goal,
                    'country': country or 'International',
                    'priority': 4  # High priority for fresh scraping
                } for s in scholarships])
            
            st.success(f"✅ Successfully scraped {len(scholarships)} scholarships from {url}")
            return scholarships
            
        except Exception as e:
            st.error(f"❌ Failed to scrape {url}: {str(e)}")
            return []
    
    def _find_elements_by_pattern(self, soup, pattern):
        """Find elements matching scholarship patterns"""
        elements = []
        
        if pattern['tag'] in ['div', 'article', 'li']:
            # Search by class patterns
            for class_pattern in pattern.get('class_patterns', []):
                found = soup.find_all(pattern['tag'], class_=re.compile(class_pattern, re.I))
                elements.extend(found)
        
        elif pattern['tag'] in ['h2', 'h3']:
            # Search by text patterns in headings
            for text_pattern in pattern.get('text_patterns', []):
                found = soup.find_all(pattern['tag'], string=re.compile(text_pattern, re.I))
                elements.extend(found)
        
        return elements[:10]  # Limit results
    
    def _extract_scholarship_from_element(self, element, source_url, goal, country):
        """Extract scholarship data from a single element"""
        
        # Try to find title
        title = ""
        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
        if title_elem:
            title = title_elem.get_text(strip=True)
        elif element.name in ['h1', 'h2', 'h3', 'h4']:
            title = element.get_text(strip=True)
        else:
            # Fallback: use first few words
            text = element.get_text(strip=True)
            title = ' '.join(text.split()[:8]) + "..." if len(text.split()) > 8 else text
        
        if not title or len(title) < 10:
            return None
        
        # Extract description
        description = element.get_text(strip=True)[:300] + "..." if len(element.get_text(strip=True)) > 300 else element.get_text(strip=True)
        
        # Try to extract amount (look for money patterns)
        amount = "Amount not specified"
        money_patterns = [r'\$[\d,]+', r'USD?\s*[\d,]+', r'€[\d,]+', r'£[\d,]+', r'UGX\s*[\d,]+']
        for pattern in money_patterns:
            match = re.search(pattern, description, re.I)
            if match:
                amount = match.group()
                break
        
        # Try to extract deadline
        deadline = "Check website for deadline"
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, description, re.I)
            if match:
                deadline = match.group()
                break
        
        # Determine category based on keywords
        category = "General"
        if any(word in description.lower() for word in ['engineering', 'technology', 'computer']):
            category = "STEM"
        elif any(word in description.lower() for word in ['business', 'mba', 'management']):
            category = "Business"
        elif any(word in description.lower() for word in ['medical', 'medicine', 'health']):
            category = "Medical"
        elif any(word in description.lower() for word in ['art', 'creative', 'design']):
            category = "Arts"
        
        return {
            'title': title,
            'description': description,
            'amount': amount,
            'deadline': deadline,
            'category': category,
            'source': source_url,
            'goal_type': goal,
            'country': country or 'International'
        }

    def perform_aggressive_search(self, goal="student", keywords=None, country=None, max_sites=5):
        """Perform aggressive real-time scraping for immediate results"""
        
        st.info("🚀 Performing aggressive real-time scholarship search...")
        
        # Get target sites for aggressive scraping
        target_sites = []
        
        # Add country-specific sites (prioritize)
        if country and country in self.country_scholarship_sites:
            target_sites.extend(self.country_scholarship_sites[country][:3])
        
        # Add international sites
        international_sites = [
            'https://www.scholars4dev.com/',
            'https://www.opportunitiesforafricans.com/',
            'https://www.afterschoolafrica.com/scholarships/'
        ]
        target_sites.extend(international_sites[:max_sites - len(target_sites)])
        
        all_scholarships = []
        
        for i, site in enumerate(target_sites[:max_sites]):
            try:
                st.info(f"🕷️ Scraping site {i+1}/{len(target_sites[:max_sites])}: {site}")
                
                site_scholarships = self.scrape_single_site(site, goal, country, max_scholarships=5)
                all_scholarships.extend(site_scholarships)
                
                # Show progress
                if site_scholarships:
                    st.success(f"✅ Found {len(site_scholarships)} scholarships from {site}")
                
                # Anti-bot delay between sites
                if i < len(target_sites) - 1:
                    time.sleep(random.uniform(2, 4))
                    
            except Exception as e:
                st.warning(f"⚠️ Could not scrape {site}: {str(e)}")
                continue
        
        st.success(f"🎉 Aggressive search complete! Found {len(all_scholarships)} fresh scholarships")
        return all_scholarships

    def update_session_headers(self):
        """Update the session headers with a new random user agent and referrer."""
        import random
        from .config import USER_AGENTS, REFERRERS, BROWSER_HEADERS
        self.current_user_agent = random.choice(USER_AGENTS)
        headers = BROWSER_HEADERS.copy()
        headers['User-Agent'] = self.current_user_agent
        headers['Referer'] = random.choice(REFERRERS)
        self.session.headers.update(headers)
        # Optionally rotate cookies or clear session if needed
        self.session_persistence['user_agent_rotations'] += 1
    
    def _rotate_user_agent(self):
        """Rotate user agent for anti-bot protection"""
        self.session_persistence['user_agent_rotations'] += 1
        
        # Rotate every 5-8 requests
        if self.session_persistence['user_agent_rotations'] % random.randint(5, 8) == 0:
            self.update_session_headers()
    
    def _apply_anti_bot_delay(self):
        """Apply intelligent delays to avoid bot detection"""
        
        # Base delay between requests
        base_delay = random.uniform(MIN_DELAY, MAX_DELAY)
        
        # Additional delay based on request frequency
        if self.session_persistence['total_requests'] > 10:
            frequency_delay = random.uniform(1, 3)
            base_delay += frequency_delay
        
        # Random human-like pauses
        if random.random() < 0.1:  # 10% chance of longer pause
            base_delay += random.uniform(5, 10)
        
        time.sleep(base_delay)
        self.session_persistence['total_requests'] += 1
