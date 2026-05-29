# Context Window Optimizer - Claude Code Level
# Intelligent context management and token optimization
# Features: smart truncation, summary injection, priority-based context

import re
import os
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import deque
from datetime import datetime
from neuro.skills.skill_middleware import register_skill


class ContextPriority(Enum):
    """Priority levels for context items."""
    CRITICAL = 0    # System prompts, core instructions
    HIGH = 1        # Recent changes, active files
    MEDIUM = 2      # Recent history, partial context
    LOW = 3         # Background info, old context
    IGNORABLE = 4   # Can be dropped first


@dataclass
class ContextItem:
    """A context item with priority and metadata."""
    content: str
    priority: ContextPriority
    source: str  # 'file', 'history', 'memory', 'system'
    token_count: int = 0
    created_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.token_count:
            self.token_count = len(self.content) // 4  # Rough estimate
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ContextBudget:
    """Budget for context management."""
    max_tokens: int = 100000
    max_items: int = 100
    preserve_recent: int = 10  # Keep last N items regardless of priority
    summary_threshold: int = 20000  # When to start summarizing
    truncate_types: List[str] = field(default_factory=list)


@dataclass
class TruncationResult:
    """Result of context truncation."""
    original_tokens: int
    truncated_tokens: int
    removed_items: List[str]
    summaries_added: List[str]
    preserved_sources: List[str]


