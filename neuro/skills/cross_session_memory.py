"""
Cross-Session Memory System - Learning across sessions
Competitor: Manus Memory across sessions

Features:
- SQLite-based persistent storage
- Task outcome learning
- Pattern recognition
- Cross-session context transfer
- Learning recommendations
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class LearnedPattern:
    """A learned pattern from past experiences"""
    pattern_id: str
    pattern_type: str  # 'success', 'failure', 'technique'
    description: str
    context: str  # When this pattern applies
    occurrence_count: int
    success_rate: float
    recommendation: str
    created_at: str
    last_used: str


@dataclass
class SessionContext:
    """Context transferred between sessions"""
    session_id: str
    user_preferences: Dict[str, Any]
    learned_skills: List[str]
    ongoing_tasks: List[str]
    completed_count: int
    failed_count: int


class CrossSessionMemory:
    """
    Cross-Session Memory System
    
    Features:
    - SQLite-based persistent storage
    - Task outcome learning
    - Pattern recognition from past experiences
    - Cross-session context preservation
    - Intelligent recommendations
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / ".neuro" / "cross_session.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                description TEXT NOT NULL,
                context TEXT NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.5,
                recommendation TEXT,
                created_at TEXT NOT NULL,
                last_used TEXT NOT NULL,
                tags TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                task_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                context_json TEXT
            )
        ''')
        
        # Task history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                task_description TEXT NOT NULL,
                task_type TEXT,
                success BOOLEAN,
                error_message TEXT,
                solution TEXT,
                duration_seconds REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Learned skills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                skill_type TEXT NOT NULL,
                description TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                last_success TEXT,
                complexity TEXT DEFAULT 'medium'
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def learn_from_outcome(
        self,
        task: str,
        task_type: Optional[str],
        success: bool,
        error: Optional[str] = None,
        solution: Optional[str] = None,
        duration: Optional[float] = None
    ):
        """
        Learn from task outcome to improve future performance.
        
        Args:
            task: Task description
            task_type: Type of task (e.g., 'coding', 'debug', 'refactor')
            success: Whether task succeeded
            error: Error message if failed
            solution: How it was solved (if applicable)
            duration: Time taken
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get current session
        session_id = self._get_or_create_session()
        
        # Record task
        cursor.execute('''
            INSERT INTO task_history 
            (session_id, task_description, task_type, success, error_message, solution, duration_seconds, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, task, task_type or 'unknown', success, error, solution, duration, datetime.now().isoformat()))
        
        # Update pattern based on outcome
        if success:
            self._update_success_pattern(task, task_type, solution)
        else:
            self._update_failure_pattern(task, task_type, error)
        
        # Update session stats
        cursor.execute('''
            UPDATE sessions SET 
                task_count = task_count + 1,
                success_count = success_count + ?
            WHERE id = ?
        ''', (1 if success else 0, session_id))
        
        conn.commit()
        conn.close()
    
    def _get_or_create_session(self) -> str:
        """Get or create current session ID"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO sessions (id, started_at, task_count, success_count, failure_count)
            VALUES (?, ?, 0, 0, 0)
        ''', (session_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def _update_success_pattern(
        self,
        task: str,
        task_type: Optional[str],
        solution: Optional[str]
    ):
        """Update pattern when task succeeds"""
        if not task_type:
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute('''
            SELECT id, occurrence_count, success_rate FROM patterns 
            WHERE context = ? AND pattern_type = 'success'
        ''', (task_type,))
        
        row = cursor.fetchone()
        
        if row:
            pattern_id, count, rate = row
            new_count = count + 1
            new_rate = (rate * count + 1) / new_count
            
            cursor.execute('''
                UPDATE patterns SET 
                    occurrence_count = ?,
                    success_rate = ?,
                    last_used = ?
                WHERE id = ?
            ''', (new_count, new_rate, datetime.now().isoformat(), pattern_id))
        else:
            pattern_id = f"pattern_{datetime.now().timestamp()}"
            
            cursor.execute('''
                INSERT INTO patterns 
                (id, pattern_type, description, context, occurrence_count, success_rate, recommendation, created_at, last_used)
                VALUES (?, 'success', ?, ?, 1, 1.0, ?, ?, ?)
            ''', (
                pattern_id,
                task[:200],
                task_type,
                solution[:500] if solution else "Keep doing what works",
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def _update_failure_pattern(
        self,
        task: str,
        task_type: Optional[str],
        error: Optional[str]
    ):
        """Update pattern when task fails"""
        if not task_type or not error:
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check if similar failure pattern exists
        error_keywords = ' '.join(error.lower().split()[:5])
        
        cursor.execute('''
            SELECT id, occurrence_count, success_rate FROM patterns 
            WHERE description LIKE ? AND pattern_type = 'failure'
        ''', (f'%{error_keywords[:50]}%',))
        
        row = cursor.fetchone()
        
        if row:
            pattern_id, count, rate = row
            new_count = count + 1
            new_rate = (rate * count + 0) / new_count  # 0 for failure
            
            cursor.execute('''
                UPDATE patterns SET 
                    occurrence_count = ?,
                    success_rate = ?,
                    last_used = ?
                WHERE id = ?
            ''', (new_count, new_rate, datetime.now().isoformat(), pattern_id))
        else:
            pattern_id = f"fail_{datetime.now().timestamp()}"
            
            cursor.execute('''
                INSERT INTO patterns 
                (id, pattern_type, description, context, occurrence_count, success_rate, recommendation, created_at, last_used)
                VALUES (?, 'failure', ?, ?, 1, 0.0, ?, ?, ?)
            ''', (
                pattern_id,
                error[:200] if error else task[:200],
                task_type,
                f"Avoid this approach. Error: {error[:100]}" if error else "Try different method",
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_recommendations(self, task_type: str) -> List[str]:
        """Get recommendations for a task type based on past learning"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        recommendations = []
        
        # Get success patterns
        cursor.execute('''
            SELECT recommendation FROM patterns 
            WHERE context = ? AND pattern_type = 'success'
            ORDER BY success_rate DESC, occurrence_count DESC
            LIMIT 5
        ''', (task_type,))
        
        for row in cursor.fetchall():
            if row[0]:
                recommendations.append(f"✓ {row[0]}")
        
        # Get failure patterns to avoid
        cursor.execute('''
            SELECT description, recommendation FROM patterns 
            WHERE context = ? AND pattern_type = 'failure'
            ORDER BY occurrence_count DESC
            LIMIT 3
        ''', (task_type,))
        
        for row in cursor.fetchall():
            if row[1]:
                recommendations.append(f"✗ Avoid: {row[1]}")
        
        conn.close()
        
        return recommendations if recommendations else [
            f"No prior experience with {task_type}. Starting fresh."
        ]
    
    def get_session_context(self) -> SessionContext:
        """Get context to transfer to new session"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get most recent session
        cursor.execute('''
            SELECT id, task_count, success_count, failure_count, context_json
            FROM sessions ORDER BY started_at DESC LIMIT 1
        ''')
        
        row = cursor.fetchone()
        
        if not row:
            return SessionContext(
                session_id="new",
                user_preferences={},
                learned_skills=[],
                ongoing_tasks=[],
                completed_count=0,
                failed_count=0
            )
        
        session_id, task_count, success, failure, context_json = row
        
        # Get learned skills
        cursor.execute('''
            SELECT skill_name FROM learned_skills 
            WHERE success_count > failure_count
            ORDER BY success_count DESC
            LIMIT 20
        ''')
        
        skills = [row[0] for row in cursor.fetchall()]
        
        # Get ongoing tasks from recent history
        cursor.execute('''
            SELECT task_description FROM task_history 
            WHERE success = 0 ORDER BY created_at DESC LIMIT 5
        ''')
        
        ongoing = [row[0][:100] for row in cursor.fetchall()]
        
        conn.close()
        
        preferences = {}
        if context_json:
            try:
                preferences = json.loads(context_json)
            except:
                pass
        
        return SessionContext(
            session_id=session_id,
            user_preferences=preferences,
            learned_skills=skills,
            ongoing_tasks=ongoing,
            completed_count=task_count,
            failed_count=failure
        )
    
    def save_preference(self, key: str, value: Any):
        """Save user preference"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, json.dumps(value), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            try:
                return json.loads(row[0])
            except:
                return row[0]
        
        return default
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {}
        
        # Total patterns
        cursor.execute('SELECT COUNT(*) FROM patterns')
        stats['total_patterns'] = cursor.fetchone()[0]
        
        # Success patterns
        cursor.execute("SELECT COUNT(*) FROM patterns WHERE pattern_type = 'success'")
        stats['success_patterns'] = cursor.fetchone()[0]
        
        # Failure patterns
        cursor.execute("SELECT COUNT(*) FROM patterns WHERE pattern_type = 'failure'")
        stats['failure_patterns'] = cursor.fetchone()[0]
        
        # Total tasks learned
        cursor.execute('SELECT COUNT(*) FROM task_history')
        stats['total_tasks'] = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute('SELECT success FROM task_history WHERE success = 1')
        successes = len(cursor.fetchall())
        cursor.execute('SELECT success FROM task_history')
        total = len(cursor.fetchall())
        stats['overall_success_rate'] = (successes / total * 100) if total > 0 else 0
        
        # Top patterns by success rate
        cursor.execute('''
            SELECT description, success_rate FROM patterns 
            WHERE pattern_type = 'success'
            ORDER BY success_rate DESC LIMIT 5
        ''')
        stats['top_patterns'] = [{'desc': r[0][:50], 'rate': r[1]} for r in cursor.fetchall()]
        
        conn.close()
        
        return stats


