# Python Patterns Skill
# Language-specific best practices for Python code generation
# Inspired by ECC's python-patterns

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class PythonPattern:
    name: str
    description: str
    template: str
    use_cases: List[str]
    example: Optional[str] = None

class PythonPatternsSkill:
    """
    Python idioms and best practices for Neuro agent.
    Helps generate idiomatic Python code.
    
    Usage:
        from neuro.skills.python_patterns import PythonPatternsSkill
        
        patterns = PythonPatternsSkill()
        pattern = patterns.get_pattern("context_manager")
        code = pattern.template.format(resource="file")
    """
    
    PATTERNS = {
        # Creational Patterns
        "singleton": PythonPattern(
            name="singleton",
            description="Ensure a class has only one instance",
            template="""class {class_name}:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance""",
            use_cases=["database connection", "config singleton", "logger"],
        ),
        "factory": PythonPattern(
            name="factory",
            description="Create objects without specifying exact class",
            template="""def create_{object_type}({params}):
    \"\"\"Factory function for {object_type} creation.\"\"\"
    return {class_name}({params})""",
            use_cases=["object creation", "dependency injection"],
        ),
        
        # Structural Patterns
        "context_manager": PythonPattern(
            name="context_manager",
            description="Resource management with __enter__/__exit__",
            template="""class {class_name}:
    def __enter__(self):
        # Acquire resource
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release resource
        return False  # Don't suppress exceptions""",
            use_cases=["file handling", "database transactions", "locks"],
        ),
        "decorator": PythonPattern(
            name="decorator",
            description="Add behavior to functions dynamically",
            template="""def {decorator_name}(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Pre-processing
        result = func(*args, **kwargs)
        # Post-processing
        return result
    return wrapper""",
            use_cases=["logging", "timing", "caching", "authorization"],
        ),
        
        # Behavioral Patterns
        "observer": PythonPattern(
            name="observer",
            description="Notify observers of state changes",
            template="""class Observable:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        self._observers.append(observer)
    
    def notify(self, *args, **kwargs):
        for observer in self._observers:
            observer.update(*args, **kwargs)""",
            use_cases=["event handling", "MVC", "data binding"],
        ),
        "strategy": PythonPattern(
            name="strategy",
            description="Select algorithm at runtime",
            template="""class Strategy:
    def execute(self, data):
        raise NotImplementedError

class ConcreteStrategy(Strategy):
    def execute(self, data):
        # Specific algorithm
        return result""",
            use_cases=["sorting", "validation", "compression"],
        ),
        
        # Async Patterns
        "async_context": PythonPattern(
            name="async_context",
            description="Async resource management",
            template="""async def {function_name}({params}):
    async with {context_manager}({args}) as resource:
        # Async operations
        return result""",
            use_cases=["database", "HTTP clients", "file I/O"],
        ),
        "async_batch": PythonPattern(
            name="async_batch",
            description="Batch process with asyncio.gather",
            template="""async def process_batch(items: List, batch_size: int = 10):
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(*[
            process_item(item) for item in batch
        ])
        results.extend(batch_results)
    return results""",
            use_cases=["API calls", "database inserts", "file processing"],
        ),
        
        # Data Processing
        "pipeline": PythonPattern(
            name="pipeline",
            description="Chain data transformations",
            template="""def pipeline(*functions):
    def execute(data):
        result = data
        for func in functions:
            result = func(result)
        return result
    return execute

# Usage:
# transform = pipeline(clean, validate, normalize)""",
            use_cases=["data cleaning", "transformation chains"],
        ),
        "lazy_evaluation": PythonPattern(
            name="lazy_evaluation",
            description="Defer computation until needed",
            template="""from functools import cached_property

class {class_name}:
    @cached_property
    def expensive_value(self):
        # Computed only once, on first access
        return self._compute_expensive_value()""",
            use_cases=["expensive computations", "heavy resources"],
        ),
    }
    
    def get_pattern(self, name: str) -> Optional[PythonPattern]:
        """Get a pattern by name."""
        return self.PATTERNS.get(name)
    
    def list_patterns(self) -> List[Dict[str, str]]:
        """List all available patterns."""
        return [
            {"name": p.name, "description": p.description, "use_cases": p.use_cases}
            for p in self.PATTERNS.values()
        ]
    
    def suggest_pattern(self, context: str) -> Optional[PythonPattern]:
        """Suggest pattern based on context."""
        context_lower = context.lower()
        
        # Keyword mapping
        keywords = {
            "singleton": ["single", "one instance", "shared", "global"],
            "factory": ["create", "factory", "builder", "construct"],
            "context_manager": ["with", "resource", "cleanup", "finally"],
            "decorator": ["before", "after", "wrap", "intercept"],
            "observer": ["notify", "event", "listener", "subscribe"],
            "strategy": ["algorithm", " interchangeable", "select", "vary"],
            "async_context": ["await", "async with", "aiohttp"],
            "async_batch": ["batch", "bulk", "gather", "concurrent"],
            "pipeline": ["chain", "transform", "pipe", "flow"],
            "lazy_evaluation": ["lazy", "cached", "defer", "expensive"],
        }
        
        for pattern_name, kws in keywords.items():
            if any(kw in context_lower for kw in kws):
                return self.PATTERNS[pattern_name]
        
        return None


# SKILL.md content
SKILL_MD = """
---
name: python-patterns
description: Python idioms and best practices for idiomatic code generation
triggers:
  - python
  - pattern
  - idioms
  - django
  - async
  - pytest
---

# Python Patterns Skill

Provides idiomatic Python patterns for code generation, inspired by ECC's python-patterns.

## Available Patterns

### Creational
- **singleton**: Single instance pattern
- **factory**: Factory function pattern

### Structural  
- **context_manager**: Resource management with `with`
- **decorator**: Function wrapping

### Behavioral
- **observer**: Event notification
- **strategy**: Runtime algorithm selection

### Async
- **async_context**: Async resource management
- **async_batch**: Concurrent batch processing

### Data Processing
- **pipeline**: Transformation chains
- **lazy_evaluation**: Deferred computation

## Usage

```python
from neuro.skills.python_patterns import PythonPatternsSkill

patterns = PythonPatternsSkill()

# Get specific pattern
pattern = patterns.get_pattern("decorator")

# Auto-suggest pattern
suggested = patterns.suggest_pattern("I need to log function calls")

# List all patterns
all_patterns = patterns.list_patterns()
```

## Integration with Neuro

The pattern system integrates with your model routing:
- Python generation → Use PythonPatternsSkill
- Django → Add Django-specific patterns
- Async code → Use async_context/async_batch
"""