class TokenCounter:
    """Simple tokenizer for Python."""
    
    # Common English words for basic tokenization
    COMMON_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'it', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'what',
        'which', 'who', 'when', 'where', 'why', 'how', 'not', 'no', 'yes', 'all',
        'any', 'each', 'every', 'some', 'more', 'most', 'other', 'such', 'so',
    }
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Count approximate tokens in text."""
        # Split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Count: ~4 chars per token on average
        raw_count = len(text) // 4
        
        # Adjust based on word count (more accurate)
        word_count = len(words)
        
        # Combine estimates
        return max(raw_count, word_count)
    
    @staticmethod
    def estimate_tokens_from_chars(chars: int) -> int:
        """Estimate tokens from character count."""
        return chars // 4


class SemanticChunker:
    """Split context into semantically meaningful chunks."""
    
    @staticmethod
    def chunk_by_lines(content: str, max_tokens: int = 2000) -> List[str]:
        """Split into line-based chunks."""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = TokenCounter.count_tokens(line)
            
            if current_tokens + line_tokens > max_tokens and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    @staticmethod
    def chunk_by_paragraphs(content: str) -> List[str]:
        """Split into paragraph-based chunks."""
        paragraphs = re.split(r'\n\s*\n', content)
        return [p.strip() for p in paragraphs if p.strip()]


class ContextSummarizer:
    """Summarize context items for compression."""
    
    # Patterns for compression
    REMOVE_PATTERNS = [
        (r'//.*$', ''),                    # Remove single-line comments
        (r'/\*.*?\*/', '', re.DOTALL),     # Remove multi-line comments
        (r'#"[^"]*"', ''),                 # Remove docstrings
        (r';;.*$', ''),                    # Remove Lisp comments
        (r'<!--.*?-->', '', re.DOTALL),    # Remove HTML comments
    ]
    
    @staticmethod
    def compress_code(code: str) -> str:
        """Compress code by removing comments and whitespace."""
        result = code
        
        for pattern, replacement, *flags in SemanticChunker.REMOVE_PATTERNS:
            flags = flags[0] if flags else 0
            result = re.sub(pattern, replacement, result, flags=flags)
        
        # Remove extra whitespace
        result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
        result = re.sub(r'[ \t]+', ' ', result)
        
        return result.strip()
    
    @staticmethod
    def summarize_file(filepath: str, max_lines: int = 100) -> str:
        """Create a summary of a file."""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()[:max_lines]
            
            content = ''.join(lines)
            
            # Extract structure
            functions = re.findall(r'def (\w+)', content)
            classes = re.findall(r'class (\w+)', content)
            imports = re.findall(r'(?:from|import) (\w+)', content)
            
            summary = f"# {filepath}\n"
            
            if classes:
                summary += f"Classes: {', '.join(classes)}\n"
            if functions:
                summary += f"Functions: {', '.join(functions)}\n"
            if imports:
                summary += f"Imports: {', '.join(imports[:10])}\n"
            
            summary += f"... ({len(lines)} lines shown)\n"
            
            return summary
        except Exception as e:
            return f"# {filepath}: Error reading file"
    
    @staticmethod
    def summarize_diff(diff: str) -> str:
        """Summarize a diff for context."""
        lines = diff.split('\n')
        
        added = sum(1 for l in lines if l.startswith('+') and not l.startswith('+++'))
        removed = sum(1 for l in lines if l.startswith('-') and not l.startswith('---'))
        
        files_changed = set()
        for l in lines:
            if l.startswith('diff') or l.startswith('==='):
                match = re.search(r'diff.*(\S+\.\w+)', l)
                if match:
                    files_changed.add(match.group(1))
        
        summary = f"Changes: +{added}/-{removed} lines in {len(files_changed)} files"
        summary += f"\nFiles: {', '.join(list(files_changed)[:5])}"
        
        if len(files_changed) > 5:
            summary += f" and {len(files_changed) - 5} more"
        
        return summary


@register_skill("context_optimizer", "Intelligent context management and token optimization", category="agent_core")
class ContextOptimizer:
    """
    Claude Code-level context window optimization.
    
    Features:
    - Priority-based context preservation
    - Smart truncation and summarization
    - Token budget management
    - File-aware context injection
    
    Usage:
        from neuro.skills.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer(max_tokens=80000)
        optimized = optimizer.optimize(messages, active_files=["app.py"])
    """
    
    def __init__(self, budget: ContextBudget = None):
        self.budget = budget or ContextBudget()
        self.token_counter = TokenCounter()
        self.chunker = SemanticChunker()
        self.summarizer = ContextSummarizer()
        self.total_tokens_used = 0
        
        # Cache for summarization
        self._summary_cache: Dict[str, str] = {}
    
    def optimize(self, messages: List[Dict[str, Any]], 
                 active_files: List[str] = None,
                 task_context: str = None) -> Tuple[List[Dict[str, Any]], TruncationResult]:
        """
        Optimize message context within token budget.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            active_files: Files currently being worked on (high priority)
            task_context: Current task description
            
        Returns:
            Tuple of (optimized_messages, truncation_result)
        """
        active_files = active_files or []
        
        # Extract context items from messages
        items = self._extract_items(messages)
        
        # Add task context as high priority
        if task_context:
            items.insert(0, ContextItem(
                content=f"TASK: {task_context}",
                priority=ContextPriority.HIGH,
                source="task"
            ))
        
        # Sort by priority
        sorted_items = self._sort_by_priority(items, active_files)
        
        # Truncate to budget
        truncated_items, result = self._truncate_to_budget(sorted_items)
        
        # Rebuild messages
        optimized = self._rebuild_messages(truncated_items)
        
        self.total_tokens_used += result.truncated_tokens
        return optimized, result
    
    def _extract_items(self, messages: List[Dict[str, Any]]) -> List[ContextItem]:
        """Extract context items from messages."""
        items = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            tokens = self.token_counter.count_tokens(content)
            
            # Determine priority based on role
            if role == 'system':
                priority = ContextPriority.CRITICAL
            elif role == 'assistant':
                priority = ContextPriority.MEDIUM
            else:
                priority = ContextPriority.HIGH
            
            items.append(ContextItem(
                content=content,
                priority=priority,
                source=f"message_{role}",
                token_count=tokens,
                metadata={'role': role}
            ))
        
        return items
    
    def _sort_by_priority(self, items: List[ContextItem],
                         active_files: List[str]) -> List[ContextItem]:
        """Sort items by priority."""
        def priority_key(item: ContextItem) -> Tuple[int, int, int]:
            # Check if this item references active files
            is_active = 0
            for f in active_files:
                if f in item.content:
                    is_active = 1
                    break
            
            return (item.priority.value, -is_active, item.created_at)
        
        return sorted(items, key=priority_key)
    
    def _truncate_to_budget(self, items: List[ContextItem]) -> Tuple[List[ContextItem], TruncationResult]:
        """Truncate items to fit within token budget."""
        result = TruncationResult(
            original_tokens=sum(i.token_count for i in items),
            truncated_tokens=0,
            removed_items=[],
            summaries_added=[],
            preserved_sources=[]
        )
        
        kept_items = []
        
        # First, always keep CRITICAL items
        for item in items:
            if item.priority == ContextPriority.CRITICAL:
                kept_items.append(item)
                result.preserved_sources.append(item.source)
        
        # Calculate tokens used
        current_tokens = sum(i.token_count for i in kept_items)
        result.truncated_tokens = current_tokens
        
        # Add items until budget reached
        for item in items:
            if item.priority == ContextPriority.CRITICAL:
                continue
            
            # Check budget
            if current_tokens + item.token_count > self.budget.max_tokens:
                # Try to summarize instead of dropping
                if self.budget.summary_threshold and current_tokens > self.budget.summary_threshold:
                    summary = self._summarize_if_needed(item)
                    if summary:
                        kept_items.append(summary)
                        result.summaries_added.append(item.source)
                        current_tokens += summary.token_count
                        continue
                
                # Skip if can't fit
                result.removed_items.append(item.source)
                continue
            
            kept_items.append(item)
            current_tokens += item.token_count
            result.preserved_sources.append(item.source)
        
        result.truncated_tokens = current_tokens
        return kept_items, result
    
    def _summarize_if_needed(self, item: ContextItem) -> Optional[ContextItem]:
        """Create a summary of an item instead of dropping it."""
        cache_key = f"{item.source}:{item.content[:100]}"
        
        if cache_key in self._summary_cache:
            return self._summary_cache[cache_key]
        
        # Determine summarization strategy
        if item.source.startswith('message_'):
            summary_content = f"[Context from {item.source}]:\n{item.content[:500]}..."
        elif '.py' in item.source or '.js' in item.source:
            summary_content = self.summarizer.summarize_file(item.source)
        else:
            summary_content = f"[Summary]: {item.content[:300]}..."
        
        summary_tokens = self.token_counter.count_tokens(summary_content)
        
        summary = ContextItem(
            content=summary_content,
            priority=item.priority,
            source=f"summary_{item.source}",
            token_count=summary_tokens,
            metadata={'original_source': item.source}
        )
        
        self._summary_cache[cache_key] = summary
        return summary
    
    def _rebuild_messages(self, items: List[ContextItem]) -> List[Dict[str, Any]]:
        """Rebuild messages from context items."""
        messages = []
        
        by_role = {}
        for item in items:
            role = item.metadata.get('role', 'user')
            if role not in by_role:
                by_role[role] = []
            by_role[role].append(item)
        
        # Rebuild in order (system, user, assistant)
        for role in ['system', 'user', 'assistant']:
            if role in by_role:
                for item in by_role[role]:
                    messages.append({
                        'role': role,
                        'content': item.content
                    })
        
        return messages
    
    def inject_file_context(self, messages: List[Dict],
                           filepath: str,
                           max_lines: int = 200) -> List[Dict]:
        """Inject file context into messages."""
        summary = self.summarizer.summarize_file(filepath, max_lines)
        
        # Add as system message or inject into existing
        existing_system = None
        for i, msg in enumerate(messages):
            if msg.get('role') == 'system':
                existing_system = i
                break
        
        summary_msg = {
            'role': 'system',
            'content': f"\n\n### Active File Context ###\n{summary}\n\n"
        }
        
        if existing_system is not None:
            messages[existing_system]['content'] += summary_msg['content']
        else:
            messages.insert(0, summary_msg)
        
        return messages
    
    def get_token_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get token statistics for messages."""
        stats = {
            'total': 0,
            'system': 0,
            'user': 0,
            'assistant': 0
        }
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            tokens = self.token_counter.count_tokens(content)
            
            stats['total'] += tokens
            if role in stats:
                stats[role] += tokens
        
        return stats


