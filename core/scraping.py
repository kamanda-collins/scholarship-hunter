import requests
from bs4 import BeautifulSoup
import re
import time
import random
import streamlit as st
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import hashlib
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
        """Fast search using intelligent caching with optional live scraping"""
        
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
        
        # Step 2: Optional background refresh (if enabled)
        if len(formatted_opportunities) < 10:  # Only scrape if cache is sparse
            st.info("🔄 Cache has limited results. Performing targeted live scraping...")
            
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
                    'country': country or 'International',
                    'keywords': ','.join(keywords) if keywords else '',
                    'goal_type': goal,
                    'priority': 2 if country else 1
                } for opp in fresh_opportunities])
                
                formatted_opportunities.extend(fresh_opportunities)
                st.success(f"✅ Added {len(fresh_opportunities)} fresh scholarships to results")
        
        # Remove duplicates and sort by priority
        seen_titles = set()
        unique_opportunities = []
        for opp in formatted_opportunities:
            title_key = opp['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_opportunities.append(opp)
        
        # Sort by priority (country-specific first)
        unique_opportunities.sort(key=lambda x: (
            -x.get('priority', 1),  # Higher priority first
            x['title']  # Then alphabetical
        ))
        
        return unique_opportunities[:50]  # Return top 50 results

    def mimic_human_behavior(self):
        """Add random human-like behaviors to avoid bot detection"""
        # Occasionally clear cookies (like a human might)
        if random.random() < 0.1:  # 10% chance
            self.session.cookies.clear()
            st.info("🍪 Cleared cookies (human behavior)")
        
        # Randomly update headers
        if random.random() < 0.3:  # 30% chance
            self.update_session_headers()
            st.info("🔄 Updated browser headers")
        
        # Simulate reading time
        if random.random() < 0.2:  # 20% chance
            read_time = random.uniform(1, 3)
            st.info(f"📖 Simulating reading time: {read_time:.1f}s")
            time.sleep(read_time)

    def update_session_headers(self):
        """Update session headers with realistic browser behavior"""
        # Use the predefined browser headers and add random referrer
        referrer = random.choice(REFERRERS)
        
        self.session.headers.update({
            'User-Agent': self.current_user_agent,
            'Referer': referrer,
            **BROWSER_HEADERS  # Unpack the browser headers dictionary
        })

    def adaptive_retry_strategy(self, response_code, attempt):
        """Adaptive retry strategy based on response codes"""
        if response_code == 403:
            # Forbidden - likely bot detection
            self.rotate_user_agent()
            return random.uniform(10, 20)  # Long wait
        elif response_code == 429:
            # Rate limited
            return 15 + (attempt * 5)  # Exponential backoff
        elif response_code == 503:
            # Service unavailable
            return random.uniform(5, 15)
        else:
            # Other errors
            return random.uniform(2, 8)

    def intelligent_delay(self, base_delay=None):
        """Enhanced intelligent delay with human-like patterns"""
        if base_delay is None:
            base_delay = random.uniform(MIN_DELAY, MAX_DELAY)
        
        # Increase delay based on recent activity patterns
        total_recent_requests = sum(1 for t in self.last_request_time.values() 
                                  if datetime.now() - t < timedelta(minutes=5))
        
        # Progressive delay scaling
        if total_recent_requests > 25:
            base_delay *= 2.5  # Much longer delay for heavy activity
            st.info("🐌 Heavy activity detected - using longer delays")
        elif total_recent_requests > 15:
            base_delay *= 1.8  # Moderate scaling
            st.info("⏱️ Moderate activity - adjusting delays")
        elif total_recent_requests > 8:
            base_delay *= 1.3  # Light scaling
        
        # Add human-like variation patterns
        if random.random() < 0.1:  # 10% chance for a "thinking" pause
            thinking_delay = random.uniform(2, 8)
            st.info(f"🤔 Taking a moment to think... ({thinking_delay:.1f}s)")
            time.sleep(thinking_delay)
        
        # Add time-of-day awareness (simulate human browsing patterns)
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours - faster browsing
            base_delay *= 0.8
        elif 22 <= current_hour or current_hour <= 6:  # Late night/early morning - slower
            base_delay *= 1.4
            
        # Ensure minimum human-like delay
        base_delay = max(base_delay, 0.5)
        
        time.sleep(base_delay)
        return base_delay

    def get_country_specific_sites(self, country):
        """Get scholarship sites specific to a country"""
        country_sites = self.country_scholarship_sites.get(country, [])
        international_sites = self.country_scholarship_sites.get('International', [])
        
        # Combine country-specific and international sites
        all_sites = country_sites + international_sites[:3]  # Limit international sites
        return all_sites

    def remove_duplicate_opportunities(self, opportunities):
        """Remove duplicate opportunities based on title similarity"""
        if not opportunities:
            return []
        
        unique_opportunities = []
        seen_titles = set()
        
        for opp in opportunities:
            title = opp['title'].lower().strip()
            # Create a simplified version of the title for comparison
            simplified_title = re.sub(r'[^\w\s]', '', title)
            simplified_title = ' '.join(simplified_title.split())
            
            # Check if we've seen a very similar title
            is_duplicate = False
            for seen_title in seen_titles:
                # Calculate similarity (simple approach)
                if len(simplified_title) > 10 and len(seen_title) > 10:
                    if simplified_title in seen_title or seen_title in simplified_title:
                        is_duplicate = True
                        break
                elif simplified_title == seen_title:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_opportunities.append(opp)
                seen_titles.add(simplified_title)
        
        return unique_opportunities

    def _perform_limited_scraping(self, goal, keywords, country, max_sites=3):
        """Perform limited scraping from most reliable sources"""
        opportunities = []
        
        # Select only the most reliable sites for quick scraping
        reliable_sites = [
            "https://www.scholarships.com/",
            "https://www.fastweb.com/",
            "https://www.petersons.com/",
        ]
        
        # Add country-specific sites if available
        if country and hasattr(self, 'country_scholarship_sites'):
            country_sites = self.country_scholarship_sites.get(country, [])[:2]  # Top 2 country sites
            reliable_sites = country_sites + reliable_sites
        
        # Limit to max_sites for speed
        sites_to_try = reliable_sites[:max_sites]
        
        for i, site in enumerate(sites_to_try):
            try:
                # Quick check if we should scrape this source
                if not self.cache.should_scrape_source(site, max_age_hours=6):  # 6 hour cache
                    continue
                
                st.info(f"🔍 Quick scraping: {site} ({i+1}/{len(sites_to_try)})")
                
                # Perform quick scraping with shorter timeouts
                site_opportunities = self._scrape_site_quick(site, keywords)
                
                if site_opportunities:
                    opportunities.extend(site_opportunities[:5])  # Max 5 per site
                    self.cache.update_cache_metadata(site, success=True)
                else:
                    self.cache.update_cache_metadata(site, success=False)
                
                # Quick delay between sites
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                st.warning(f"⚠️ Quick scraping failed for {site}: {str(e)[:50]}")
                self.cache.update_cache_metadata(site, success=False)
                continue
        
        return opportunities[:10]  # Return max 10 fresh results
    
    def _scrape_site_quick(self, url, keywords):
        """Quick scraping with minimal processing"""
        try:
            # Very short timeout for quick results
            response = self.session.get(
                url,
                headers=self._get_stealth_headers(),
                timeout=10,  # Short timeout
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Quick and dirty scholarship extraction
            opportunities = []
            
            # Look for common scholarship patterns
            scholarship_elements = (
                soup.find_all(['div', 'article', 'section'], class_=re.compile(r'scholarship|opportunity|grant', re.I))[:5] +
                soup.find_all(['h2', 'h3', 'h4'], string=re.compile(r'scholarship|grant|award', re.I))[:5]
            )
            
            for elem in scholarship_elements[:5]:  # Max 5 per site for speed
                try:
                    title = self._extract_text(elem, ['h1', 'h2', 'h3', 'h4', 'title']) or "Scholarship Opportunity"
                    description = self._extract_text(elem, ['p', 'div', 'span']) or "Check website for details"
                    
                    # Basic filtering
                    if keywords:
                        text_to_check = (title + " " + description).lower()
                        if not any(keyword.lower() in text_to_check for keyword in keywords):
                            continue
                    
                    opportunities.append({
                        'title': title[:100],  # Truncate for consistency
                        'description': description[:200],
                        'amount': 'Check website',
                        'deadline': 'Check website',
                        'category': 'General',
                        'source': url
                    })
                    
                except Exception:
                    continue
            
            return opportunities
            
        except Exception:
            return []
