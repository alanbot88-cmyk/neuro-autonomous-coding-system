"""
Workspace Manager - Safe file operations for Neuro
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FileChange:
    """Record of a file change."""
    file: str
    action: str  # create, update, delete
    before: Optional[str] = None
    after: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class RepoMap:
    """Map of the repository structure."""
    root: str
    files: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def add_file(self, path: str, content: str = ""):
        stat = os.stat(path) if os.path.exists(path) else None
        self.files[path] = {
            "size": stat.st_size if stat else 0,
            "modified": stat.st_mtime if stat else 0,
            "type": "directory" if os.path.isdir(path) else "file",
        }
    
    def scan(self, root: str, max_depth: int = 5):
        """Scan directory and build map."""
        self.root = root
        for dirpath, dirnames, filenames in os.walk(root):
            depth = dirpath[len(root):].count(os.sep)
            if depth >= max_depth:
                dirnames[:] = []
                continue
            for f in filenames:
                fp = os.path.join(dirpath, f)
                self.add_file(fp)
    
    def exists(self, path: str) -> bool:
        return path in self.files


class SafeFileWriter:
    """Safe file operations with backup."""
    
    def __init__(self, workspace: str, dry_run: bool = True):
        self.workspace = Path(workspace)
        self.dry_run = dry_run
        self.changes: List[FileChange] = []
        self.backup_dir = self.workspace / ".neuro_backups"
    
    def read(self, path: str) -> str:
        """Read file contents safely."""
        full_path = self.workspace / path
        if full_path.exists():
            return full_path.read_text()
        return ""
    
    def write(self, path: str, content: str, create_dirs: bool = True) -> bool:
        """Write file with backup and dry-run support."""
        full_path = self.workspace / path
        
        # Check if file exists
        exists = full_path.exists()
        before = full_path.read_text() if exists else None
        
        change = FileChange(
            file=path,
            action="update" if exists else "create",
            before=before,
            after=content,
        )
        
        if self.dry_run:
            self.changes.append(change)
            return True
        
        # Create directories
        if create_dirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing file
        if exists and before is not None:
            self._backup(path, before)
        
        # Write new content
        full_path.write_text(content)
        self.changes.append(change)
        return True
    
    def _backup(self, path: str, content: str):
        """Create backup of file."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / f"{path.replace('/', '_')}_{self._hash(path)}.bak"
        backup_path.write_text(content)
    
    def _hash(self, path: str) -> str:
        return hashlib.md5(path.encode()).hexdigest()[:8]
    
    def apply_patch(self, path: str, old: str, new: str) -> bool:
        """Apply a patch to a file."""
        content = self.read(path)
        if old not in content:
            return False
        
        doc = content.replace(old, new)
        return self.write(path, doc)
    
    def undo_last(self) -> bool:
        """Undo the last change if possible."""
        if not self.changes:
            return False
        
        last = self.changes.pop()
        if self.dry_run or last.before is None:
            return True
        
        file_path = self.workspace / last.file
        file_path.write_text(last.before)
        return True
    
    def get_changes(self) -> List[Dict[str, Any]]:
        """Get list of planned/applied changes."""
        return [
            {
                "file": c.file,
                "action": c.action,
                "timestamp": c.timestamp,
            }
            for c in self.changes
        ]


class ChangeTracker:
    """Track changes across a session."""
    
    def __init__(self):
        self.changes: List[FileChange] = []
    
    def record(self, change: FileChange):
        self.changes.append(change)
    
    def get_summary(self) -> Dict[str, int]:
        return {
            "total": len(self.changes),
            "created": sum(1 for c in self.changes if c.action == "create"),
            "updated": sum(1 for c in self.changes if c.action == "update"),
            "deleted": sum(1 for c in self.changes if c.action == "delete"),
        }
    
    def to_json(self) -> str:
        return json.dumps([
            {
                "file": c.file,
                "action": c.action,
                "timestamp": c.timestamp,
            }
            for c in self.changes
        ], indent=2)


def create_repo_map(workspace: str) -> RepoMap:
    """Quick function to create repo map."""
    repo_map = RepoMap(root=workspace)
    repo_map.scan(workspace)
    return repo_map


def safe_write(workspace: str, path: str, content: str, dry_run: bool = True) -> bool:
    """Quick function to safely write a file."""
    writer = SafeFileWriter(workspace, dry_run=dry_run)
    return writer.write(path, content)