def learn_task_outcome(
    task: str,
    success: bool,
    task_type: Optional[str] = None,
    error: Optional[str] = None,
    solution: Optional[str] = None
):
    """Learn from task outcome"""
    memory = CrossSessionMemory()
    memory.learn_from_outcome(task, task_type, success, error, solution)


def get_recommendations_for(task_type: str) -> List[str]:
    """Get recommendations for a task type"""
    memory = CrossSessionMemory()
    return memory.get_recommendations(task_type)


def get_context_for_new_session() -> SessionContext:
    """Get context for starting a new session"""
    memory = CrossSessionMemory()
    return memory.get_session_context()


# Skill functions
@register_skill
def store_learning(
    task: str,
    success: bool,
    task_type: Optional[str] = None,
    error: Optional[str] = None,
    solution: Optional[str] = None
) -> str:
    """
    Store learning from task outcome.
    
    Args:
        task: Task description
        success: Whether task succeeded
        task_type: Type of task
        error: Error message if failed
        solution: How it was solved
    
    Returns:
        Confirmation message
    """
    learn_task_outcome(task, success, task_type, error, solution)
    return f"Learned from {'successful' if success else 'failed'} task: {task[:50]}..."


@register_skill
def recall_learning(task_type: str) -> str:
    """
    Recall learning and get recommendations for a task type.
    
    Args:
        task_type: Type of task to get recommendations for
    
    Returns:
        Recommendations string
    """
    memory = CrossSessionMemory()
    recommendations = memory.get_recommendations(task_type)
    
    if not recommendations or "No prior experience" in recommendations[0]:
        return f"No prior learning for {task_type}. Starting fresh."
    
    return "Recommendations based on past learning:\n" + "\n".join(recommendations)


