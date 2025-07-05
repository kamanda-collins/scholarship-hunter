"""
Shared Scholarship Database with Intelligent Caching
Provides fast access to scholarships with country-specific data
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class ScholarshipCache:
    """Manages shared scholarship database with intelligent caching"""
    
    def __init__(self, db_file="cache/scholarships.db"):
        self.db_file = db_file
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.init_database()
        self.populate_initial_data()
    
    def init_database(self):
        """Initialize the scholarship cache database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Main scholarships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scholarships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                amount TEXT,
                deadline TEXT,
                category TEXT,
                source TEXT,
                country TEXT,
                keywords TEXT,
                goal_type TEXT,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Cache metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT UNIQUE,
                last_scraped TIMESTAMP,
                success_count INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                is_reliable BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_initial_data(self):
        """Populate database with initial scholarship data"""
        if self.get_scholarship_count() > 0:
            return  # Already populated
        
        # Comprehensive scholarship data with focus on Uganda and Africa
        initial_scholarships = [
            # Uganda-specific scholarships
            {
                "title": "Makerere University Excellence Scholarship",
                "description": "Merit-based scholarship for outstanding Ugandan students pursuing undergraduate degrees at Makerere University",
                "amount": "Full tuition + stipend",
                "deadline": "March 15, 2025",
                "category": "Academic Excellence",
                "source": "https://www.mak.ac.ug/scholarships",
                "country": "Uganda",
                "keywords": "undergraduate,excellence,merit,makerere",
                "goal_type": "student",
                "priority": 3
            },
            {
                "title": "Uganda Government Scholarship Scheme",
                "description": "Government-sponsored scholarships for Ugandan citizens in STEM fields",
                "amount": "Full tuition + living allowance",
                "deadline": "April 30, 2025",
                "category": "Government",
                "source": "https://www.education.go.ug/scholarships",
                "country": "Uganda",
                "keywords": "government,stem,science,engineering,technology",
                "goal_type": "student",
                "priority": 3
            },
            {
                "title": "Kampala International University Bursary",
                "description": "Need-based financial assistance for deserving students at KIU",
                "amount": "50-75% tuition coverage",
                "deadline": "June 1, 2025",
                "category": "Financial Aid",
                "source": "https://www.kiu.ac.ug/bursaries",
                "country": "Uganda",
                "keywords": "financial aid,need-based,undergraduate",
                "goal_type": "student",
                "priority": 3
            },
            {
                "title": "Uganda Christian University Scholarship",
                "description": "Academic and leadership scholarships for UCU students",
                "amount": "Varies",
                "deadline": "February 28, 2025",
                "category": "Leadership",
                "source": "https://www.ucu.ac.ug/scholarships",
                "country": "Uganda",
                "keywords": "leadership,academic,christian,undergraduate",
                "goal_type": "student",
                "priority": 3
            },
            
            # East African scholarships
            {
                "title": "East African Community Scholarship",
                "description": "Regional scholarships for students from EAC member countries",
                "amount": "$5,000 - $15,000",
                "deadline": "May 15, 2025",
                "category": "Regional",
                "source": "https://www.eac.int/scholarships",
                "country": "East Africa",
                "keywords": "regional,east africa,undergraduate,graduate",
                "goal_type": "student",
                "priority": 2
            },
            
            # African scholarships
            {
                "title": "Mastercard Foundation Scholars Program",
                "description": "Comprehensive scholarship for academically talented African students",
                "amount": "Full scholarship + mentorship",
                "deadline": "Rolling applications",
                "category": "Foundation",
                "source": "https://mastercardfdn.org/scholars/",
                "country": "Africa",
                "keywords": "mastercard,foundation,african,leadership,undergraduate,graduate",
                "goal_type": "student",
                "priority": 2
            },
            {
                "title": "African Union Scholarship Programme",
                "description": "Continental scholarship program for African students",
                "amount": "Full tuition + allowances",
                "deadline": "March 31, 2025",
                "category": "Continental",
                "source": "https://au.int/en/scholarships",
                "country": "Africa",
                "keywords": "african union,continental,graduate,research",
                "goal_type": "student",
                "priority": 2
            },
            
            # International scholarships accessible to Ugandans
            {
                "title": "Commonwealth Scholarships",
                "description": "UK government scholarships for Commonwealth country citizens including Uganda",
                "amount": "Full funding",
                "deadline": "October 31, 2025",
                "category": "International",
                "source": "https://cscuk.fcdo.gov.uk/",
                "country": "International",
                "keywords": "commonwealth,uk,graduate,research,uganda",
                "goal_type": "student",
                "priority": 1
            },
            {
                "title": "Chevening Scholarships",
                "description": "UK government's global scholarship programme for future leaders",
                "amount": "Full funding + networking",
                "deadline": "November 7, 2025",
                "category": "Leadership",
                "source": "https://www.chevening.org/",
                "country": "International",
                "keywords": "chevening,uk,leadership,graduate,masters",
                "goal_type": "student",
                "priority": 1
            },
            {
                "title": "Fulbright Foreign Student Program",
                "description": "US government scholarship for international students including Ugandans",
                "amount": "Full funding",
                "deadline": "May 15, 2025",
                "category": "International",
                "source": "https://www.fulbright.org/",
                "country": "International",
                "keywords": "fulbright,usa,graduate,research,exchange",
                "goal_type": "student",
                "priority": 1
            },
            
            # Entrepreneurship scholarships
            {
                "title": "YALI Regional Leadership Center Scholarship",
                "description": "Leadership development program for young African entrepreneurs",
                "amount": "Full program coverage",
                "deadline": "Quarterly applications",
                "category": "Entrepreneurship",
                "source": "https://yali.state.gov/",
                "country": "Africa",
                "keywords": "entrepreneurship,leadership,young,african,business",
                "goal_type": "entrepreneur",
                "priority": 2
            },
            {
                "title": "Tony Elumelu Foundation Entrepreneurship Programme",
                "description": "Seed funding and mentorship for African entrepreneurs",
                "amount": "$5,000 seed funding",
                "deadline": "January 31, 2025",
                "category": "Entrepreneurship",
                "source": "https://www.tonyelumelufoundation.org/",
                "country": "Africa",
                "keywords": "entrepreneurship,startup,seed funding,african,business",
                "goal_type": "entrepreneur",
                "priority": 2
            },
            
            # Research scholarships
            {
                "title": "African Institute for Mathematical Sciences Scholarships",
                "description": "Graduate scholarships in mathematical sciences for African students",
                "amount": "Full funding",
                "deadline": "February 28, 2025",
                "category": "Research",
                "source": "https://www.aims.ac.za/",
                "country": "Africa",
                "keywords": "mathematics,science,research,graduate,african",
                "goal_type": "researcher",
                "priority": 2
            },
            
            # Arts scholarships
            {
                "title": "UNESCO-Aschberg Programme for Artists",
                "description": "Residency program for young artists from developing countries",
                "amount": "Residency + stipend",
                "deadline": "Rolling applications",
                "category": "Arts",
                "source": "https://en.unesco.org/",
                "country": "International",
                "keywords": "arts,artist,residency,unesco,cultural",
                "goal_type": "artist",
                "priority": 1
            },
            
            # Nonprofit/social work scholarships
            {
                "title": "Acumen Academy Fellowships",
                "description": "Leadership development for social sector professionals",
                "amount": "Program coverage",
                "deadline": "Multiple deadlines",
                "category": "Social Impact",
                "source": "https://acumenacademy.org/",
                "country": "International",
                "keywords": "social impact,nonprofit,leadership,development",
                "goal_type": "nonprofit",
                "priority": 1
            }
        ]
        
        self.add_scholarships(initial_scholarships)
        print(f"✅ Populated database with {len(initial_scholarships)} scholarships")
    
    def add_scholarships(self, scholarships: List[Dict]):
        """Add multiple scholarships to the database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        for scholarship in scholarships:
            cursor.execute('''
                INSERT OR REPLACE INTO scholarships 
                (title, description, amount, deadline, category, source, country, keywords, goal_type, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scholarship.get('title'),
                scholarship.get('description'),
                scholarship.get('amount'),
                scholarship.get('deadline'),
                scholarship.get('category'),
                scholarship.get('source'),
                scholarship.get('country'),
                scholarship.get('keywords'),
                scholarship.get('goal_type'),
                scholarship.get('priority', 1)
            ))
        
        conn.commit()
        conn.close()
    
    def search_scholarships(self, goal: str = None, keywords: List[str] = None, 
                          country: str = None, limit: int = 50) -> List[Dict]:
        """Search scholarships with intelligent filtering"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Build dynamic query
        query = "SELECT * FROM scholarships WHERE is_active = 1"
        params = []
        
        if goal:
            query += " AND goal_type = ?"
            params.append(goal)
        
        if country:
            # Prioritize country-specific, then regional, then international
            query += " AND (country = ? OR country LIKE '%Africa%' OR country = 'International')"
            params.append(country)
        
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append("(title LIKE ? OR description LIKE ? OR keywords LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            
            if keyword_conditions:
                query += " AND (" + " OR ".join(keyword_conditions) + ")"
        
        # Order by priority (country-specific first), then by creation date
        query += " ORDER BY priority DESC, created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to dictionary format
        columns = [description[0] for description in cursor.description]
        scholarships = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return scholarships
    
    def get_scholarship_count(self) -> int:
        """Get total number of scholarships in cache"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE is_active = 1")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_scholarship_count_by_country(self, country: str = None) -> int:
        """Get number of scholarships by country"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if country:
            # Count scholarships that mention the country in title, description, or category
            cursor.execute("""
                SELECT COUNT(*) FROM scholarships 
                WHERE is_active = 1 AND (
                    LOWER(title) LIKE ? OR 
                    LOWER(description) LIKE ? OR 
                    LOWER(category) LIKE ? OR
                    LOWER(source) LIKE ?
                )
            """, (f'%{country.lower()}%', f'%{country.lower()}%', f'%{country.lower()}%', f'%{country.lower()}%'))
        else:
            cursor.execute("SELECT COUNT(*) FROM scholarships WHERE is_active = 1")
            
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def update_cache_metadata(self, source_url: str, success: bool):
        """Update cache metadata for a source"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO cache_metadata (source_url, last_scraped, success_count, total_attempts)
            VALUES (?, ?, 0, 0)
        ''', (source_url, datetime.now()))
        
        if success:
            cursor.execute('''
                UPDATE cache_metadata 
                SET last_scraped = ?, success_count = success_count + 1, total_attempts = total_attempts + 1
                WHERE source_url = ?
            ''', (datetime.now(), source_url))
        else:
            cursor.execute('''
                UPDATE cache_metadata 
                SET last_scraped = ?, total_attempts = total_attempts + 1
                WHERE source_url = ?
            ''', (datetime.now(), source_url))
        
        conn.commit()
        conn.close()
    
    def should_scrape_source(self, source_url: str, max_age_hours: int = 24) -> bool:
        """Determine if a source should be scraped based on cache age and reliability"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT last_scraped, success_count, total_attempts 
            FROM cache_metadata 
            WHERE source_url = ?
        ''', (source_url,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return True  # Never scraped before
        
        last_scraped, success_count, total_attempts = result
        
        # Parse timestamp
        try:
            last_scraped_dt = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
            age_hours = (datetime.now() - last_scraped_dt).total_seconds() / 3600
            
            # Don't scrape if recently scraped and source is unreliable
            if age_hours < max_age_hours and total_attempts > 0:
                success_rate = success_count / total_attempts
                if success_rate < 0.3:  # Less than 30% success rate
                    return False
            
            return age_hours >= max_age_hours
        except:
            return True
