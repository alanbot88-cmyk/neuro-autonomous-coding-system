"""
Structured Edit Format Parser and Command Runner
Neuro's core file editing and command execution system
"""

import json
import os
import re
import subprocess
import shlex
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


# =============================================================================
# STRUCTURED EDIT FORMAT
# =============================================================================

EDIT_FORMAT_SCHEMA = {
    "analysis": "brief reasoning summary",
    "files": [
        {
            "path": "relative/path/from/repo/root.py",
            "action": "create|modify|delete",
            "content": "full file content here"  # Required for create/modify
        }
    ],
    "commands": ["pytest -q"],  # Optional validation commands
    "notes": "anything important"  # Optional notes
}


@dataclass
class FileEdit:
    """Represents a single file edit."""
    path: str
    action: str  # create, modify, delete
    content: Optional[str] = None
    
    def is_safe(self, workspace_root: str) -> Tuple[bool, str]:
        """Check if the edit is safe (within workspace, no path traversal)."""
        # Check for path traversal
        if ".." in self.path or self.path.startswith("/"):
            return False, "Path traversal or absolute path detected"
        
        # Check for dangerous paths
        dangerous_patterns = [".env", ".git/credentials", "/etc/", "~/.ssh/"]
        for pattern in dangerous_patterns:
            if pattern in self.path:
                return False, f"Dangerous path pattern detected: {pattern}"
        
        # Validate path is within workspace
        full_path = os.path.join(workspace_root, self.path)
        try:
            resolved = os.path.realpath(full_path)
            workspace_resolved = os.path.realpath(workspace_root)
            if not resolved.startswith(workspace_resolved):
                return False, "File path escapes workspace"
        except Exception as e:
            return False, f"Path validation error: {e}"
        
        return True, "OK"


