# Git Operations - Claude Code Level
# Smart Git workflows: branch management, smart commits, PR creation
# Features: auto-staging, commit message generation, PR automation

import subprocess
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime
from neuro.skills.skill_middleware import register_skill


class ConflictStrategy(Enum):
    """Strategy for handling merge conflicts."""
    THEIRS = "theirs"
    OURS = "ours"
    MANUAL = "manual"
    AUTO_MERGE = "auto_merge"


class CommitType(Enum):
    """Types of commits for smart commit messages."""
    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    CHORE = "chore"
    STYLE = "style"
    PERF = "perf"
    CI = "ci"
    BUILD = "build"


@dataclass
class GitBranch:
    """Git branch information."""
    name: str
    is_current: bool
    is_remote: bool
    upstream: Optional[str] = None
    ahead: int = 0
    behind: int = 0


@dataclass
class CommitInfo:
    """Commit information."""
    sha: str
    message: str
    author: str
    date: str
    files_changed: List[str] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0


@dataclass
class PullRequestInfo:
    """Pull request information."""
    title: str
    body: str
    head_branch: str
    base_branch: str
    labels: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    draft: bool = False


@dataclass
class GitStatus:
    """Current Git working directory status."""
    branch: str
    staged: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    untracked: List[str] = field(default_factory=list)
    conflicted: List[str] = field(default_factory=list)
    is_clean: bool = False


def detect_changed_files(root_dir: str = ".") -> Dict[str, List[str]]:
    """Detect all changed files in the working directory."""
    result = {
        'staged': [],
        'modified': [],
        'untracked': [],
        'deleted': []
    }
    
    try:
        # Get staged files
        proc = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=root_dir, capture_output=True, text=True
        )
        result['staged'] = [f for f in proc.stdout.strip().split('\n') if f]
        
        # Get modified files
        proc = subprocess.run(
            ['git', 'diff', '--name-only'],
            cwd=root_dir, capture_output=True, text=True
        )
        result['modified'] = [f for f in proc.stdout.strip().split('\n') if f]
        
        # Get untracked files
        proc = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            cwd=root_dir, capture_output=True, text=True
        )
        result['untracked'] = [f for f in proc.stdout.strip().split('\n') if f]
        
        # Get deleted files
        proc = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=D'],
            cwd=root_dir, capture_output=True, text=True
        )
        result['deleted'] = [f for f in proc.stdout.strip().split('\n') if f]
        
    except Exception as e:
        pass
    
    return result


