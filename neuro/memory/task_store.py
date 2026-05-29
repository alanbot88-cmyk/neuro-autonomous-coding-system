"""
Task Store - SQLite-based task history storage
Part of memory system for learning from past tasks

Supports:
- Task history storage and retrieval
- Failure pattern learning
- Model performance tracking
- Similar task recall
"""

import os
import sqlite3
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


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


@dataclass
class FailurePattern:
    """A recorded failure pattern with what worked to fix it."""
    id: int
    error_type: str
    context: str
    what_worked: str
    occurrences: int
    success_rate: float
    created_at: str
    updated_at: str


@dataclass
class ModelPerformance:
    """Performance metrics for a model on a task type."""
    model: str
    task_type: str
    total_calls: int
    successful_calls: int
    avg_latency_ms: float
    success_rate: float
    last_updated: str


class TaskStore:
    """
    SQLite-based task history store with learning capabilities.
    
    Features:
    - Task history storage and retrieval
    - Failure pattern tracking and recall
    - Model performance monitoring
    - Similar task recommendations
    
    Usage:
        from neuro.memory.task_store import TaskStore
        
        store = TaskStore()
        
        # Save failure pattern
        store.save_failure_pattern(
            error_type="IMPORT_ERROR",
            context="Missing module: requests",
            what_worked="pip install requests"
        )
        
        # Get similar tasks
        similar = store.recall_similar_task("Build a REST API")
        
        # Get best model for task type
        best_model = store.get_best_model_for_task("code_generation")
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
        """Initialize the database with all tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Main tasks table
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
        
        # Failure patterns table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                context TEXT NOT NULL,
                what_worked TEXT NOT NULL,
                occurrences INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Model performance table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                task_type TEXT NOT NULL,
                total_calls INTEGER DEFAULT 0,
                successful_calls INTEGER DEFAULT 0,
                total_latency_ms REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0,
                last_updated TEXT NOT NULL,
                UNIQUE(model, task_type)
            )
        """)
        
        # Create indexes
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_goal_hash ON tasks(goal_hash)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON tasks(created_at)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_error_type ON failure_patterns(error_type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_model_perf ON model_performance(model, task_type)")
        
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
    
    # =========================================================================
    # FAILURE PATTERN LEARNING
    # =========================================================================
    
    def save_failure_pattern(
        self,
        error_type: str,
        context: str,
        what_worked: str
    ) -> int:
        """
        Save a failure pattern with what worked to fix it.
        
        Args:
            error_type: Type of error (e.g., IMPORT_ERROR, SYNTAX_ERROR)
            context: Context where error occurred
            what_worked: What fixed the issue
            
        Returns:
            Pattern ID
        """
        now = datetime.now().isoformat()
        
        # Check if pattern already exists
        existing = self.conn.execute("""
            SELECT id, occurrences FROM failure_patterns 
            WHERE error_type = ? AND context = ?
        """, (error_type, context)).fetchone()
        
        if existing:
            # Update existing pattern
            new_occurrences = existing["occurrences"] + 1
            self.conn.execute("""
                UPDATE failure_patterns 
                SET what_worked = ?, occurrences = ?, updated_at = ?
                WHERE id = ?
            """, (what_worked, new_occurrences, now, existing["id"]))
            self.conn.commit()
            return existing["id"]
        
        # Insert new pattern
        cursor = self.conn.execute("""
            INSERT INTO failure_patterns (
                error_type, context, what_worked, occurrences,
                success_rate, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (error_type, context, what_worked, 1, 0.0, now, now))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def recall_similar_task(self, current_task: str) -> Optional[Dict[str, Any]]:
        """
        Recall similar successful task from history.
        
        Args:
            current_task: Description of current task
            
        Returns:
            Dict with similar task info or None if not found
        """
        # Get similar tasks that were successful
        task_hash = hashlib.md5(current_task.encode()).hexdigest()[:16]
        
        rows = self.conn.execute("""
            SELECT * FROM tasks 
            WHERE status = 'success' AND (
                goal_hash = ? OR 
                goal LIKE ?
            )
            ORDER BY created_at DESC
            LIMIT 5
        """, (task_hash, f"%{current_task[:50]}%")).fetchall()
        
        if not rows:
            return None
        
        # Return most recent successful task
        record = self._row_to_record(rows[0])
        
        return {
            "goal": record.goal,
            "files_changed": record.files_changed,
            "model_used": record.model_used,
            "duration_ms": record.duration_ms,
            "metadata": record.metadata,
        }
    
    def get_successful_patterns(self, task_type: str) -> List[Dict[str, Any]]:
        """
        Get successful patterns for a task type.
        
        Args:
            task_type: Type of task (e.g., "web_app", "api_build")
            
        Returns:
            List of patterns with success info
        """
        # Search for task type in goals and metadata
        rows = self.conn.execute("""
            SELECT * FROM tasks 
            WHERE status = 'success' AND (
                goal LIKE ? OR
                metadata LIKE ?
            )
            ORDER BY created_at DESC
            LIMIT 10
        """, (f"%{task_type}%", f"%{task_type}%")).fetchall()
        
        return [
            {
                "goal": self._row_to_record(r).goal,
                "files_changed": self._row_to_record(r).files_changed,
                "model_used": self._row_to_record(r).model_used,
            }
            for r in rows
        ]
    
    # =========================================================================
    # MODEL PERFORMANCE TRACKING
    # =========================================================================
    
    def update_model_performance(
        self,
        model: str,
        task_type: str,
        success: bool,
        latency_ms: float
    ):
        """
        Update model performance metrics.
        
        Args:
            model: Model identifier (e.g., "groq/llama-3.3-70b-versatile")
            task_type: Type of task performed
            success: Whether the task succeeded
            latency_ms: Response latency in milliseconds
        """
        now = datetime.now().isoformat()
        
        # Try to get existing record
        existing = self.conn.execute("""
            SELECT * FROM model_performance 
            WHERE model = ? AND task_type = ?
        """, (model, task_type)).fetchone()
        
        if existing:
            # Update existing
            total_calls = existing["total_calls"] + 1
            successful_calls = existing["successful_calls"] + (1 if success else 0)
            total_latency = existing["total_latency_ms"] + latency_ms
            success_rate = successful_calls / total_calls
            
            self.conn.execute("""
                UPDATE model_performance 
                SET total_calls = ?, successful_calls = ?, 
                    total_latency_ms = ?, success_rate = ?, last_updated = ?
                WHERE model = ? AND task_type = ?
            """, (total_calls, successful_calls, total_latency, 
                  success_rate, now, model, task_type))
        else:
            # Insert new
            success_rate = 1.0 if success else 0.0
            self.conn.execute("""
                INSERT INTO model_performance (
                    model, task_type, total_calls, successful_calls,
                    total_latency_ms, success_rate, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (model, task_type, 1, 1 if success else 0, 
                  latency_ms, success_rate, now))
        
        self.conn.commit()
    
    def get_best_model_for_task(self, task_type: str) -> str:
        """
        Get the best performing model for a task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            Model identifier or empty string if no data
        """
        rows = self.conn.execute("""
            SELECT model, success_rate, total_calls 
            FROM model_performance 
            WHERE task_type = ? AND total_calls >= 3
            ORDER BY success_rate DESC, total_calls DESC
            LIMIT 5
        """, (task_type,)).fetchall()
        
        if not rows:
            return ""
        
        # Return best model (highest success rate with sufficient data)
        return rows[0]["model"]
    
    def get_model_comparison(self, task_type: str) -> List[Dict[str, Any]]:
        """
        Get comparison of all models for a task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            List of models with performance metrics
        """
        rows = self.conn.execute("""
            SELECT model, total_calls, successful_calls, 
                   total_latency_ms / total_calls as avg_latency_ms,
                   success_rate
            FROM model_performance 
            WHERE task_type = ?
            ORDER BY success_rate DESC, avg_latency_ms ASC
        """, (task_type,)).fetchall()
        
        return [
            {
                "model": r["model"],
                "total_calls": r["total_calls"],
                "successful_calls": r["successful_calls"],
                "avg_latency_ms": r["avg_latency_ms"] or 0,
                "success_rate": r["success_rate"],
            }
            for r in rows
        ]
    
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