def quick_optimize(messages: List[Dict], max_tokens: int = 80000) -> List[Dict]:
    """Quick context optimization."""
    optimizer = ContextOptimizer(ContextBudget(max_tokens=max_tokens))
    optimized, _ = optimizer.optimize(messages)
    return optimized


def get_token_estimate(text: str) -> int:
    """Quick token estimation."""
    return TokenCounter.count_tokens(text)


# SKILL.md content
SKILL_MD = """
---
name: context-optimizer
description: Intelligent context management and token optimization for large contexts
triggers:
  - context
  - token
  - optimize
  - truncate
  - memory
---

# Context Window Optimizer

Intelligent context management similar to Claude Code's context handling.

## Features

### Token Budget Management
- Set maximum tokens per request
- Prioritize critical context
- Track token usage

### Smart Truncation
- Priority-based preservation
- Active file awareness
- Semantic chunking

### Summarization
- Auto-summarize long files
- Compress code by removing comments
- Cache summaries for reuse

## Usage

```python
from neuro.skills.context_optimizer import (
    ContextOptimizer, ContextBudget, quick_optimize
)

# Quick optimization
optimized = quick_optimize(messages, max_tokens=80000)

# Full control
budget = ContextBudget(
    max_tokens=100000,
    summary_threshold=30000
)
optimizer = ContextOptimizer(budget)
optimized, result = optimizer.optimize(
    messages,
    active_files=['app.py'],
    task_context="Fix authentication bug"
)

# Get stats
stats = optimizer.get_token_stats(messages)
```
"""
