"""
Task Store - SQLite-based task history storage
Part of memory system for learning from past tasks
"""

import os
import sqlite3
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class TaskRecord:
    """A record of a completed task."""
    id: int
    goal: str
    goal_hash: str
    status: str  # success, failure, partial
    files_changed: List[str]
    error: Optional[str]
    duration_ms: float
    model_used: str
    provider_used: str
    passes_used: int
    created_at: str
    metadata: Dict[str, Any]


class TaskStore:
    """
    SQLite-based task history store.
    Stores task history for pattern learning.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            home = os.path.expanduser("~")
            neuro_dir = os.path.join(home, ".neuro")
            os.makedirs(neuro_dir, exist_ok=True)
            db_path = os.path.join(neuro_dir, "task_history.db")
        
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                goal_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                files_changed TEXT,  -- JSON list
                error TEXT,
                duration_ms REAL,
                model_used TEXT,
                provider_used TEXT,
                passes_used INTEGER,
                created_at TEXT NOT NULL,
                metadata TEXT  -- JSON dict
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_goal_hash ON tasks(goal_hash)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON tasks(created_at)
        """)
        
        self.conn.commit()
    
    def add_task(
        self,
        goal: str,
        status: str,
        files_changed: List[str],
        error: Optional[str] = None,
        duration_ms: float = 0,
        model_used: str = "",
        provider_used: str = "",
        passes_used: int = 1,
        metadata: Optional[Dict] = None,
    ) -> int:
        """Add a task record to the store."""
        goal_hash = hashlib.md5(goal.encode()).hexdigest()[:16]
        
        self.conn.execute("""
            INSERT INTO tasks (
                goal, goal_hash, status, files_changed, error,
                duration_ms, model_used, provider_used, passes_used,
                created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            goal,
            goal_hash,
            status,
            json.dumps(files_changed),
            error,
            duration_ms,
            model_used,
            provider_used,
            passes_used,
            datetime.now().isoformat(),
            json.dumps(metadata or {}),
        ))
        
        self.conn.commit()
        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    def get_similar(
        self,
        goal: str,
        limit: int = 5,
        status_filter: Optional[str] = None,
    ) -> List[TaskRecord]:
        """Get similar tasks based on goal hash."""
        goal_hash = hashlib.md5(goal.encode()).hexdigest()[:16]
        
        query = """
            SELECT * FROM tasks 
            WHERE goal_hash = ? OR goal LIKE ?
        """
        params = [goal_hash, f"%{goal[:50]}%"]
        
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        rows = self.conn.execute(query, params).fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_recent(self, limit: int = 20) -> List[TaskRecord]:
        """Get recent tasks."""
        rows = self.conn.execute("""
            SELECT * FROM tasks 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_failures(self, limit: int = 50) -> List[TaskRecord]:
        """Get recent failure patterns."""
        rows = self.conn.execute("""
            SELECT * FROM tasks 
            WHERE status IN ('failure', 'partial')
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about task history."""
        cursor = self.conn.execute
        
        total = cursor("SELECT COUNT(*) FROM tasks").fetchone()[0]
        success = cursor("SELECT COUNT(*) FROM tasks WHERE status = 'success'").fetchone()[0]
        failure = cursor("SELECT COUNT(*) FROM tasks WHERE status = 'failure'").fetchone()[0]
        partial = cursor("SELECT COUNT(*) FROM tasks WHERE status = 'partial'").fetchone()[0]
        
        avg_duration = cursor("SELECT AVG(duration_ms) FROM tasks").fetchone()[0] or 0
        
        recent = datetime.now() - timedelta(days=7)
        recent_count = cursor(
            "SELECT COUNT(*) FROM tasks WHERE created_at > ?",
            (recent.isoformat(),)
        ).fetchone()[0]
        
        return {
            "total_tasks": total,
            "success_count": success,
            "failure_count": failure,
            "partial_count": partial,
            "success_rate": success / total if total > 0 else 0,
            "avg_duration_ms": avg_duration,
            "recent_week_count": recent_count,
        }
    
    def search(self, query: str, limit: int = 10) -> List[TaskRecord]:
        """Search tasks by goal content."""
        rows = self.conn.execute("""
            SELECT * FROM tasks 
            WHERE goal LIKE ?
            ORDER BY created_at DESC 
            LIMIT ?
        """, (f"%{query}%", limit)).fetchall()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_common_patterns(self, min_occurrences: int = 2) -> List[Dict]:
        """Find common failure patterns."""
        patterns = self.conn.execute("""
            SELECT error, COUNT(*) as count 
            FROM tasks 
            WHERE error IS NOT NULL AND status = 'failure'
            GROUP BY error 
            HAVING COUNT(*) >= ?
            ORDER BY count DESC
        """, (min_occurrences,)).fetchall()
        
        return [{"error": p["error"], "count": p["count"]} for p in patterns]
    
    def _row_to_record(self, row: sqlite3.Row) -> TaskRecord:
        """Convert a database row to TaskRecord."""
        return TaskRecord(
            id=row["id"],
            goal=row["goal"],
            goal_hash=row["goal_hash"],
            status=row["status"],
            files_changed=json.loads(row["files_changed"] or "[]"),
            error=row["error"],
            duration_ms=row["duration_ms"],
            model_used=row["model_used"] or "",
            provider_used=row["provider_used"] or "",
            passes_used=row["passes_used"],
            created_at=row["created_at"],
            metadata=json.loads(row["metadata"] or "{}"),
        )
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience function
def get_store() -> TaskStore:
    """Get the default task store."""
    return TaskStore()


def add_task_record(**kwargs) -> int:
    """Quick function to add a task record."""
    store = get_store()
    task_id = store.add_task(**kwargs)
    store.close()
    return task_id


def get_similar_tasks(goal: str, limit: int = 5) -> List[TaskRecord]:
    """Quick function to find similar tasks."""
    store = get_store()
    tasks = store.get_similar(goal, limit)
    store.close()
    return tasks
