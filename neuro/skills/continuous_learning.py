# Instinct-Based Learning System
# Inspired by ECC's continuous-learning-v2
# Adds confidence scoring, pattern extraction, and skill evolution to Neuro

import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import re

@dataclass
class Instinct:
    """
    A learned pattern with confidence scoring.
    Inspired by ECC's instinct system.
    """
    id: str
    pattern: str  # The learned pattern/regex
    context: str  # When this pattern applies
    action: str  # What to do when matched
    evidence: List[str]  # Example instances
    confidence: float = 0.5  # 0.0 to 1.0
    uses: int = 0
    successes: int = 0
    failures: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.uses == 0:
            return 0.5
        return self.successes / self.uses
    
    def update_confidence(self, success: bool):
        """Update confidence based on outcome."""
        self.uses += 1
        if success:
            self.successes += 1
        else:
            self.failures += 1
        
        # Bayesian update: confidence = successes / (uses + 2)
        self.confidence = self.successes / (self.uses + 2)
        self.updated_at = time.time()


@dataclass 
class SkillEvolution:
    """
    A skill evolved from related instincts.
    """
    id: str
    name: str
    description: str
    instincts: List[str]  # Instinct IDs that formed this skill
    content: str  # SKILL.md content
    confidence: float = 0.7
    created_at: float = field(default_factory=time.time)
    file_path: Optional[Path] = None


class InstinctStore:
    """
    Persistent storage for instincts.
    Evolved from your basic SQLite task_store.
    """
    
    def __init__(self, storage_dir: str = "~/.neuro/instincts"):
        self.storage_dir = Path(os.path.expanduser(storage_dir))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.instincts: Dict[str, Instinct] = {}
        self.skills: Dict[str, SkillEvolution] = {}
        self._load_all()
    
    def _load_all(self):
        """Load all instincts and skills from disk."""
        # Load instincts
        instincts_file = self.storage_dir / "instincts.json"
        if instincts_file.exists():
            with open(instincts_file) as f:
                data = json.load(f)
                for inst_data in data.get("instincts", []):
                    inst = Instinct(**inst_data)
                    self.instincts[inst.id] = inst
        
        # Load evolved skills
        skills_dir = self.storage_dir / "skills"
        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.json"):
                with open(skill_file) as f:
                    skill_data = json.load(f)
                    skill = SkillEvolution(**skill_data)
                    self.skills[skill.id] = skill
    
    def _save_all(self):
        """Save all instincts to disk."""
        instincts_file = self.storage_dir / "instincts.json"
        with open(instincts_file, "w") as f:
            json.dump({
                "instincts": [vars(i) for i in self.instincts.values()]
            }, f, indent=2)
        
        # Save evolved skills
        skills_dir = self.storage_dir / "skills"
        skills_dir.mkdir(exist_ok=True)
        for skill in self.skills.values():
            skill_file = skills_dir / f"{skill.id}.json"
            with open(skill_file, "w") as f:
                json.dump(vars(skill), f, indent=2)
    
    def add_instinct(self, pattern: str, context: str, action: str, 
                     evidence: List[str] = None, tags: List[str] = None) -> Instinct:
        """Add a new instinct."""
        inst_id = f"instinct_{len(self.instincts) + 1}_{int(time.time())}"
        instinct = Instinct(
            id=inst_id,
            pattern=pattern,
            context=context,
            action=action,
            evidence=evidence or [],
            tags=tags or []
        )
        self.instincts[inst_id] = instinct
        self._save_all()
        return instinct
    
    def match_instincts(self, text: str, threshold: float = 0.6) -> List[Tuple[Instinct, float]]:
        """
        Match text against all instincts.
        Returns instincts with match score > threshold.
        """
        matches = []
        for instinct in self.instincts.values():
            # Try regex match
            try:
                if re.search(instinct.pattern, text, re.IGNORECASE):
                    matches.append((instinct, instinct.confidence))
            except re.error:
                # Fall back to substring match
                if instinct.pattern.lower() in text.lower():
                    matches.append((instinct, instinct.confidence * 0.8))
        
        # Sort by confidence
        matches.sort(key=lambda x: x[1], reverse=True)
        return [(m, score) for m, score in matches if score >= threshold]
    
    def record_outcome(self, instinct_id: str, success: bool):
        """Record success/failure for an instinct."""
        if instinct_id in self.instincts:
            self.instincts[instinct_id].update_confidence(success)
            self._save_all()
    
    def evolve_skills(self, cluster_threshold: float = 0.8) -> List[SkillEvolution]:
        """
        Cluster related instincts into skills.
        Uses tag similarity and pattern overlap.
        """
        # Group by shared tags
        tag_groups: Dict[str, List[Instinct]] = defaultdict(list)
        for instinct in self.instincts.values():
            for tag in instinct.tags:
                tag_groups[tag].append(instinct)
        
        # Create skills from high-confidence instinct groups
        evolved = []
        for tag, instincts in tag_groups.items():
            if len(instincts) >= 2:  # Need at least 2 instincts
                avg_confidence = sum(i.confidence for i in instincts) / len(instincts)
                if avg_confidence >= cluster_threshold:
                    skill = self._create_skill_from_instincts(tag, instincts)
                    self.skills[skill.id] = skill
                    evolved.append(skill)
        
        self._save_all()
        return evolved
    
    def _create_skill_from_instincts(self, tag: str, instincts: List[Instinct]) -> SkillEvolution:
        """Create a skill from a group of instincts."""
        skill_id = f"skill_{tag}_{int(time.time())}"
        
        # Generate SKILL.md content
        content = f"""---
name: {tag}-evolved
description: Auto-evolved skill from {len(instincts)} instincts
triggers:
  - {tag}
---

# {tag.title()} Skill (Evolved)

Auto-generated from instinct patterns.

## Origin
Created from {len(instincts)} instincts with average confidence {sum(i.confidence for i in instincts)/len(instincts):.2f}

## Patterns

"""
        for inst in instincts:
            content += f"""### {inst.context}
- Pattern: `{inst.pattern}`
- Action: {inst.action}
- Confidence: {inst.confidence:.2f}
- Uses: {inst.uses}, Successes: {inst.successes}

"""
        
        skill = SkillEvolution(
            id=skill_id,
            name=tag,
            description=f"Auto-evolved skill for {tag}",
            instincts=[i.id for i in instincts],
            content=content,
            confidence=sum(i.confidence for i in instincts) / len(instincts)
        )
        
        # Save skill file
        skills_dir = self.storage_dir / "skills"
        skills_dir.mkdir(exist_ok=True)
        skill.file_path = skills_dir / f"{skill_id}.md"
        skill.file_path.write_text(content)
        
        return skill
    
    def export_instincts(self) -> Dict[str, Any]:
        """Export instincts for sharing."""
        return {
            "exported_at": time.time(),
            "count": len(self.instincts),
            "instincts": [vars(i) for i in self.instincts.values()],
            "skills": [vars(s) for s in self.skills.values()]
        }
    
    def import_instincts(self, data: Dict[str, Any]):
        """Import instincts from external source."""
        for inst_data in data.get("instincts", []):
            if inst_data["id"] not in self.instincts:
                instinct = Instinct(**inst_data)
                self.instincts[instinct.id] = instinct
        self._save_all()