@dataclass 
class StructuredEdit:
    """Represents a complete structured edit output from a model."""
    analysis: str
    files: List[FileEdit]
    commands: List[str] = field(default_factory=list)
    notes: str = ""
    
    @classmethod
    def from_json(cls, json_str: str) -> "StructuredEdit":
        """Parse JSON string into StructuredEdit."""
        data = json.loads(json_str)
        files = []
        for f in data.get("files", []):
            files.append(FileEdit(
                path=f.get("path", ""),
                action=f.get("action", "modify"),
                content=f.get("content"),
            ))
        
        return cls(
            analysis=data.get("analysis", ""),
            files=files,
            commands=data.get("commands", []),
            notes=data.get("notes", ""),
        )
    
    @classmethod
    def from_text(cls, text: str) -> Optional["StructuredEdit"]:
        """Try to extract structured edit from text (may have markdown code blocks)."""
        # Try to find JSON in code blocks first
        json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return cls.from_json(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find raw JSON
        json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        for match in re.finditer(json_pattern, text, re.DOTALL):
            try:
                data = json.loads(match.group(0))
                if "files" in data:
                    return cls.from_json(match.group(0))
            except json.JSONDecodeError:
                continue
        
        return None


def validate_edit_format(data: Dict) -> Tuple[bool, List[str]]:
    """Validate that data follows the structured edit format."""
    errors = []
    
    # Check required fields
    if "files" not in data:
        errors.append("Missing 'files' field")
        return False, errors
    
    if not isinstance(data["files"], list):
        errors.append("'files' must be a list")
        return False, errors
    
    # Validate each file
    valid_actions = {"create", "modify", "delete"}
    for i, f in enumerate(data["files"]):
        if "path" not in f:
            errors.append(f"File {i}: missing 'path' field")
        
        if "action" not in f:
            errors.append(f"File {i}: missing 'action' field")
        elif f["action"] not in valid_actions:
            errors.append(f"File {i}: invalid action '{f['action']}' (must be create/modify/delete)")
        
        # Content required for create/modify
        if f.get("action") in ("create", "modify") and "content" not in f:
            errors.append(f"File {i}: missing 'content' for action '{f.get('action')}'")
    
    return len(errors) == 0, errors


def parse_structured_edit(text: str) -> Tuple[Optional[StructuredEdit], List[str]]:
    """Parse text into StructuredEdit with validation."""
    structured = StructuredEdit.from_text(text)
    
    if structured is None:
        return None, ["Could not parse structured edit from text"]
    
    errors = []
    for f in structured.files:
        if not f.path:
            errors.append("File path is empty")
        if f.action not in ("create", "modify", "delete"):
            errors.append(f"Invalid action: {f.action}")
        if f.action in ("create", "modify") and not f.content:
            errors.append(f"Missing content for {f.path}")
    
    if errors:
        return None, errors
    
    return structured, []


# =============================================================================
# COMMAND EXECUTION
# =============================================================================

@dataclass
class CommandResult:
    """Result of command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    duration_ms: float = 0.0


# Dangerous commands that should never run
DANGEROUS_COMMANDS = {
    "rm -rf /",
    "rm -rf /*",
    ":(){ :|:& };:",  # Fork bomb
    "mkfs",
    "dd if=",
    "> /dev/sda",
}


class CommandRunner:
    """Execute commands safely in workspace."""
    
    def __init__(self, workspace_root: str, timeout: int = 120):
        self.workspace_root = Path(workspace_root).absolute()
        self.timeout = timeout
        self.dry_run = False
    
    def is_dangerous(self, command: str) -> bool:
        """Check if command is dangerous."""
        cmd_lower = command.lower()
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in cmd_lower:
                return True
        return False
    
    def is_safe_command(self, command: str) -> bool:
        """Check if command is considered safe for Neuro."""
        # Allow only specific safe commands for code execution
        allowed_commands = {
            # Python
            "python", "python3", "pytest", "pip", "uv",
            # Node
            "npm", "node", "npx",
            # Git
            "git",
            # Build tools
            "make", "cmake", "cargo", "go",
            # Generic
            "ls", "cat", "find", "grep",
        }
        
        try:
            cmd = shlex.split(command)[0]
            return cmd in allowed_commands
        except:
            return False
    
    def run(self, command: str, cwd: Optional[str] = None, 
            capture_output: bool = True) -> CommandResult:
        """Run a command and return result."""
        import time
        
        # Validate command
        if self.is_dangerous(command):
            return CommandResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr="Dangerous command blocked",
            )
        
        # Set working directory
        if cwd is None:
            cwd = str(self.workspace_root)
        
        # Ensure we're in workspace
        try:
            cwd_path = Path(cwd).absolute()
            workspace_resolved = self.workspace_root.resolve()
            if not str(cwd_path).startswith(str(workspace_resolved)):
                return CommandResult(
                    command=command,
                    exit_code=1,
                    stdout="",
                    stderr="Working directory outside workspace",
                )
        except Exception as e:
            return CommandResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr=f"Working directory error: {e}",
            )
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=self.timeout,
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            return CommandResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                timed_out=False,
                duration_ms=duration_ms,
            )
            
        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            return CommandResult(
                command=command,
                exit_code=124,  # Standard timeout exit code
                stdout="",
                stderr=f"Command timed out after {self.timeout}s",
                timed_out=True,
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return CommandResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr=str(e),
                duration_ms=duration_ms,
            )
    
    def run_test(self, test_command: Optional[str] = None) -> CommandResult:
        """Run appropriate test command for the project."""
        # Detect project type and run appropriate tests
        has_pytest = (self.workspace_root / "pytest.ini").exists() or \
                     (self.workspace_root / "pyproject.toml").exists() or \
                     (self.workspace_root / "setup.py").exists()
        
        has_npm = (self.workspace_root / "package.json").exists()
        
        if test_command:
            return self.run(test_command)
        elif has_pytest:
            return self.run("python -m pytest -q")
        elif has_npm:
            return self.run("npm test")
        
        return CommandResult(
            command="detect",
            exit_code=0,
            stdout="No test framework detected",
            stderr="",
        )


# =============================================================================
# AUTONOMOUS EDIT LOOP
# =============================================================================

class AutonomousEditLoop:
    """
    Main loop for autonomous editing.
    Task intake → repo scan → planning → file selection → structured edit generation
    → safe file writing → command execution → test/build validation → error analysis
    → repair loop → final diff summary
    """
    
    def __init__(self, workspace: str, dry_run: bool = True):
        self.workspace = Path(workspace)
        self.writer = SafeFileWriterLite(workspace, dry_run=dry_run)
        self.runner = CommandRunner(workspace)
        self.dry_run = dry_run
    
    def apply_edit(self, edit: StructuredEdit) -> Dict[str, Any]:
        """Apply a structured edit to the workspace."""
        applied = []
        failed = []
        
        # Validate all files first
        for f in edit.files:
            safe, msg = f.is_safe(str(self.workspace))
            if not safe:
                failed.append({"file": f.path, "error": msg})
                continue
            
            # Apply the edit
            if f.action == "create":
                success = self.writer.create(f.path, f.content)
            elif f.action == "modify":
                success = self.writer.write(f.path, f.content)
            elif f.action == "delete":
                success = self.writer.delete(f.path)
            else:
                success = False
                failed.append({"file": f.path, "error": f"Unknown action: {f.action}"})
            
            if success:
                applied.append(f.path)
            else:
                failed.append({"file": f.path, "error": "Write failed"})
        
        return {
            "applied": applied,
            "failed": failed,
            "commands": edit.commands,
        }
    
    def run_validation(self, commands: List[str]) -> List[CommandResult]:
        """Run validation commands."""
        results = []
        for cmd in commands:
            result = self.runner.run(cmd)
            results.append(result)
        return results
    
    def execute_and_validate(self, edit: StructuredEdit) -> Dict[str, Any]:
        """Apply edits and run validation."""
        # Apply edits
        apply_result = self.apply_edit(edit)
        
        # Run commands if not dry run
        command_results = []
        if not self.dry_run and apply_result["commands"]:
            command_results = self.run_validation(apply_result["commands"])
        
        return {
            "apply": apply_result,
            "commands": [
                {"command": r.command, "exit_code": r.exit_code, 
                 "stdout": r.stdout[:500], "stderr": r.stderr[:500]}
                for r in command_results
            ],
        }


class SafeFileWriterLite:
    """Simplified safe file writer for the edit loop."""
    
    def __init__(self, workspace: str, dry_run: bool = True):
        self.workspace = Path(workspace)
        self.dry_run = dry_run
        self.written_files = []
    
    def _validate_path(self, path: str) -> Tuple[bool, str, Path]:
        """Validate path is within workspace."""
        if ".." in path or path.startswith("/"):
            return False, "Path traversal or absolute path", None
        
        full_path = (self.workspace / path).resolve()
        try:
            resolved = full_path.resolve()
            if not str(resolved).startswith(str(self.workspace.resolve())):
                return False, "Path escapes workspace", None
        except:
            pass
        
        return True, "OK", full_path
    
    def create(self, path: str, content: str) -> bool:
        """Create a new file."""
        safe, msg, full_path = self._validate_path(path)
        if not safe:
            return False
        
        if self.dry_run:
            self.written_files.append(path)
            return True
        
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            self.written_files.append(path)
            return True
        except Exception as e:
            return False
    
    def write(self, path: str, content: str) -> bool:
        """Write/modify a file."""
        return self.create(path, content)  # Same logic for simplicity
    
    def delete(self, path: str) -> bool:
        """Delete a file."""
        safe, msg, full_path = self._validate_path(path)
        if not safe:
            return False
        
        if self.dry_run:
            return True
        
        try:
            if full_path.exists():
                full_path.unlink()
            return True
        except Exception:
            return False
    
    def get_written_files(self) -> List[str]:
        """Get list of files that would be/were written."""
        return self.written_files


# =============================================================================
# ERROR REPAIR LOOP
# =============================================================================

class ErrorRepairLoop:
    """Handle error repair during autonomous editing."""
    
    def __init__(self, workspace: str, max_attempts: int = 3):
        self.workspace = workspace
        self.max_attempts = max_attempts
        self.runner = CommandRunner(workspace)
    
    def repair(
        self, 
        original_task: str,
        changed_files: List[str],
        command: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        router=None,  # Optional router for LLM-based repair
    ) -> Optional[StructuredEdit]:
        """
        Analyze error and attempt repair.
        
        Returns a StructuredEdit to apply, or None if repair failed.
        """
        if exit_code == 0:
            return None  # No error to repair
        
        # Simple repair heuristics
        error_type = self._classify_error(stderr)
        
        if error_type == "syntax_error":
            return self._repair_syntax_error(changed_files, stderr)
        elif error_type == "import_error":
            return self._repair_import_error(changed_files, stderr)
        elif error_type == "test_failure":
            return self._repair_test_failure(changed_files, stdout, stderr)
        
        # If LLM router provided, use it for smarter repair
        if router:
            return self._llm_repair(original_task, changed_files, command, stdout, stderr, router)
        
        return None
    
    def _classify_error(self, stderr: str) -> str:
        """Classify the type of error."""
        if "SyntaxError" in stderr or "IndentationError" in stderr:
            return "syntax_error"
        elif "ImportError" in stderr or "ModuleNotFoundError" in stderr:
            return "import_error"
        elif "FAILED" in stderr or "ERROR" in stderr:
            return "test_failure"
        return "unknown"
    
    def _repair_syntax_error(self, files: List[str], stderr: str) -> Optional[StructuredEdit]:
        """Repair a syntax error."""
        # Extract file and line info from stderr
        match = re.search(r'File "([^"]+)", line (\d+)', stderr)
        if not match:
            return None
        
        file_path = match.group(1)
        # Get context around the error
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Find the problematic line
            line_num = int(match.group(2)) - 1
            if line_num >= 0 and line_num < len(lines):
                # Simple heuristic: if line ends without : or has extra indentation
                line = lines[line_num].rstrip()
                if line.endswith(':') or line.startswith(' '):
                    # Try to fix common issues
                    pass  # Would need LLM for proper fix
        except:
            pass
        
        return None
    
    def _repair_import_error(self, files: List[str], stderr: str) -> Optional[StructuredEdit]:
        """Repair an import error."""
        # Extract missing module
        match = re.search(r"No module named '([^']+)'", stderr)
        if not match:
            return None
        
        module = match.group(1)
        
        # Could add pip install command, but that's dangerous
        return None
    
    def _repair_test_failure(self, files: List[str], stdout: str, stderr: str) -> Optional[StructuredEdit]:
        """Repair a test failure."""
        # Parse test output to understand what failed
        return None
    
    def _llm_repair(
        self, 
        task: str, 
        files: List[str], 
        command: str,
        stdout: str,
        stderr: str,
        router
    ) -> Optional[StructuredEdit]:
        """Use LLM for intelligent repair."""
        system_prompt = """You are a debugging expert. Analyze the error and produce a structured fix.
The output MUST be valid JSON in this format:
{
  "analysis": "brief reasoning summary",
  "files": [
    {
      "path": "relative/path/file.py",
      "action": "create|modify|delete",
      "content": "full file content for create/modify, omit for delete"
    }
  ],
  "commands": [],
  "notes": "anything important"
}"""
        
        user_prompt = f"""Original task: {task}
Changed files: {', '.join(files)}
Command run: {command}
Output: {stdout[:2000]}
Error: {stderr[:2000]}

Analyze the error and produce a fix."""
        
        try:
            result = router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="openrouter/qwen/qwen3-coder:free"
            )
            
            if "error" not in result:
                return StructuredEdit.from_text(result["content"])
        except:
            pass
        
        return None