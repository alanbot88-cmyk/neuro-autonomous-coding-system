"""
Smart Context Engine
====================
Builds and manages context for autonomous coding tasks.

Creates context bundles containing:
- Relevant files
- Relevant functions
- Test files
- Git history
- Similar code patterns

Also manages:
- Context compression
- Relevance ranking
- Scope detection
"""

import os
import re
import subprocess
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict


@dataclass
class ContextBundle:
    """
    Complete context bundle for a task.
    
    Attributes:
        relevant_files: Files that are relevant to the task
        relevant_functions: Functions/classes that are relevant
        test_files: Test files related to the task
        git_context: Git history and context
        similar_patterns: Similar code patterns found
        total_tokens: Estimated token count of context
    """
    relevant_files: List[str] = field(default_factory=list)
    relevant_functions: List[Dict[str, Any]] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    git_context: List[Dict[str, str]] = field(default_factory=list)
    similar_patterns: List[Dict[str, Any]] = field(default_factory=list)
    total_tokens: int = 0


class ContextEngine:
    """
    Smart Context Engine
    ====================
    Builds comprehensive context for coding tasks.
    
    Responsibilities:
    - Find and rank relevant files
    - Build context bundles
    - Compress conversation history
    - Detect task scope
    
    Attributes:
        workspace_root: Root directory of workspace
        max_tokens: Maximum context tokens (default ~100k)
    """
    
    def __init__(self, workspace_root: str = "."):
        """
        Initialize context engine.
        
        Args:
            workspace_root: Root directory for file operations
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.max_tokens = 100_000  # ~100k tokens roughly
        self._language_map = self._init_language_map()
    
    def build_context(
        self,
        task: Dict[str, Any],
        codebase_root: Optional[str] = None
    ) -> ContextBundle:
        """
        Build comprehensive context for a task.
        
        Args:
            task: Task specification dict
            codebase_root: Optional override for codebase root
            
        Returns:
            ContextBundle with all relevant information
        """
        root = Path(codebase_root) if codebase_root else self.workspace_root
        
        description = task.get("description", "")
        scope_files = task.get("scope_files", [])
        task_type = task.get("type", "general")
        
        # Detect scope
        scoped_files = self.detect_scope(task, root)
        
        # Find relevant files
        relevant_files = self._find_relevant_files(description, root, scoped_files)
        
        # Find relevant functions
        relevant_functions = self._find_relevant_functions(relevant_files, description)
        
        # Find test files
        test_files = self._find_test_files(relevant_files)
        
        # Get git context
        git_context = self._get_git_context_batch(relevant_files)
        
        # Find similar patterns
        similar_patterns = self._find_similar_patterns(description, relevant_files)
        
        # Build bundle
        bundle = ContextBundle(
            relevant_files=relevant_files,
            relevant_functions=relevant_functions,
            test_files=test_files,
            git_context=git_context,
            similar_patterns=similar_patterns,
            total_tokens=self._estimate_tokens(relevant_files, relevant_functions)
        )
        
        # Compress if needed
        if bundle.total_tokens > self.max_tokens:
            bundle = self._compress_bundle(bundle)
        
        return bundle
    
    def compress_history(
        self,
        conversation_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Summarize old conversation turns to save context.
        
        Args:
            conversation_history: List of conversation turns
            
        Returns:
            Compressed history with summaries for old turns
        """
        if not conversation_history:
            return []
        
        compressed = []
        summary_threshold = 5  # Summarize turns beyond this
        
        for i, turn in enumerate(conversation_history):
            if i < summary_threshold:
                # Keep recent turns as-is
                compressed.append(turn)
            else:
                # Summarize old turns
                summary = self._summarize_turn(turn)
                if summary:
                    compressed.append({
                        "type": "summary",
                        "original_index": i,
                        "summary": summary
                    })
        
        return compressed
    
    def rank_relevance(
        self,
        snippets: List[Dict[str, Any]],
        task: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Score and sort code snippets by relevance.
        
        Args:
            snippets: List of code snippets with metadata
            task: Task specification
            
        Returns:
            Sorted list with relevance scores
        """
        task_keywords = self._extract_keywords(task.get("description", ""))
        
        ranked = []
        for snippet in snippets:
            score = self._calculate_relevance_score(snippet, task_keywords)
            ranked.append({
                **snippet,
                "relevance_score": score
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return ranked
    
    def detect_scope(
        self,
        task: Dict[str, Any],
        codebase_root: Path
    ) -> Set[str]:
        """
        Detect files and modules in scope for the task.
        
        Args:
            task: Task specification
            codebase_root: Root of codebase
            
        Returns:
            Set of file paths in scope
        """
        scope = set()
        
        # Direct scope
        if "scope_files" in task:
            for f in task["scope_files"]:
                scope.add(str(Path(f).resolve()))
        
        # Type-based scope
        task_type = task.get("type", "general")
        type_scopes = {
            "web_app": ["templates", "static", "views", "routes", "components"],
            "new_feature": ["modules", "features", "services"],
            "refactor": ["core", "lib", "src"],
        }
        
        for directory in type_scopes.get(task_type, []):
            dir_path = codebase_root / directory
            if dir_path.exists():
                for f in dir_path.rglob("*.py"):
                    scope.add(str(f))
        
        return scope
    
    # Private methods
    
    def _find_relevant_files(
        self,
        description: str,
        root: Path,
        scoped_files: Set[str]
    ) -> List[str]:
        """Find files relevant to task description."""
        keywords = self._extract_keywords(description)
        relevant = list(scoped_files)
        
        if not keywords:
            return list(scoped_files) if scoped_files else [str(root)]
        
        # Search for files matching keywords
        for root_dir, dirs, files in os.walk(root):
            # Skip hidden and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') 
                     and d not in ['node_modules', '__pycache__', '.git', 'venv']]
            
            for file in files:
                if '.' not in file:
                    continue
                
                file_path = Path(root_dir) / file
                file_lower = file.lower()
                
                # Check if filename contains keywords
                for keyword in keywords:
                    if keyword in file_lower:
                        if str(file_path) not in relevant:
                            relevant.append(str(file_path))
                        break
                
                # Limit results
                if len(relevant) > 50:
                    break
        
        return relevant
    
    def _find_relevant_functions(
        self,
        files: List[str],
        description: str
    ) -> List[Dict[str, Any]]:
        """Find functions/classes relevant to description."""
        keywords = self._extract_keywords(description)
        functions = []
        
        for file_path in files[:10]:  # Limit to first 10 files
            try:
                path = Path(file_path)
                if not path.exists() or not path.suffix == '.py':
                    continue
                
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    # Function definition
                    func_match = re.match(r'^(?:async\s+)?def\s+(\w+)\s*\(', stripped)
                    if func_match:
                        func_name = func_match.group(1)
                        if self._matches_keywords(func_name, keywords):
                            functions.append({
                                "name": func_name,
                                "type": "function",
                                "file": file_path,
                                "line": i
                            })
                    
                    # Class definition
                    class_merge = re.match(r'^class\s+(\w+)', stripped)
                    if class_merge:
                        class_name = class_merge.group(1)
                        if self._matches_keywords(class_name, keywords):
                            functions.append({
                                "name": class_name,
                                "type": "class",
                                "file": file_path,
                                "line": i
                            })
                            
            except (IOError, UnicodeDecodeError):
                continue
        
        return functions
    
    def _find_test_files(self, source_files: List[str]) -> List[str]:
        """Find test files for source files."""
        test_files = []
        
        for source in source_files:
            source_path = Path(source)
            
            if not source_path.exists():
                continue
            
            stem = source_path.stem
            parent = source_path.parent
            
            # Common test patterns
            patterns = [
                parent / f"test_{stem}{source_path.suffix}",
                parent / f"{stem}_test{source_path.suffix}",
                parent / "tests" / f"{stem}{source_path.suffix}",
                source_path.parent / f"{stem}.test{source_path.suffix}",
            ]
            
            for pattern in patterns:
                if pattern.exists() and str(pattern) not in test_files:
                    test_files.append(str(pattern))
        
        return test_files
    
    def _get_git_context_batch(
        self,
        files: List[str]
    ) -> List[Dict[str, str]]:
        """Get git context for multiple files."""
        context = []
        
        for file_path in files[:5]:  # Limit to first 5 files
            try:
                cmd = ['git', 'log', '--oneline', '-3', '--', file_path]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.split(' ', 1)
                            if len(parts) == 2:
                                context.append({
                                    "file": file_path,
                                    "hash": parts[0],
                                    "message": parts[1]
                                })
                                
            except subprocess.SubprocessError:
                continue
        
        return context
    
    def _find_similar_patterns(
        self,
        description: str,
        files: List[str]
    ) -> List[Dict[str, Any]]:
        """Find similar code patterns."""
        patterns = []
        keywords = self._extract_keywords(description)
        
        for file_path in files[:20]:  # Limit search
            try:
                path = Path(file_path)
                if not path.exists():
                    continue
                
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Look for patterns matching keywords
                for keyword in keywords:
                    matches = re.finditer(
                        rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}',
                        content,
                        re.IGNORECASE
                    )
                    
                    for match in matches[:3]:  # Limit matches per file
                        patterns.append({
                            "file": file_path,
                            "pattern": match.group(),
                            "keyword": keyword
                        })
                        
            except (IOError, UnicodeDecodeError):
                continue
        
        return patterns[:30]  # Return top 30
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Common programming terms to skip
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
            'by', 'from', 'as', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'which', 'while', 'who', 'whom', 'this', 'that', 'these',
            'those', 'am', 'its', 'it', 'function', 'code', 'file',
            'class', 'method', 'variable', 'data'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text.lower())
        
        # Filter stopwords and short words
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _matches_keywords(self, identifier: str, keywords: List[str]) -> bool:
        """Check if identifier matches any keywords."""
        identifier_lower = identifier.lower()
        return any(kw in identifier_lower for kw in keywords)
    
    def _calculate_relevance_score(
        self,
        snippet: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        """Calculate relevance score for a snippet."""
        score = 0.0
        
        # Name match
        name = snippet.get("name", "").lower()
        for keyword in keywords:
            if keyword in name:
                score += 0.5
        
        # Content match
        content = snippet.get("content", "").lower()
        matches = sum(1 for kw in keywords if kw in content)
        score += min(matches * 0.1, 0.5)
        
        # Normalize to 0-1
        return min(score, 1.0)
    
    def _estimate_tokens(
        self,
        files: List[str],
        functions: List[Dict[str, Any]]
    ) -> int:
        """Estimate total tokens in context."""
        total = 0
        
        for file_path in files[:20]:
            try:
                path = Path(file_path)
                if path.exists() and path.stat().st_size < 1024 * 1024:
                    total += path.stat().st_size // 4  # Rough: 4 chars per token
            except OSError:
                continue
        
        # Add function overhead
        total += len(functions) * 50
        
        return total
    
    def _compress_bundle(
        self,
        bundle: ContextBundle
    ) -> ContextBundle:
        """Compress bundle to fit within token limit."""
        # Remove files beyond the limit
        target_files = bundle.relevant_files[:30]
        
        return ContextBundle(
            relevant_files=target_files,
            relevant_functions=bundle.relevant_functions[:20],
            test_files=bundle.test_files[:10],
            git_context=bundle.git_context[:10],
            similar_patterns=bundle.similar_patterns[:20],
            total_tokens=sum(len(f) // 4 for f in target_files)
        )
    
    def _summarize_turn(self, turn: Dict[str, Any]) -> str:
        """Summarize a conversation turn."""
        role = turn.get("role", "")
        content = turn.get("content", "")
        
        # Truncate content
        if len(content) > 500:
            content = content[:500] + "..."
        
        return f"[{role}]: {content}"
    
    def _init_language_map(self) -> Dict[str, str]:
        """Initialize language extension map."""
        return {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
        }


class ContextCache:
    """Simple cache for context bundles."""
    
    def __init__(self, max_size: int = 50):
        """
        Initialize context cache.
        
        Args:
            max_size: Maximum number of cached contexts
        """
        self.max_size = max_size
        self._cache: Dict[str, ContextBundle] = {}
    
    def get(self, key: str) -> Optional[ContextBundle]:
        """Get cached context."""
        return self._cache.get(key)
    
    def set(self, key: str, bundle: ContextBundle) -> None:
        """Cache a context bundle."""
        if len(self._cache) >= self.max_size:
            # Remove oldest
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = bundle
    
    def clear(self) -> None:
        """Clear all cached contexts."""
        self._cache.clear()
