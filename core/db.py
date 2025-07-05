import sqlite3
import json
from datetime import datetime
from .config import DATABASE_FILE

class DatabaseManager:
    """Manages scholarship database"""
    def __init__(self, db_file=DATABASE_FILE):
        self.db_file = db_file
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scholarships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                amount TEXT,
                source TEXT,
                category TEXT,
                target_audience TEXT,
                scraped_at DATETIME,
                UNIQUE(title, source)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                added_by TEXT,
                added_at DATETIME,
                last_scraped DATETIME,
                status TEXT,
                is_public INTEGER DEFAULT 0,
                popularity INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        ''')
        conn.commit()
        conn.close()

    def add_scholarships(self, scholarships):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        added_count = 0
        for scholarship in scholarships:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO scholarships 
                    (title, description, deadline, amount, source, category, target_audience, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scholarship.get('title', ''),
                    scholarship.get('description', ''),
                    scholarship.get('deadline', ''),
                    scholarship.get('amount', ''),
                    scholarship.get('source', ''),
                    scholarship.get('category', ''),
                    scholarship.get('target_audience', ''),
                    scholarship.get('scraped_at', datetime.now().isoformat())
                ))
                added_count += 1
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        conn.close()
        return added_count

    def get_scholarships(self, goal=None, keywords=None, limit=50):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        query = "SELECT * FROM scholarships WHERE 1=1"
        params = []
        if goal and goal != "all":
            query += " AND (target_audience LIKE ? OR category LIKE ?)"
            params.extend([f"%{goal}%", f"%{goal}%"])
        if keywords:
            for keyword in keywords:
                query += " AND (title LIKE ? OR description LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
        query += " ORDER BY scraped_at DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        columns = ['id', 'title', 'description', 'deadline', 'amount', 'source', 'category', 'target_audience', 'scraped_at']
        return [dict(zip(columns, row)) for row in results]

    def add_custom_site(self, url, user_id, is_public=False):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO custom_sites (url, added_by, added_at, status, is_public, popularity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, user_id, datetime.now().isoformat(), 'active', int(is_public), 1))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            cursor.execute('''
                UPDATE custom_sites SET popularity = popularity + 1
                WHERE url = ?
            ''', (url,))
            conn.commit()
            conn.close()
            return False

    def get_custom_sites(self, user_id=None, include_public=True):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        if user_id and include_public:
            cursor.execute('''
                SELECT url, popularity FROM custom_sites 
                WHERE (added_by = ? OR is_public = 1) AND status = 'active'
                ORDER BY popularity DESC
            ''', (user_id,))
        elif user_id:
            cursor.execute('''
                SELECT url, popularity FROM custom_sites 
                WHERE added_by = ? AND status = 'active'
                ORDER BY popularity DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT url, popularity FROM custom_sites 
                WHERE is_public = 1 AND status = 'active'
                ORDER BY popularity DESC
            ''')
        results = [{'url': row[0], 'popularity': row[1]} for row in cursor.fetchall()]
        conn.close()
        return results

    def get_user_custom_urls(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT url, popularity FROM custom_sites 
            WHERE added_by = ? AND status = 'active'
            ORDER BY added_at DESC
        ''', (user_id,))
        results = [{'url': row[0], 'popularity': row[1]} for row in cursor.fetchall()]
        conn.close()
        return results

    def save_user_profile(self, user_id, profile_data):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles (user_id, profile_data, created_at, updated_at)
            VALUES (?, ?, COALESCE((SELECT created_at FROM user_profiles WHERE user_id = ?), ?), ?)
        ''', (user_id, json.dumps(profile_data), user_id, datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_user_profile(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT profile_data FROM user_profiles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return json.loads(result[0])
        return {}
