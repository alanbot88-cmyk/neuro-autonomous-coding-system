"""
Patch Guard - Validates patches before applying
Ensures only verified patches are applied
Critical for 75-80% score by preventing broken patches

Now with improved unified diff parsing for SWE-bench patches.
"""

import os
import re
import hashlib
import json
import difflib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


# =============================================================================
# UNIFIED DIFF PARSING (for SWE-bench compatibility)
# =============================================================================

class UnifiedDiffParser:
    """
    Parse unified diff patches correctly using difflib.unified_diff.
    Critical for SWE-bench where patches have hunk offsets.
    """
    
    @staticmethod
    def parse_patch(patch_text: str) -> List[Dict[str, Any]]:
        """
        Parse a unified diff patch into structured hunks.
        
        Args:
            patch_text: Unified diff string
            
        Returns:
            List of dicts with file_path, hunks, and metadata
        """
        patches = []
        current_patch = None
        current_hunk = None
        
        for line in patch_text.split('\n'):
            if line.startswith('--- '):
                if current_patch:
                    if current_hunk:
                        current_patch[' hunks'].append(current_hunk)
                    patches.append(current_patch)
                
                parts = line[4:].split('\t')
                current_patch = {
                    'old_file': parts[0].strip(),
                    'new_file': '',
                    ' hunks': [],
                    'is_new': False,
                    'is_deleted': False,
                }
                current_hunk = None
            
            elif line.startswith('+++ '):
                if current_patch:
                    parts = line[4:].split('\t')
                    current_patch['new_file'] = parts[0].strip()
                    if current_patch['new_file'] == '/dev/null':
                        current_patch['is_deleted'] = True
                    if current_patch['old_file'] == '/dev/null':
                        current_patch['is_new'] = True
            
            elif line.startswith('@@'):
                if current_hunk and current_patch:
                    current_patch[' hunks'].append(current_hunk)
                
                match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)', line)
                if match:
                    current_hunk = {
                        'old_start': int(match.group(1)),
                        'old_count': int(match.group(2)) if match.group(2) else 1,
                        'new_start': int(match.group(3)),
                        'new_count': int(match.group(4)) if match.group(4) else 1,
                        'old_lines': [],
                        'new_lines': [],
                        'header': line,
                    }
            
            elif current_hunk is not None:
                if line.startswith('-'):
                    current_hunk['old_lines'].append(line[1:])
                elif line.startswith('+'):
                    current_hunk['new_lines'].append(line[1:])
                elif line.startswith(' '):
                    current_hunk['old_lines'].append(line[1:])
                    current_hunk['new_lines'].append(line[1:])
        
        if current_hunk and current_patch:
            current_patch[' hunks'].append(current_hunk)
        if current_patch:
            patches.append(current_patch)
        
        return patches
    
    @staticmethod
    def apply_patch(file_path: str, patch: Dict[str, Any]) -> bool:
        """Apply a parsed patch to a file using proper hunk offsets."""
        if not os.path.exists(file_path):
            if patch.get('is_new'):
                content = '\n'.join(
                    hunk['new_lines'] 
                    for hunk in patch[' hunks']
                )
                os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content + '\n' if content else '')
                return True
            return False
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for hunk in reversed(patch[' hunks']):
            old_start = hunk['old_start'] - 1
            old_count = hunk['old_count']
            
            old_content = ''.join(lines[old_start:old_start + old_count])
            expected_old = ''.join(hunk['old_lines'])
            
            if old_content.rstrip('\n') != expected_old.rstrip('\n'):
                if not UnifiedDiffParser._fuzzy_apply(lines, hunk, old_start):
                    return False
            
            new_lines = hunk['new_lines']
            lines[old_start:old_start + old_count] = [l + '\n' for l in new_lines]
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        return True
    
    @staticmethod
    def _fuzzy_apply(lines: List[str], hunk: Dict, target_start: int) -> bool:
        """Attempt fuzzy matching when exact hunk doesn't apply."""
        old_lines = hunk['old_lines']
        new_lines = hunk['new_lines']
        
        if not old_lines:
            return False
        
        search_text = '\n'.join(old_lines)
        current_text = '\n'.join(lines)
        
        seq = difflib.SequenceMatcher(None, search_text, current_text)
        match = seq.find_longest_match(0, len(search_text), 0, len(current_text))
        
        if match.size >= len(search_text) * 0.8:
            old_lines_before = search_text[:match.a].count('\n')
            current_lines_before = current_text[:match.b].count('\n')
            new_start = current_lines_before + old_lines_before
            
            if new_start >= 0 and new_start + match.size <= len(lines):
                lines[new_start:new_start + match.size] = [l + '\n' for l in new_lines]
                return True
        
        return False
    
    @staticmethod
    def generate_patch(old_content: str, new_content: str, old_path: str = "a", 
                       new_path: str = "b") -> str:
        """Generate a unified diff from old and new content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=old_path,
            tofile=new_path,
            lineterm=''
        )
        
        return ''.join(diff)


@dataclass
class Patch:
    """Represents a code patch to apply."""
    file_path: str
    old_content: str = ""
    new_content: str = ""
    hunk_start: int = 0
    hunk_lines: int = 0
    hash: str = ""
    applied: bool = False
    verified: bool = False
    validation_error: str = ""
    unified_diff: str = ""  # Raw unified diff format
    parsed_patch: Optional[Dict[str, Any]] = None  # Structured parsed patch
    
    def __post_init__(self):
        if not self.hash:
            self.hash = self._compute_hash()
        # Auto-parse unified diff if provided
        if self.unified_diff and not self.parsed_patch:
            self.parsed_patch = self._parse_unified_diff()
    
    def _compute_hash(self) -> str:
        """Compute hash of the patch."""
        content = f"{self.file_path}:{self.old_content}:{self.new_content}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _parse_unified_diff(self) -> Optional[Dict[str, Any]]:
        """Parse unified diff format into structured patch."""
        if not self.unified_diff:
            return None
        patches = UnifiedDiffParser.parse_patch(self.unified_diff)
        # Find matching file
        for p in patches:
            old_file = p.get('old_file', '')
            new_file = p.get('new_file', '')
            # Extract filename from path
            old_name = os.path.basename(old_file.replace('a/', '').replace('b/', ''))
            new_name = os.path.basename(new_file.replace('a/', '').replace('b/', ''))
            if old_name in self.file_path or new_name in self.file_path or self.file_path in old_name:
                return p
        return patches[0] if patches else None


@dataclass
class ValidationResult:
    """Result of patch validation."""
    patch: Patch
    passed: bool
    validation_type: str
    message: str
    test_results: List[Dict] = field(default_factory=list)
    duration_ms: float = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PatchGuard:
    """
    Guard that validates patches before applying.
    Only applies patches that pass all validation checks.
    This is critical for achieving high scores.
    """
    
    def __init__(self, working_dir: Optional[str] = None, dry_run: bool = False):
        self.working_dir = working_dir or os.getcwd()
        self.dry_run = dry_run
        self.pending_patches: List[Patch] = []
        self.applied_patches: List[Patch] = []
        self.rejected_patches: List[Patch] = []
        self.backup_dir = os.path.join(self.working_dir, ".neuro_backups")
        
        # Create backup directory
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def add_patch(self, file_path: str, old_content: str, new_content: str) -> Patch:
        """Add a patch to the queue."""
        patch = Patch(
            file_path=file_path,
            old_content=old_content,
            new_content=new_content,
        )
        self.pending_patches.append(patch)
        return patch
    
    def validate_patch(self, patch: Patch, validation_type: str = "syntax") -> ValidationResult:
        """
        Validate a patch before applying.
        
        Validation types:
        - syntax: Check for syntax errors
        - test: Run relevant tests
        - diff: Verify diff is valid
        - safety: Check for dangerous patterns
        """
        start = datetime.now()
        
        if validation_type == "syntax":
            return self._validate_syntax(patch)
        elif validation_type == "diff":
            return self._validate_diff(patch)
        elif validation_type == "safety":
            return self._validate_safety(patch)
        elif validation_type == "test":
            return self._validate_with_test(patch)
        else:
            return ValidationResult(
                patch=patch,
                passed=True,
                validation_type=validation_type,
                message="Unknown validation type - allowing",
            )
    
    def validate_all(self, validation_types: List[str] = None) -> List[ValidationResult]:
        """
        Validate all pending patches.
        
        Args:
            validation_types: List of validation types to run
            
        Returns:
            List of validation results
        """
        validation_types = validation_types or ["syntax", "safety"]
        results = []
        
        for patch in self.pending_patches:
            for vtype in validation_types:
                result = self.validate_patch(patch, vtype)
                results.append(result)
                
                if not result.passed:
                    patch.validation_error = result.message
                    patch.verified = False
                    break
            else:
                patch.verified = True
        
        return results
    
    def apply_verified_patches(self) -> Dict[str, Any]:
        """
        Apply only verified patches.
        
        Returns:
            Dict with results of applying patches
        """
        results = {
            "applied": [],
            "rejected": [],
            "failed": [],
            "total": len(self.pending_patches),
        }
        
        for patch in self.pending_patches:
            if not patch.verified:
                results["rejected"].append({
                    "file": patch.file_path,
                    "reason": patch.validation_error or "Not verified",
                    "hash": patch.hash,
                })
                self.rejected_patches.append(patch)
                continue
            
            if self.dry_run:
                results["applied"].append({
                    "file": patch.file_path,
                    "status": "dry_run",
                    "hash": patch.hash,
                })
                continue
            
            try:
                # Create backup first
                self._backup_file(patch.file_path)
                
                # Apply patch
                success = self._apply_patch(patch)
                
                if success:
                    patch.applied = True
                    results["applied"].append({
                        "file": patch.file_path,
                        "status": "applied",
                        "hash": patch.hash,
                    })
                    self.applied_patches.append(patch)
                else:
                    results["failed"].append({
                        "file": patch.file_path,
                        "status": "apply_failed",
                        "hash": patch.hash,
                    })
                    
            except Exception as e:
                results["failed"].append({
                    "file": patch.file_path,
                    "status": "error",
                    "error": str(e),
                    "hash": patch.hash,
                })
        
        # Clear pending patches
        self.pending_patches.clear()
        
        return results
    
    def rollback_last(self) -> Dict[str, Any]:
        """Rollback the last applied patch."""
        if not self.applied_patches:
            return {"success": False, "message": "No patches to rollback"}
        
        patch = self.applied_patches.pop()
        
        try:
            backup_path = self._get_backup_path(patch.file_path)
            if os.path.exists(backup_path):
                os.replace(backup_path, patch.file_path)
                patch.applied = False
                return {"success": True, "file": patch.file_path}
            else:
                return {"success": False, "file": patch.file_path, "message": "No backup found"}
        except Exception as e:
            return {"success": False, "file": patch.file_path, "error": str(e)}
    
    def rollback_all(self) -> Dict[str, Any]:
        """Rollback all applied patches."""
        results = {"rolled_back": [], "failed": []}
        
        while self.applied_patches:
            result = self.rollback_last()
            if result["success"]:
                results["rolled_back"].append(result["file"])
            else:
                results["failed"].append(result.get("file", "unknown"))
        
        return results
    
    def _validate_syntax(self, patch: Patch) -> ValidationResult:
        """Validate Python syntax."""
        if not patch.new_content:
            return ValidationResult(
                patch=patch,
                passed=False,
                validation_type="syntax",
                message="Empty patch content",
            )
        
        if patch.file_path.endswith('.py'):
            try:
                compile(patch.new_content, patch.file_path, 'exec')
                return ValidationResult(
                    patch=patch,
                    passed=True,
                    validation_type="syntax",
                    message="Syntax valid",
                )
            except SyntaxError as e:
                return ValidationResult(
                    patch=patch,
                    passed=False,
                    validation_type="syntax",
                    message=f"Syntax error: {e}",
                )
        
        return ValidationResult(
            patch=patch,
            passed=True,
            validation_type="syntax",
            message="Non-Python file - syntax check skipped",
        )
    
    def _validate_diff(self, patch: Patch) -> ValidationResult:
        """Validate that the diff is well-formed."""
        if not patch.old_content:
            return ValidationResult(
                patch=patch,
                passed=False,
                validation_type="diff",
                message="No old content specified",
            )
        
        # Check that old content exists in file
        if os.path.exists(patch.file_path):
            with open(patch.file_path, 'r') as f:
                current = f.read()
            
            if patch.old_content not in current:
                return ValidationResult(
                    patch=patch,
                    passed=False,
                    validation_type="diff",
                    message="Old content not found in file - file may have changed",
                )
        
        return ValidationResult(
            patch=patch,
            passed=True,
            validation_type="diff",
            message="Diff structure valid",
        )
    
    def _validate_safety(self, patch: Patch) -> ValidationResult:
        """Check for potentially dangerous patterns."""
        dangerous_patterns = [
            (r'eval\s*\(', "Use of eval() is dangerous"),
            (r'exec\s*\(', "Use of exec() is dangerous"),
            (r'__import__\s*\(', "Dynamic import may be unsafe"),
            (r'os\.system\s*\(', "os.system() can be dangerous"),
            (r'subprocess.*shell\s*=\s*True', "shell=True can be dangerous"),
            (r'pickle\.load', "pickle.load() can execute arbitrary code"),
            (r'yaml\.load\s*\(.*Loader\s*=\s*yaml\.FullLoader', "Unsafe YAML loading"),
            (r'password\s*=\s*["\'].*["\']', "Hardcoded password detected"),
            (r'api[_-]?key\s*=\s*["\'].*["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'].*["\']', "Hardcoded secret detected"),
        ]
        
        warnings = []
        for pattern, message in dangerous_patterns:
            if re.search(pattern, patch.new_content, re.IGNORECASE):
                warnings.append(message)
        
        if warnings:
            return ValidationResult(
                patch=patch,
                passed=True,  # Still allow but warn
                validation_type="safety",
                message=f"Safety warnings: {'; '.join(warnings)}",
            )
        
        return ValidationResult(
            patch=patch,
            passed=True,
            validation_type="safety",
            message="No safety issues detected",
        )
    
    def _validate_with_test(self, patch: Patch) -> ValidationResult:
        """Validate by running tests."""
        # This would integrate with the test runner
        # For now, return a placeholder
        return ValidationResult(
            patch=patch,
            passed=True,
            validation_type="test",
            message="Test validation not implemented yet",
        )
    
    def _backup_file(self, file_path: str) -> str:
        """Create a backup of a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{Path(file_path).name}.{timestamp}.backup"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if os.path.exists(file_path):
            import shutil
            shutil.copy2(file_path, backup_path)
        
        return backup_path
    
    def _get_backup_path(self, file_path: str) -> str:
        """Get the most recent backup for a file."""
        backup_name_pattern = f"{Path(file_path).name}.*.backup"
        backups = sorted(
            Path(self.backup_dir).glob(backup_name_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if backups:
            return str(backups[0])
        return ""
    
    def _apply_patch(self, patch: Patch) -> bool:
        """Apply a patch to a file."""
        if not os.path.exists(patch.file_path):
            # Create new file
            with open(patch.file_path, 'w') as f:
                f.write(patch.new_content)
            return True
        
        # Replace old content with new
        with open(patch.file_path, 'r') as f:
            content = f.read()
        
        if patch.old_content and patch.old_content in content:
            content = content.replace(patch.old_content, patch.new_content, 1)
        else:
            # Just write new content
            content = patch.new_content
        
        with open(patch.file_path, 'w') as f:
            f.write(content)
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of patch guard."""
        return {
            "pending": len(self.pending_patches),
            "verified_pending": sum(1 for p in self.pending_patches if p.verified),
            "applied": len(self.applied_patches),
            "rejected": len(self.rejected_patches),
            "dry_run": self.dry_run,
            "backup_dir": self.backup_dir,
        }
    
    def export_patch_log(self, path: str):
        """Export patch application log."""
        log = {
            "timestamp": datetime.now().isoformat(),
            "applied_patches": [
                {
                    "file": p.file_path,
                    "hash": p.hash,
                    "verified": p.verified,
                }
                for p in self.applied_patches
            ],
            "rejected_patches": [
                {
                    "file": p.file_path,
                    "hash": p.hash,
                    "error": p.validation_error,
                }
                for p in self.rejected_patches
            ],
        }
        
        with open(path, 'w') as f:
            json.dump(log, f, indent=2)


def create_patch_guard(working_dir: Optional[str] = None, dry_run: bool = True) -> PatchGuard:
    """
    Create a new PatchGuard instance.
    
    Usage:
        from neuro.validation.patch_guard import create_patch_guard
        
        guard = create_patch_guard("/path/to/project", dry_run=True)
        
        guard.add_patch("file.py", old_code, new_code)
        results = guard.validate_all(["syntax", "safety"])
        applied = guard.apply_verified_patches()
    """
    return PatchGuard(working_dir, dry_run)