@register_skill
def get_session_summary() -> str:
    """
    Get summary of past sessions and learning.
    
    Returns:
        Summary of learned patterns and stats
    """
    memory = CrossSessionMemory()
    context = memory.get_session_context()
    stats = memory.get_learning_stats()
    
    summary = [
        "=== CROSS-SESSION MEMORY ===",
        f"Session ID: {context.session_id}",
        f"Tasks Completed: {context.completed_count}",
        f"Success Rate: {stats.get('overall_success_rate', 0):.1f}%",
        f"Patterns Learned: {stats.get('total_patterns', 0)}",
        f"Top Skills: {', '.join(context.learned_skills[:5]) or 'None yet'}",
        "",
        "Recent Recommendations:"
    ]
    
    for pattern in stats.get('top_patterns', [])[:3]:
        summary.append(f"  • {pattern['desc']}... ({pattern['rate']:.0%} success)")
    
    return "\n".join(summary)


@register_skill
def save_user_preference(key: str, value: Any) -> str:
    """
    Save a user preference for cross-session recall.
    
    Args:
        key: Preference name
        value: Preference value (will be JSON serialized)
    
    Returns:
        Confirmation
    """
    memory = CrossSessionMemory()
    memory.save_preference(key, value)
    return f"Saved preference: {key} = {value}"


# Skill metadata
cross_session_memory_meta = {
    'name': 'cross-session-memory',
    'description': 'Persistent memory that learns across sessions with pattern recognition',
    'category': 'memory',
    'keywords': ['memory', 'learning', 'cross-session', 'persistence', 'patterns'],
    'competitor': 'Manus Memory across sessions',
    'free': True
}