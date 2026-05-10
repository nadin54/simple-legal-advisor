import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

class LegalDatabase:
    def __init__(self, db_name='legal_advisor.db'):
        self.db_name = db_name
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT,
                    status TEXT DEFAULT 'Open',
                    priority TEXT DEFAULT 'Medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Legal Advice table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS advice (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER,
                    advice TEXT NOT NULL,
                    advisor_type TEXT DEFAULT 'ML',
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            # Queries log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    category TEXT,
                    helpful INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER,
                    rating INTEGER,
                    comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            conn.commit()

    def create_case(self, title, description, priority='Medium'):
        """Create a new case"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cases (title, description, priority)
                VALUES (?, ?, ?)
            ''', (title, description, priority))
            conn.commit()
            return cursor.lastrowid

    def get_all_cases(self):
        """Get all cases"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cases ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]

    def get_case(self, case_id):
        """Get specific case"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_case(self, case_id, title=None, description=None, category=None, status=None, priority=None, notes=None):
        """Update case"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            values = []
            
            if title:
                updates.append('title = ?')
                values.append(title)
            if description:
                updates.append('description = ?')
                values.append(description)
            if category:
                updates.append('category = ?')
                values.append(category)
            if status:
                updates.append('status = ?')
                values.append(status)
            if priority:
                updates.append('priority = ?')
                values.append(priority)
            if notes:
                updates.append('notes = ?')
                values.append(notes)
            
            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(case_id)
            
            query = f"UPDATE cases SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

    def close_case(self, case_id):
        """Close a case"""
        self.update_case(case_id, status='Closed')

    def add_advice(self, case_id, advice, advisor_type='ML', confidence=0.0):
        """Add advice to case"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO advice (case_id, advice, advisor_type, confidence)
                VALUES (?, ?, ?, ?)
            ''', (case_id, advice, advisor_type, confidence))
            conn.commit()
            return cursor.lastrowid

    def get_case_advice(self, case_id):
        """Get all advice for a case"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM advice WHERE case_id = ? ORDER BY created_at DESC', (case_id,))
            return [dict(row) for row in cursor.fetchall()]

    def log_query(self, query, category):
        """Log a query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO queries (query, category)
                VALUES (?, ?)
            ''', (query, category))
            conn.commit()

    def add_feedback(self, case_id, rating, comments=''):
        """Add user feedback"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (case_id, rating, comments)
                VALUES (?, ?, ?)
            ''', (case_id, rating, comments))
            conn.commit()

    def get_statistics(self):
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as total FROM cases')
            total_cases = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM cases WHERE status='Open'")
            open_cases = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM cases WHERE status='Closed'")
            closed_cases = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(*) as total FROM advice')
            total_advice = cursor.fetchone()['total']
            
            cursor.execute('SELECT category, COUNT(*) as count FROM cases WHERE category IS NOT NULL GROUP BY category')
            categories = {row['category']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_cases': total_cases,
                'open_cases': open_cases,
                'closed_cases': closed_cases,
                'total_advice': total_advice,
                'categories': categories
            }