class ContinuousLearning:
    """
    Main learning system that observes Neuro's execution
    and extracts patterns for future use.
    Inspired by ECC's continuous-learning-v2.
    """
    
    def __init__(self, store: Optional[InstinctStore] = None):
        self.store = store or InstinctStore()
        self.session_history: List[Dict] = []
    
    def record_session(self, task: str, actions: List[Dict], outcome: str):
        """
        Record a complete session for pattern extraction.
        
        Args:
            task: The original task description
            actions: List of actions taken [{action, result, success}]
            outcome: "success", "partial", "failure"
        """
        session = {
            "task": task,
            "actions": actions,
            "outcome": outcome,
            "timestamp": time.time()
        }
        self.session_history.append(session)
        
        # Extract patterns from successful sessions
        if outcome == "success":
            self._extract_patterns(task, actions)
    
    def _extract_patterns(self, task: str, actions: List[Dict]):
        """Extract patterns from successful action sequences."""
        # Extract common action patterns
        action_types = [a.get("action", "") for a in actions]
        
        # Look for repeated patterns
        for i, action in enumerate(actions):
            if action.get("success") and action.get("result"):
                result_str = str(action["result"])
                
                # Extract patterns from code generation
                if "def " in result_str or "class " in result_str:
                    # Extract function/class patterns
                    pattern = self._extract_code_pattern(result_str)
                    if pattern:
                        self.store.add_instinct(
                            pattern=pattern["regex"],
                            context=f"Python code generation for {task[:50]}",
                            action=pattern["action"],
                            evidence=[result_str[:200]],
                            tags=["python", "code-generation", action.get("action", "unknown")]
                        )
                
                # Extract regex patterns from text processing
                if "regex" in action.get("action", "").lower():
                    pattern = self._extract_regex_pattern(result_str)
                    if pattern:
                        self.store.add_instinct(
                            pattern=pattern,
                            context=f"Text pattern for {task[:50]}",
                            action="text processing",
                            evidence=[result_str[:200]],
                            tags=["regex", "text-processing"]
                        )
    
    def _extract_code_pattern(self, code: str) -> Optional[Dict]:
        """Extract reusable patterns from code."""
        patterns = []
        
        # Function definition pattern
        func_match = re.search(r'def (\w+)\([^)]*\):', code)
        if func_match:
            return {
                "regex": rf'def\s+\w+\([^)]*\):[^\n]*\n(?:[ \t]+[^\n]*\n)*',
                "action": f"Define {func_match.group(1)} function"
            }
        
        # Class pattern
        class_match = re.search(r'class (\w+)(?:\([^)]*\))?:', code)
        if class_match:
            return {
                "regex": rf'class\s+\w+(?:\([^)]*\))?:[^\n]*\n(?:[ \t]+[^\n]*\n)*',
                "action": f"Create {class_match.group(1)} class"
            }
        
        # Import pattern
        import_match = re.search(r'(?:from|import) (\w+)', code)
        if import_match:
            return {
                "regex": r'(?:from|import)\s+\w+',
                "action": f"Import {import_match.group(1)}"
            }
        
        return None
    
    def _extract_regex_pattern(self, text: str) -> Optional[str]:
        """Extract regex patterns from text."""
        # Look for common patterns
        email = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
        if email:
            return r'[\w.-]+@[\w.-]+\.\w+'
        
        url = re.search(r'https?://[\w.-]+(?:/[\w./-]*)?', text)
        if url:
            return r'https?://[\w.-]+(?:/[\w./-]*)?'
        
        return None
    
    def get_context_for_task(self, task: str) -> str:
        """
        Get relevant context for a new task based on learned instincts.
        """
        matches = self.store.match_instincts(task, threshold=0.5)
        
        context_parts = []
        for instinct, confidence in matches[:5]:  # Top 5 matches
            context_parts.append(f"[{confidence:.0%} confidence] {instinct.action}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get current learning system status."""
        return {
            "total_instincts": len(self.store.instincts),
            "total_skills": len(self.store.skills),
            "avg_confidence": sum(i.confidence for i in self.store.instincts.values()) / max(1, len(self.store.instincts)),
            "recent_sessions": len(self.session_history),
            "high_confidence_instincts": len([i for i in self.store.instincts.values() if i.confidence >= 0.8])
        }


# Global instance
_learning_system: Optional[ContinuousLearning] = None

def get_learning_system() -> ContinuousLearning:
    """Get or create the global learning system."""
    global _learning_system
    if _learning_system is None:
        _learning_system = ContinuousLearning()
    return _learning_system


# SKILL.md content
SKILL_MD = """
---
name: continuous-learning-v2
description: Instinct-based learning with confidence scoring and skill evolution
triggers:
  - learn
  - pattern
  - instinct
  - evolve
  - extract
---

# Continuous Learning v2 Skill

Instinct-based learning system inspired by ECC's continuous-learning-v2.
Enhances your existing SQLite memory with:

## Features

### 1. Instincts
Learned patterns with confidence scoring:
- id: Unique identifier
- pattern: Regex or text pattern
- context: When it applies
- action: What to do
- confidence: 0.0 to 1.0 (Bayesian updated)

### 2. Skill Evolution
Cluster related instincts into reusable skills:
```
/evolve  # Cluster instincts into skills
```

### 3. Session Recording
Record tasks and extract patterns:
```python
from neuro.skills.continuous_learning import get_learning_system

learning = get_learning_system()
learning.record_session(
    task="Fix auth bug",
    actions=[{"action": "grep", "result": "...", "success": True}],
    outcome="success"
)
```

### 4. Context Retrieval
Get relevant learned patterns for new tasks:
```python
context = learning.get_context_for_task("Fix login issue")
# Returns: "[90% confidence] Use token validation"
```

## Usage

```python
# Record learning
learning.record_session(task, actions, outcome)

# Get context for new task
context = learning.get_context_for_task("New task description")

# Check status
status = learning.get_status()
# {"total_instincts": 42, "avg_confidence": 0.75, ...}

# Export/Import instincts
data = learning.store.export_instincts()
learning.store.import_instincts(data)
```
"""