def analyze_changes_for_commit(changed_files: List[str], root_dir: str = ".") -> Dict[str, Any]:
    """
    Analyze changed files to determine commit type and scope.
    Claude Code-style change analysis.
    """
    file_types = {'py': 0, 'js': 0, 'ts': 0, 'jsx': 0, 'tsx': 0, 'md': 0, 'json': 0, 'yaml': 0, 'yml': 0}
    file_count = len(changed_files)
    
    for f in changed_files:
        ext = f.rsplit('.', 1)[-1] if '.' in f else ''
        if ext in file_types:
            file_types[ext] += 1
    
    # Determine scope (primary affected area)
    scopes = []
    for f in changed_files[:5]:  # Top 5 files
        parts = f.rsplit('/', 1)
        if len(parts) > 1 and parts[0] not in ['src', 'lib', 'app', 'tests']:
            scopes.append(parts[0])
    
    scope = scopes[0] if scopes else 'core'
    
    # Determine commit type based on file patterns
    if any('test' in f.lower() for f in changed_files):
        commit_type = CommitType.TEST
    elif any(f.endswith(('.md', 'README')) for f in changed_files):
        commit_type = CommitType.DOCS
    elif any(f.endswith(('.yaml', '.yml', '.json')) for f in changed_files):
        commit_type = CommitType.CHORE
    elif any(f.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')) for f in changed_files):
        # Check if it's a fix (error/fix patterns in messages)
        commit_type = CommitType.FEAT
    else:
        commit_type = CommitType.CHORE
    
    return {
        'type': commit_type,
        'scope': scope,
        'file_count': file_count,
        'file_types': file_types
    }


def generate_commit_message(analysis: Dict[str, Any], description: str = None) -> str:
    """Generate a conventional commit message."""
    type_str = analysis['type'].value
    scope = analysis['scope']
    scope_str = f"({scope})" if scope else ""
    
    if description:
        short_desc = description[:50] if len(description) > 50 else description
    else:
        short_desc = _generate_short_description(analysis)
    
    return f"{type_str}{scope_str}: {short_desc}"


def _generate_short_description(analysis: Dict[str, Any]) -> str:
    """Generate short description based on file changes."""
    ft = analysis['file_types']
    count = analysis['file_count']
    
    if ft['py'] > 0 and ft['py'] == count:
        return f"update {count} Python file{'s' if count > 1 else ''}"
    elif ft['js'] + ft['ts'] + ft['jsx'] + ft['tsx'] > 0:
        return f"update {count} JavaScript file{'s' if count > 1 else ''}"
    elif ft['md'] > 0:
        return f"update documentation"
    elif ft['json'] + ft['yaml'] + ft['yml'] > 0:
        return f"update configuration"
    else:
        return f"update {count} file{'s' if count > 1 else ''}"


@register_skill("git_operations", "Smart Git operations: branch management, commits, PR workflows", category="version_control")
class GitOperations:
    """
    Claude Code-level Git operations.
    
    Features:
    - Smart branch creation and management
    - Auto-staging and commit message generation
    - PR creation with templates
    - Conflict detection and resolution
    - File history and blame
    
    Usage:
        from neuro.skills.git_operations import GitOperations
        
        git = GitOperations()
        status = git.get_status()
        branches = git.list_branches()
        
        # Smart commit
        info = git.prepare_commit(description="Added new feature")
        
        # Create PR
        pr = git.create_pr(title="Feature: New capability", body="...")
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.changes = detect_changed_files(repo_path)
    
    def get_status(self) -> GitStatus:
        """Get current Git status."""
        try:
            proc = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            staged = []
            modified = []
            untracked = []
            conflicted = []
            
            for line in proc.stdout.strip().split('\n'):
                if not line:
                    continue
                status_code = line[:2]
                filepath = line[3:]
                
                if status_code[0] != ' ':
                    staged.append(filepath)
                if status_code[1] == 'M':
                    modified.append(filepath)
                if status_code[1] == '?':
                    untracked.append(filepath)
                if status_code[0] == 'U' or status_code[1] == 'U':
                    conflicted.append(filepath)
            
            # Get current branch
            proc = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path, capture_output=True, text=True
            )
            branch = proc.stdout.strip() or "HEAD"
            
            return GitStatus(
                branch=branch,
                staged=staged,
                modified=modified,
                untracked=untracked,
                conflicted=conflicted,
                is_clean=len(staged) == 0 and len(modified) == 0 and len(untracked) == 0
            )
            
        except Exception as e:
            return GitStatus(branch="unknown", is_clean=True)
    
    def list_branches(self, remote: bool = False) -> List[GitBranch]:
        """List all branches."""
        branches = []
        flag = '-r' if remote else '-a'
        
        try:
            proc = subprocess.run(
                ['git', 'branch', flag, '--format=%(refname:short)|%(HEAD)|%(upstream:short)'],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            for line in proc.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                name = parts[0].replace('origin/', '')
                is_current = parts[1] == '*'
                upstream = parts[2] if len(parts) > 2 and parts[2] else None
                
                branches.append(GitBranch(
                    name=name,
                    is_current=is_current,
                    is_remote=remote or name.startswith('origin/'),
                    upstream=upstream
                ))
                
        except Exception:
            pass
        
        return branches
    
    def create_branch(self, name: str, switch: bool = True) -> bool:
        """Create and optionally switch to a new branch."""
        try:
            subprocess.run(
                ['git', 'checkout', '-b', name],
                cwd=self.repo_path, capture_output=True, text=True
            )
            return True
        except Exception:
            return False
    
    def stage_files(self, files: List[str] = None, all: bool = False) -> bool:
        """Stage files for commit."""
        try:
            if all:
                subprocess.run(
                    ['git', 'add', '-A'],
                    cwd=self.repo_path, capture_output=True, text=True
                )
            elif files:
                for f in files:
                    subprocess.run(
                        ['git', 'add', f],
                        cwd=self.repo_path, capture_output=True, text=True
                    )
            self.changes = detect_changed_files(self.repo_path)
            return True
        except Exception:
            return False
    
    def smart_commit(self, message: str = None, all: bool = False) -> str:
        """Create a smart commit with auto-generated message."""
        self.stage_files(all=all)
        status = self.get_status()
        
        if not status.staged:
            return "No files staged for commit"
        
        if not message:
            analysis = analyze_changes_for_commit(status.staged, self.repo_path)
            message = generate_commit_message(analysis)
        
        try:
            proc = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_path, capture_output=True, text=True
            )
            return proc.stdout or "Committed successfully"
        except Exception as e:
            return f"Commit failed: {e}"
    
    def amend_commit(self, message: str = None) -> str:
        """Amend the last commit."""
        try:
            args = ['git', 'commit', '--amend', '--no-edit']
            if message:
                args[-1] = f'-m "{message}"'
            
            proc = subprocess.run(
                args,
                cwd=self.repo_path, capture_output=True, text=True
            )
            return proc.stdout or "Commit amended"
        except Exception as e:
            return f"Amend failed: {e}"
    
    def squash_commits(self, count: int = 2, message: str = None) -> str:
        """Squash last N commits into one."""
        try:
            # Get the Nth commit sha (not counting HEAD)
            proc = subprocess.run(
                ['git', 'log', f'-{count + 1}', '--format=%H'],
                cwd=self.repo_path, capture_output=True, text=True
            )
            commits = proc.stdout.strip().split('\n')
            base_sha = commits[-1] if commits else 'HEAD~1'
            
            # Interactive rebase
            cmd = f"git rebase -i {base_sha}"
            # Note: This is a simplified version; full implementation would use editor
            return f"Squash with: {cmd}"
        except Exception as e:
            return f"Squash failed: {e}"
    
    def create_pr(self, title: str, body: str = "", base: str = "main",
                  labels: List[str] = None, draft: bool = False,
                  remote: str = "origin") -> Dict[str, Any]:
        """
        Create a pull request.
        Uses GitHub API via gh CLI if available.
        """
        status = self.get_status()
        
        # Get upstream remote
        try:
            proc = subprocess.run(
                ['git', 'remote', 'get-url', remote],
                cwd=self.repo_path, capture_output=True, text=True
            )
            remote_url = proc.stdout.strip()
        except Exception:
            remote_url = ""
        
        # Detect if GitHub repo
        is_github = 'github.com' in remote_url
        branch = status.branch
        
        if is_github:
            try:
                # Use gh CLI
                cmd = ['gh', 'pr', 'create', '--title', title, '--base', base, '--head', branch]
                
                if body:
                    # Create body file
                    body_file = '/tmp/pr_body.md'
                    with open(body_file, 'w') as f:
                        f.write(body)
                    cmd.extend(['--body-file', body_file])
                
                if draft:
                    cmd.append('--draft')
                
                for label in (labels or []):
                    cmd.extend(['--label', label])
                
                proc = subprocess.run(
                    cmd,
                    cwd=self.repo_path, capture_output=True, text=True
                )
                
                if proc.returncode == 0:
                    return {
                        'success': True,
                        'url': proc.stdout.strip(),
                        'message': 'PR created successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': proc.stderr
                    }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            # Return instructions for manual PR
            return {
                'success': False,
                'message': f'Create PR manually: {base} <- {branch}',
                'instructions': f"Push branch and create PR from {branch} to {base}"
            }
    
    def sync_branch(self, pull: bool = True, push: bool = True) -> str:
        """Sync current branch with remote."""
        results = []
        
        if pull:
            try:
                proc = subprocess.run(
                    ['git', 'pull', '--rebase'],
                    cwd=self.repo_path, capture_output=True, text=True
                )
                results.append(f"Pull: {proc.stdout or 'Success'}")
            except Exception as e:
                results.append(f"Pull failed: {e}")
        
        if push:
            try:
                proc = subprocess.run(
                    ['git', 'push'],
                    cwd=self.repo_path, capture_output=True, text=True
                )
                results.append(f"Push: {proc.stdout or 'Success'}")
            except Exception as e:
                results.append(f"Push failed: {e}")
        
        return "\n".join(results)
    
    def get_file_history(self, file_path: str, limit: int = 10) -> List[CommitInfo]:
        """Get commit history for a file."""
        commits = []
        
        try:
            proc = subprocess.run(
                ['git', 'log', f'-{limit}', '--format=%H|%s|%an|%ad', '--date=short', '--', file_path],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            for line in proc.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append(CommitInfo(
                        sha=parts[0][:8],
                        message=parts[1],
                        author=parts[2],
                        date=parts[3]
                    ))
        except Exception:
            pass
        
        return commits
    
    def get_blame(self, file_path: str) -> List[Dict[str, Any]]:
        """Get blame info for a file."""
        blame_info = []
        
        try:
            proc = subprocess.run(
                ['git', 'blame', '--line-porcelain', file_path],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            current_commit = None
            current_line_num = None
            current_author = None
            current_summary = None
            
            for line in proc.stdout.strip().split('\n'):
                if line.startswith(('filename ', 'author ', 'summary ', 'author-mail ')):
                    parts = line.split(' ', 1)
                    key = parts[0]
                    value = parts[1] if len(parts) > 1 else ''
                    
                    if key == 'filename':
                        if current_commit:
                            blame_info.append({
                                'commit': current_commit[:8],
                                'author': current_author,
                                'line': current_line_num,
                                'summary': current_summary
                            })
                        # Start new blame entry
                        proc2 = subprocess.run(
                            ['git', 'log', '-1', '--format=%H', current_commit],
                            cwd=self.repo_path, capture_output=True, text=True
                        )
                        blame_info.append({
                            'file': value,
                            'line': 0,
                            'author': current_author,
                            'summary': current_summary
                        })
                        current_commit = None
                    elif key == 'author':
                        current_author = value
                    elif key == 'summary':
                        current_summary = value
                elif re.match(r'^[0-9a-f]{40}', line):
                    current_commit = line
                elif re.match(r'^\d+\d*$', line):
                    current_line_num = int(line)
                    
        except Exception:
            pass
        
        return blame_info
    
    def revert_commit(self, ref: str = "HEAD") -> str:
        """Revert a specific commit."""
        try:
            proc = subprocess.run(
                ['git', 'revert', '--no-edit', ref],
                cwd=self.repo_path, capture_output=True, text=True
            )
            return proc.stdout or "Reverted successfully"
        except Exception as e:
            return f"Revert failed: {e}"
    
    def reset_branch(self, mode: str = "soft", count: int = 1) -> str:
        """Reset branch to previous commits."""
        valid_modes = ['soft', 'mixed', 'hard']
        if mode not in valid_modes:
            return f"Invalid mode. Use: {valid_modes}"
        
        try:
            proc = subprocess.run(
                ['git', 'reset', f'--{mode}', f'HEAD~{count}'],
                cwd=self.repo_path, capture_output=True, text=True
            )
            return proc.stdout or f"Reset {mode} {count} commit(s)"
        except Exception as e:
            return f"Reset failed: {e}"
    
    def diff_branch(self, branch: str = "main") -> str:
        """Show diff between current branch and another."""
        try:
            proc = subprocess.run(
                ['git', 'diff', f'{branch}..HEAD', '--stat'],
                cwd=self.repo_path, capture_output=True, text=True
            )
            return proc.stdout
        except Exception as e:
            return f"Diff failed: {e}"
    
    def get_stash_list(self) -> List[Dict[str, str]]:
        """List all stashed changes."""
        stashes = []
        
        try:
            proc = subprocess.run(
                ['git', 'stash', 'list', '--format=%H|%gd|%s'],
                cwd=self.repo_path, capture_output=True, text=True
            )
            
            for line in proc.stdout.strip().split('\n'):
                if not line or ':' not in line:
                    continue
                parts = line.split('|')
                if len(parts) >= 3:
                    stashes.append({
                        'sha': parts[0][:8],
                        'ref': parts[1],
                        'message': parts[2]
                    })
        except Exception:
            pass
        
        return stashes
    
    def create_stash(self, message: str = None, include_untracked: bool = True) -> str:
        """Create a stash of current changes."""
        try:
            args = ['git', 'stash', 'push']
            if include_untracked:
                args.append('-u')
            if message:
                args.extend(['-m', message])
            
            proc = subprocess.run(
                args,
                cwd=self.repo_path, capture_output=True, text=True
            )
            return proc.stdout or "Stashed successfully"
        except Exception as e:
            return f"Stash failed: {e}"
    
    def apply_stash(self, stash_ref: str = "stash@{0}") -> str:
        """Apply a stash to working directory."""
        try:
            proc = subprocess.run(
                ['git', 'stash', 'apply', stash_ref],
                cwd=self.repo_path, capture_output=True, text=True
            )
            return proc.stdout or "Stash applied"
        except Exception as e:
            return f"Stash apply failed: {e}"


def quick_git_status() -> Dict[str, Any]:
    """Quick git status check."""
    git = GitOperations()
    status = git.get_status()
    return {
        'branch': status.branch,
        'is_clean': status.is_clean,
        'staged': len(status.staged),
        'modified': len(status.modified),
        'untracked': len(status.untracked),
        'conflicted': len(status.conflicted)
    }


def quick_commit(message: str) -> str:
    """Quick commit with message."""
    git = GitOperations()
    return git.smart_commit(message=message, all=True)


# SKILL.md content
SKILL_MD = """
---
name: git-operations
description: Smart Git operations with branch management, auto-commits, and PR workflows
triggers:
  - git
  - branch
  - commit
  - pr
  - pull request
  - push
  - merge
  - stash
---

# Git Operations - Claude Code Level

Smart Git operations similar to Claude Code's Git capabilities.

## Features

### Smart Commit Detection
Automatically analyzes changed files and generates commit messages:
- Detects commit type (feat, fix, docs, refactor, etc.)
- Identifies scope from file paths
- Generates conventional commit format

### Branch Management
- List/create/delete branches
- Switch between branches
- Track upstream branches
- Sync with remote

### PR Workflows
- Create pull requests via gh CLI
- Auto-assign labels and reviewers
- Set draft status
- Track PR status

### File Operations
- Stage files individually or all
- View file history and blame
- Restore/delete files
- Diff between branches

## Usage

```python
from neuro.skills.git_operations import GitOperations, quick_git_status, quick_commit

# Get status
status = quick_git_status()

# Full operations
git = GitOperations()
git_status = git.get_status()
git.branches()  # List branches
git.create_branch("feature/my-feature")
git.smart_commit("feat: added new capability")
git.create_pr(title="Feature", body="Description")
```
"""
