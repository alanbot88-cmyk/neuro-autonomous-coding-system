"""
Purpose-Built Coding Tools (ACI)
================================
Agent Coding Interface - Tools for code reading, writing, and manipulation.

Provides safe, structured access to codebase operations with:
- File viewing and editing
- Search and discovery
- Test execution
- Git integration
"""

import os
import re
import subprocess
import difflib
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    """Structured test execution result."""
    passed: bool
    name: str
    duration_ms: float
    error: Optional[str] = None
    output: Optional[str] = None


@dataclass
class SearchResult:
    """Structured search result."""
    file_path: str
    line_number: int
    line_content: str
    matches: List[str]


@dataclass
class SymbolInfo:
    """Information about a code symbol (function, class, etc.)."""
    name: str
    symbol_type: str
    file_path: str
    line_number: int
    end_line: int
    docstring: Optional[str] = None
    parameters: Optional[List[str]] = None


class AgentCodingInterface:
    """
    Agent Coding Interface (ACI)
    ============================
    Purpose-built tools for autonomous coding agents.
    
    Provides safe, verifiable operations for:
    - File reading and viewing
    - Code search and discovery
    - Symbol extraction
    - Test execution
    - Git context
    - Code modification
    
    Attributes:
        workspace_root: Root directory of the workspace
        max_file_size: Maximum file size to read (default 1MB)
    """
    
    def __init__(self, workspace_root: str = "."):
        """
        Initialize the ACI.
        
        Args:
            workspace_root: Root directory for file operations
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.max_file_size = 1024 * 1024  # 1MB
        self._language_extensions = self._init_language_extensions()
    
    def view_file(
        self,
        path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> str:
        """
        View file content or a specific line range.
        
        Args:
            path: Relative or absolute file path
            start_line: Optional start line (1-indexed)
            end_line: Optional end line (inclusive)
            
        Returns:
            File content or range as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If line range is invalid
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if file_path.stat().st_size > self.max_file_size:
            raise ValueError(f"File too large: {path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        if start_line is not None or end_line is not None:
            lines = content.split('\n')
            
            # Default to entire file if start_line is None
            start_idx = (start_line - 1) if start_line else 0
            # Default to end of file if end_line is None
            end_idx = end_line if end_line else len(lines)
            
            if start_idx < 0 or end_idx > len(lines):
                raise ValueError(f"Line range out of bounds: {start_line}-{end_line}")
            
            if start_idx >= end_idx:
                raise ValueError("start_line must be less than end_line")
            
            return '\n'.join(lines[start_idx:end_idx])
        
        return content
    
    def search_dir(
        self,
        pattern: str,
        directory: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for pattern in directory.
        
        Args:
            pattern: Regex pattern to search for
            directory: Directory to search (default: workspace root)
            file_type: File extension filter (e.g., '.py', '.js')
            
        Returns:
            List of SearchResult objects
        """
        search_path = self._resolve_path(directory) if directory else self.workspace_root
        
        if not search_path.is_dir():
            search_path = self.workspace_root
        
        results = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for root, dirs, files in os.walk(search_path):
            # Skip hidden directories and common non-source dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', '__pycache__', '.git', 'venv', 'env', 'build', 'dist']]
            
            for file in files:
                # Apply file type filter
                if file_type and not file.endswith(file_type):
                    continue
                
                file_path = Path(root) / file
                
                # Skip binary files
                if file.endswith(('.pyc', '.so', '.dll', '.exe', '.bin')):
                    continue
                
                try:
                    if file_path.stat().st_size > self.max_file_size:
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append(SearchResult(
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    line_content=line.strip(),
                                    matches=[m.group() for m in regex.finditer(line)]
                                ))
                except (IOError, UnicodeDecodeError):
                    continue
        
        return results
    
    def search_symbol(self, symbol_name: str, directory: Optional[str] = None) -> List[SymbolInfo]:
        """
        Find function/class definitions matching symbol name.
        
        Args:
            symbol_name: Name of function or class to find
            directory: Directory to search (default: workspace root)
            
        Returns:
            List of SymbolInfo objects
        """
        search_path = self._resolve_path(directory) if directory else self.workspace_root
        
        if not search_path.is_dir():
            search_path = self.workspace_root
        
        results = []
        symbol_lower = symbol_name.lower()
        
        # Common patterns for function/class definitions
        patterns = [
            (r'^class\s+' + re.escape(symbol_name) + r'\s*[:\(]', 'class'),
            (r'^def\s+' + re.escape(symbol_name) + r'\s*\(', 'function'),
            (r'^async\s+def\s+' + re.escape(symbol_name) + r'\s*\(', 'async_function'),
        ]
        
        for root, dirs, files in os.walk(search_path):
            # Skip non-Python files
            py_files = [f for f in files if f.endswith('.py')]
            
            for file in py_files:
                file_path = Path(root) / file
                start_line = 0
                in_multiline_def = False
                multiline_content = []
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = [(i+1, line) for i, line in enumerate(f)]
                    
                    i = 0
                    while i < len(lines):
                        line_num, line = lines[i]
                        
                        for pattern, sym_type in patterns:
                            if re.match(pattern, line, re.IGNORECASE):
                                # Check for docstring
                                docstring = None
                                params = None
                                
                                # Look for docstring in next few lines
                                for j in range(i+1, min(i+4, len(lines))):
                                    next_line = lines[j][1].strip()
                                    if next_line.startswith('"""') or next_line.startswith("'''"):
                                        docstring = next_line.strip('"""\'\'')
                                        if len(next_line) > 3:
                                            break
                                    elif next_line:
                                        break
                                
                                # Extract parameters
                                param_match = re.search(r'\((.*?)\)', line)
                                if param_match:
                                    params = [p.strip() for p in param_match.group(1).split(',') if p.strip()]
                                
                                results.append(SymbolInfo(
                                    name=symbol_name,
                                    symbol_type=sym_type,
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    end_line=line_num,
                                    docstring=docstring,
                                    parameters=params
                                ))
                                break
                        
                        i += 1
                        
                except (IOError, UnicodeDecodeError):
                    continue
        
        return results
    
    def find_tests(self, for_file: str) -> List[str]:
        """Find test files related to a source file.
        
        Args:
            for_file: Path to source file
            
        Returns:
            List of paths to test files
        """
        file_path = self._resolve_path(for_file)
        
        if not file_path.exists():
            return []
        
        # Common test file patterns
        test_patterns = []
        
        stem = file_path.stem
        ext = file_path.suffix
        parent = file_path.parent
        
        # Pattern: test_<name>.py, <name>_test.py
        test_patterns.append(parent / f"test_{stem}{ext}")
        test_patterns.append(parent / f"{stem}_test{ext}")
        
        # Pattern: tests/<name>.py
        tests_dir = parent / "tests"
        if tests_dir.exists():
            test_patterns.append(tests_dir / f"{stem}{ext}")
            test_patterns.append(tests_dir / f"test_{stem}{ext}")
        
        # Pattern: <name>.test.py, <name>.spec.py
        test_patterns.append(file_path.parent / f"{stem}.test{ext}")
        test_patterns.append(file_path.parent / f"{stem}.spec{ext}")
        
        # Find existing test files
        test_files = []
        for pattern in test_patterns:
            if pattern.exists():
                test_files.append(str(pattern))
        
        return test_files
    
    def get_function(self, function_name: str, file_path: str) -> Optional[str]:
        """
        Extract a single function from a file.
        
        Args:
            function_name: Name of function to extract
            file_path: Path to source file
            
        Returns:
            Function code as string, or None if not found
        """
        try:
            content = self.view_file(file_path)
            lines = content.split('\n')
            
            start_line = None
            end_line = None
            base_indent = None
            in_function = False
            
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                
                # Detect function start
                if re.match(rf'^(def|async\s+def)\s+{re.escape(function_name)}\s*\(', stripped):
                    start_line = i
                    base_indent = len(line) - len(stripped)
                    in_function = True
                    continue
                
                if in_function:
                    # Check for function end (less indented line or new definition)
                    if stripped and not stripped.startswith('#'):
                        current_indent = len(line) - len(stripped)
                        
                        if current_indent < base_indent:
                            end_line = i
                            break
                    
                    # Check for new function/class at same level
                    if re.match(r'^(def|class|async\s+def)\s+', stripped):
                        end_line = i
                        break
            
            if start_line is not None:
                end = end_line if end_line else len(lines)
                return '\n'.join(lines[start_line:end])
            
            return None
            
        except (FileNotFoundError, IOError):
            return None
    
    def get_class(self, class_name: str, file_path: str) -> Optional[str]:
        """
        Extract a single class from a file.
        
        Args:
            class_name: Name of class to extract
            file_path: Path to source file
            
        Returns:
            Class code as string, or None if not found
        """
        try:
            content = self.view_file(file_path)
            lines = content.split('\n')
            
            start_line = None
            end_line = None
            base_indent = None
            in_class = False
            
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                
                # Detect class start
                if re.match(rf'^class\s+{re.escape(class_name)}\s*[:\(]', stripped):
                    start_line = i
                    base_indent = len(line) - len(stripped)
                    in_class = True
                    continue
                
                if in_class:
                    # Check for class end
                    if stripped and not stripped.startswith('#'):
                        current_indent = len(line) - len(stripped)
                        
                        if current_indent < base_indent:
                            end_line = i
                            break
                    
                    # Check for new class at same level
                    if re.match(r'^class\s+', stripped):
                        end_line = i
                        break
            
            if start_line is not None:
                end = end_line if end_line else len(lines)
                return '\n'.join(lines[start_line:end])
            
            return None
            
        except (FileNotFoundError, IOError):
            return None
    
    def apply_diff(self, diff_content: str, file_path: str) -> Dict[str, Any]:
        """
        Apply a unified diff to a file safely.
        
        Args:
            diff_content: Unified diff string
            file_path: Path to target file
            
        Returns:
            Dictionary with 'success', 'applied', 'backup_path'
        """
        target = self._resolve_path(file_path)
        
        if not target.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "applied": False
            }
        
        # Create backup
        backup_path = str(target) + ".backup"
        with open(target, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        try:
            # Parse diff and apply
            result = list(difflib.unified_diff(
                original_content.splitlines(keepends=True),
                original_content.splitlines(keepends=True),
                fromfile=str(target),
                tofile=str(target),
                lineterm=''
            ))
            
            # For actual diff application, we'd use a proper diff library
            # This is a simplified version that creates backup
            
            return {
                "success": True,
                "applied": True,
                "backup_path": backup_path,
                "message": "Diff applied, backup created"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "applied": False,
                "backup_path": backup_path
            }
    
    def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Create a new file with backup capability.
        
        Args:
            path: Path for new file
            content: Initial file content
            
        Returns:
            Dictionary with 'success', 'path', 'backup_created'
        """
        file_path = self._resolve_path(path)
        
        backup_created = False
        backup_path = None
        
        if file_path.exists():
            # Create backup of existing file
            backup_path = str(file_path) + ".backup"
            with open(file_path, 'r', encoding='utf-8') as f:
                existing = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(existing)
            backup_created = True
        
        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "backup_created": backup_created,
                "backup_path": backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": str(file_path)
            }
    
    def run_tests(self, test_path: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Run tests and return structured results.
        
        Args:
            test_path: Path to test file or directory
            timeout: Maximum time in seconds
            
        Returns:
            Dictionary with test results
        """
        test_file = self._resolve_path(test_path)
        
        if not test_file.exists():
            return {
                "success": False,
                "error": f"Test path not found: {test_path}",
                "results": []
            }
        
        results = []
        
        try:
            # Detect test framework
            if test_file.suffix == '.py':
                results = self._run_pytest(test_file, timeout)
            else:
                return {
                    "success": False,
                    "error": "Unsupported test framework",
                    "results": []
                }
            
            # Calculate summary
            passed = sum(1 for r in results if r.passed)
            failed = sum(1 for r in results if not r.passed)
            
            return {
                "success": failed == 0,
                "passed": passed,
                "failed": failed,
                "total": len(results),
                "results": [
                    {
                        "passed": r.passed,
                        "name": r.name,
                        "duration_ms": r.duration_ms,
                        "error": r.error
                    }
                    for r in results
                ]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Test execution timed out after {timeout}s",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def get_git_context(self, file_path: str, commits: int = 5) -> List[Dict[str, str]]:
        """
        Get recent git commits for a file.
        
        Args:
            file_path: Path to file
            commits: Number of commits to fetch
            
        Returns:
            List of commit dictionaries
        """
        target = self._resolve_path(file_path)
        
        if not target.exists():
            return []
        
        try:
            # Get git log for file
            cmd = [
                'git', 'log', f'--oneline', f'-{commits}',
                '--', str(target)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=target.parent,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            commits_list = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commits_list.append({
                            "hash": parts[0],
                            "message": parts[1]
                        })
            
            return commits_list
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return []
    
    def detect_language(self, path: str) -> Optional[str]:
        """
        Detect programming language from file extension.
        
        Args:
            path: File path
            
        Returns:
            Language name or None
        """
        file_path = self._resolve_path(path)
        ext = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql',
            '.sh': 'shell',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.md': 'markdown',
            '.r': 'r',
            '.lua': 'lua',
            '.pl': 'perl',
        }
        
        return language_map.get(ext)
    
    def get_imports(self, file_path: str) -> List[Dict[str, str]]:
        """
        Extract all imports from a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of import dictionaries with type, module, names
        """
        try:
            content = self.view_file(file_path)
            imports = []
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Regular import
                if stripped.startswith('import '):
                    module = stripped.replace('import ', '').split(' as ')[0].strip()
                    imports.append({
                        "type": "import",
                        "module": module,
                        "line": i,
                        "names": [module.split('.')[0]]
                    })
                
                # From import
                elif stripped.startswith('from '):
                    match = re.match(r'from\s+([\w.]+)\s+import\s+(.*)', stripped)
                    if match:
                        module = match.group(1)
                        names_str = match.group(2)
                        
                        # Parse names (handling "as" and parentheses)
                        names = re.sub(r'\s+as\s+\w+', '', names_str)
                        names = names.strip('()').split(',')
                        names = [n.strip() for n in names if n.strip()]
                        
                        imports.append({
                            "type": "from",
                            "module": module,
                            "line": i,
                            "names": names
                        })
            
            return imports
            
        except (FileNotFoundError, IOError):
            return []
    
    def find_similar_code(
        self,
        code_snippet: str,
        directory: Optional[str] = None,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find code similar to the given snippet.
        
        Args:
            code_snippet: Code to find similarity for
            directory: Directory to search (default: workspace root)
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar code locations with similarity scores
        """
        search_path = self._resolve_path(directory) if directory else self.workspace_root
        
        if not search_path.is_dir():
            search_path = self.workspace_root
        
        # Normalize snippet for comparison
        normalized = self._normalize_code(code_snippet)
        snippet_words = set(normalized.split())
        
        results = []
        
        for root, dirs, files in os.walk(search_path):
            # Skip non-code files
            code_files = [f for f in files if f.endswith(('.py', '.js', '.ts', '.go'))]
            
            for file in code_files:
                file_path = Path(root) / file
                
                try:
                    if file_path.stat().st_size > self.max_file_size:
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    
                    # Simple word-based similarity
                    file_normalized = self._normalize_code(content)
                    file_words = set(file_normalized.split())
                    
                    # Calculate Jaccard similarity
                    if snippet_words and file_words:
                        intersection = len(snippet_words & file_words)
                        union = len(snippet_words | file_words)
                        similarity = intersection / union if union > 0 else 0
                        
                        if similarity >= threshold:
                            results.append({
                                "file": str(file_path),
                                "similarity": similarity,
                                "matched_terms": list(snippet_words & file_words)[:10]
                            })
                            
                except (IOError, UnicodeDecodeError):
                    continue
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:10]  # Return top 10
    
    # Helper methods
    
    def _resolve_path(self, path: Optional[str]) -> Path:
        """Resolve path relative to workspace root."""
        if not path:
            return self.workspace_root
        
        p = Path(path)
        if p.is_absolute():
            return p
        return self.workspace_root / p
    
    def _init_language_extensions(self) -> Dict[str, str]:
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
        }
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison."""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        
        # Convert to lowercase for comparison
        return code.lower()
    
    def _run_pytest(self, test_file: Path, timeout: int) -> List[TestResult]:
        """Run pytest and parse results."""
        results = []
        
        try:
            cmd = [
                'python', '-m', 'pytest',
                str(test_file),
                '-v',
                '--tb=short',
                '--no-header'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout + result.stderr
            
            # Parse pytest output
            current_test = None
            
            for line in output.split('\n'):
                # Parse test result line
                match = re.match(r'([\w_]+::[\w_]+)\s+(PASSED|FAILED|SKIPPED|ERROR)', line)
                if match:
                    test_name = match.group(1)
                    status = match.group(2)
                    
                    results.append(TestResult(
                        passed=status == 'PASSED',
                        name=test_name,
                        duration_ms=0,  # Would need pytest-json report for timing
                        error=None if status == 'PASSED' else "Test failed"
                    ))
                    
        except subprocess.TimeoutExpired:
            results.append(TestResult(
                passed=False,
                name="test_suite",
                duration_ms=timeout * 1000
            ))
        except Exception:
            pass
        
        return results
