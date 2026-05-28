"""
Neuro Agent Memory System (swarmvault)
Persistent memory and knowledge management for autonomous agents
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum

class MemoryType(Enum):
    """Types of memory storage"""
    EPISODIC = "episodic"      # Task execution history
    SEMANTIC = "semantic"      # Learned knowledge and patterns
    WORKING = "working"         # Current context
    PROCEDURAL = "procedural"   # Learned procedures

@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    content: str
    memory_type: MemoryType
    context: Dict[str, Any]
    created_at: str
    accessed_at: str
    access_count: int = 0
    importance: float = 0.5  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    embedding_hash: Optional[str] = None

@dataclass
class MemoryInsight:
    """Extracted insight from memory"""
    pattern: str
    source_entries: List[str]
    confidence: float
    recommendation: str

class SwarmVault:
    """
    Agent Memory System (swarmvault)
    Provides persistent, searchable memory for autonomous agents
    """
    
    NAME = "agent_memory"
    DESCRIPTION = "Persistent agent memory system for learning from experience"
    TRIGGERS = ["memory", "remember", "learn", "context", "knowledge", "vault"]
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_entries: int = 10000,
        retention_days: int = 90
    ):
        self.storage_path = storage_path or Path.home() / ".neuro" / "memory"
        self.max_entries = max_entries
        self.retention_days = retention_days
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.episodic_file = self.storage_path / "episodic.json"
        self.semantic_file = self.storage_path / "semantic.json"
        self.working_file = self.storage_path / "working.json"
        self.procedural_file = self.storage_path / "procedural.json"
        self.index_file = self.storage_path / "index.json"
        
        self._memory_cache: Dict[MemoryType, List[MemoryEntry]] = {}
        self._index: Dict[str, Set[str]] = {}  # keyword -> entry IDs
        
        self._load_all()
    
    def _load_all(self):
        """Load all memory files"""
        files = {
            MemoryType.EPISODIC: self.episodic_file,
            MemoryType.SEMANTIC: self.semantic_file,
            MemoryType.WORKING: self.working_file,
            MemoryType.PROCEDURAL: self.procedural_file,
        }
        
        for mem_type, filepath in files.items():
            self._memory_cache[mem_type] = self._load_file(filepath)
    
    def _load_file(self, filepath: Path) -> List[MemoryEntry]:
        """Load memory entries from file"""
        if not filepath.exists():
            return []
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return [MemoryEntry(**entry) for entry in data]
        except (json.JSONDecodeError, TypeError):
            return []
    
    def _save_file(self, mem_type: MemoryType):
        """Save memory entries to file"""
        filepath_map = {
            MemoryType.EPISODIC: self.episodic_file,
            MemoryType.SEMANTIC: self.semantic_file,
            MemoryType.WORKING: self.working_file,
            MemoryType.PROCEDURAL: self.procedural_file,
        }
        
        filepath = filepath_map[mem_type]
        entries = self._memory_cache.get(mem_type, [])
        
        with open(filepath, 'w') as f:
            json.dump([asdict(e) for e in entries], f, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for memory entry"""
        return hashlib.sha256(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    
    def _update_index(self, entry: MemoryEntry):
        """Update search index"""
        words = set(entry.content.lower().split())
        words.update(entry.tags)
        
        for word in words:
            if len(word) > 2:  # Skip short words
                if word not in self._index:
                    self._index[word] = set()
                self._index[word].add(entry.id)
    
    def store(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5
    ) -> MemoryEntry:
        """Store a new memory entry"""
        now = datetime.now().isoformat()
        
        entry = MemoryEntry(
            id=self._generate_id(content),
            content=content,
            memory_type=memory_type,
            context=context or {},
            created_at=now,
            accessed_at=now,
            access_count=0,
            importance=importance,
            tags=tags or [],
            embedding_hash=hashlib.md5(content.encode()).hexdigest()
        )
        
        if memory_type not in self._memory_cache:
            self._memory_cache[memory_type] = []
        
        self._memory_cache[memory_type].append(entry)
        self._update_index(entry)
        self._save_file(memory_type)
        
        # Cleanup old entries if needed
        self._cleanup()
        
        return entry
    
    def recall(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Recall memories matching query"""
        results = []
        query_lower = query.lower()
        
        types_to_search = [memory_type] if memory_type else list(MemoryType)
        
        for mem_type in types_to_search:
            entries = self._memory_cache.get(mem_type, [])
            
            for entry in entries:
                # Update access stats
                entry.access_count += 1
                entry.accessed_at = datetime.now().isoformat()
                
                # Score by relevance
                score = 0
                if query_lower in entry.content.lower():
                    score += 10
                if any(query_lower in tag.lower() for tag in entry.tags):
                    score += 5
                score += entry.importance * 2
                score += entry.access_count * 0.1
                
                if score > 0:
                    results.append((score, entry))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]
    
    def learn_pattern(
        self,
        pattern: str,
        context: Dict[str, Any],
        examples: List[str],
        confidence: float = 0.8
    ) -> MemoryInsight:
        """Learn a new pattern from examples"""
        insight = MemoryInsight(
            pattern=pattern,
            source_entries=[],
            confidence=confidence,
            recommendation=f"Apply pattern '{pattern}' when {context.get('trigger', 'similar context is detected')}"
        )
        
        # Store as semantic memory
        self.store(
            content=f"Pattern learned: {pattern}\nContext: {json.dumps(context)}\nExamples: {examples}",
            memory_type=MemoryType.SEMANTIC,
            context=context,
            tags=["learned-pattern", "insight"],
            importance=0.8
        )
        
        return insight
    
    def get_context(self, task: str, limit: int = 5) -> str:
        """Get relevant context for a task"""
        memories = self.recall(task, limit=limit)
        
        if not memories:
            return ""
        
        context_parts = ["Relevant past experiences:\n"]
        for mem in memories:
            context_parts.append(f"- [{mem.memory_type.value}] {mem.content[:200]}...")
        
        return "\n".join(context_parts)
    
    def remember_procedure(
        self,
        name: str,
        steps: List[str],
        context: Dict[str, Any]
    ):
        """Store a learned procedure"""
        content = f"Procedure: {name}\nSteps:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
        
        self.store(
            content=content,
            memory_type=MemoryType.PROCEDURAL,
            context=context,
            tags=["procedure", name.lower().replace(" ", "-")],
            importance=0.9
        )
    
    def get_procedure(self, name: str) -> Optional[MemoryEntry]:
        """Retrieve a stored procedure"""
        memories = self.recall(f"procedure {name}", memory_type=MemoryType.PROCEDURAL)
        return memories[0] if memories else None
    
    def _cleanup(self):
        """Remove old entries beyond retention policy"""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        for mem_type, entries in self._memory_cache.items():
            initial_count = len(entries)
            
            # Remove old entries (keep high importance ones)
            filtered = [
                e for e in entries
                if datetime.fromisoformat(e.created_at) > cutoff or e.importance > 0.8
            ]
            
            # Also limit total entries
            if len(filtered) > self.max_entries:
                # Sort by importance and recency, keep top entries
                filtered.sort(key=lambda e: (e.importance, datetime.fromisoformat(e.accessed_at)), reverse=True)
                filtered = filtered[:self.max_entries]
            
            self._memory_cache[mem_type] = filtered
            
            if len(filtered) != initial_count:
                self._save_file(mem_type)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        stats = {}
        total = 0
        
        for mem_type, entries in self._memory_cache.items():
            stats[mem_type.value] = len(entries)
            total += len(entries)
        
        stats["total"] = total
        stats["storage_path"] = str(self.storage_path)
        
        return stats
    
    def forget(self, entry_id: str) -> bool:
        """Forget a specific memory entry"""
        for mem_type, entries in self._memory_cache.items():
            for i, entry in enumerate(entries):
                if entry.id == entry_id:
                    entries.pop(i)
                    self._save_file(mem_type)
                    return True
        return False


# Global vault instance
_vault: Optional[SwarmVault] = None

def get_vault() -> SwarmVault:
    """Get or create the global vault instance"""
    global _vault
    if _vault is None:
        _vault = SwarmVault()
    return _vault

def remember(content: str, **kwargs) -> MemoryEntry:
    """Store a memory"""
    return get_vault().store(content, **kwargs)

def recall(query: str, **kwargs) -> List[MemoryEntry]:
    """Recall memories"""
    return get_vault().recall(query, **kwargs)

def get_context(task: str, **kwargs) -> str:
    """Get context for a task"""
    return get_vault().get_context(task, **kwargs)

# Skill wrapper for invoke_skill
class AgentMemorySkill:
    """Skill wrapper for swarmvault"""
    
    NAME = "agent_memory"
    DESCRIPTION = "Persistent memory system for learning from experience"
    TRIGGERS = ["remember", "recall", "learn", "memory", "context"]
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main skill entry point"""
        vault = get_vault()
        
        if "stats" in task.lower() or "info" in task.lower():
            return {"skill": cls.NAME, "stats": vault.get_stats()}
        
        if "learn" in task.lower() or "pattern" in task.lower():
            # Extract pattern and learn
            insight = vault.learn_pattern(
                pattern=task,
                context=context or {},
                examples=context.get("examples", []) if context else []
            )
            return {"skill": cls.NAME, "insight": asdict(insight)}
        
        if "procedure" in task.lower():
            proc = vault.get_procedure(task)
            if proc:
                return {"skill": cls.NAME, "procedure": proc.content}
        
        # Default: recall relevant memories
        memories = vault.recall(task, limit=5)
        return {
            "skill": cls.NAME,
            "task": task,
            "memories": [{"content": m.content, "type": m.memory_type.value, "importance": m.importance} for m in memories],
            "context": vault.get_context(task),
            "stats": vault.get_stats()
        }
