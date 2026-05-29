# Real-Time Agent State & Streaming System - Manus Level
# Live progress tracking, thinking visualization, action streaming
# Features: real-time updates, thinking process display, checkpoint notifications

import json
import time
import asyncio
import threading
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
from collections import deque
from neuro.skills.skill_middleware import register_skill


class AgentState(Enum):
    """Agent execution states."""
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionType(Enum):
    """Types of agent actions for visualization."""
    READ = "read"
    WRITE = "write"
    EDIT = "edit"
    EXECUTE = "execute"
    SEARCH = "search"
    NAVIGATE = "navigate"
    THINK = "think"
    PLAN = "plan"
    REVIEW = "review"
    VALIDATE = "validate"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"


@dataclass
class AgentAction:
    """Single agent action for streaming."""
    action_id: str
    action_type: ActionType
    timestamp: str
    duration_ms: float = 0
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'action_id': self.action_id,
            'action_type': self.action_type.value,
            'timestamp': self.timestamp,
            'duration_ms': self.duration_ms,
            'description': self.description,
            'details': self.details,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'result': self.result,
            'error': self.error
        }


@dataclass
class ThinkingBlock:
    """A thinking block (similar to Sonnet/thinking tokens)."""
    block_id: str
    content: str
    start_time: str
    end_time: Optional[str] = None
    reflections: List[str] = field(default_factory=list)
    iterations: int = 1
    
    def to_dict(self) -> Dict:
        return {
            'block_id': self.block_id,
            'content': self.content,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'reflections': self.reflections,
            'iterations': self.iterations
        }


@dataclass
class AgentCheckpoint:
    """Checkpoint for human-in-the-loop."""
    checkpoint_id: str
    name: str
    description: str
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)
    requires_approval: bool = True
    approved: Optional[bool] = None
    created_at: str = ""
    approved_at: Optional[str] = None


@dataclass
class AgentMetrics:
    """Performance metrics for the agent session."""
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    total_thinking_time_ms: float = 0
    total_execution_time_ms: float = 0
    tokens_used: int = 0
    files_modified: int = 0
    commands_executed: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_actions == 0:
            return 0.0
        return self.successful_actions / self.total_actions * 100


class StreamEvent:
    """Event for the streaming system."""
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp
        }


class StreamSubscriber:
    """Subscriber for real-time events."""
    
    def __init__(self, name: str, callback: Callable[[StreamEvent], None],
                 filters: List[str] = None):
        self.name = name
        self.callback = callback
        self.filters = filters or []
        self.event_count = 0
    
    def shouldReceive(self, event: StreamEvent) -> bool:
        """Check if subscriber should receive this event."""
        if not self.filters:
            return True
        return event.event_type in self.filters
    
    def notify(self, event: StreamEvent):
        """Notify subscriber of event."""
        self.event_count += 1
        try:
            self.callback(event)
        except Exception:
            pass


@register_skill("agent_state_manager", "Real-time agent state, streaming, and progress tracking", category="agent_core")
class AgentStateManager:
    """
    Real-time agent state and streaming system.
    Similar to Manus's progress tracking and Kimi's thinking visualization.
    
    Features:
    - Live action streaming
    - Thinking process visualization
    - Checkpoint notifications for human-in-the-loop
    - Performance metrics
    - Screenshot capture hooks
    - Complete session replay
    
    Usage:
        from neuro.skills.agent_state_manager import AgentStateManager
        
        state = AgentStateManager()
        
        # Track actions
        with state.action("execute", description="Running tests"):
            result = run_tests()
        
        # Thinking blocks
        thought = state.start_thinking("Planning architecture...")
        # ... think ...
        state.end_thinking(thought, reflections=["Good approach", "Consider edge cases"])
        
        # Checkpoints
        state.create_checkpoint("Approve changes?", options=["Yes", "No", "Modify"])
        
        # Stream to subscribers
        state.subscribe("ui", my_callback, filters=["action", "thinking"])
    """
    
    MAX_HISTORY = 10000  # Max actions to keep in memory
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.state = AgentState.IDLE
        self.start_time = datetime.now().isoformat()
        self.actions: deque = deque(maxlen=self.MAX_HISTORY)
        self.thinking_blocks: List[ThinkingBlock] = []
        self.checkpoints: List[AgentCheckpoint] = []
        self.metrics = AgentMetrics()
        self.subscribers: List[StreamSubscriber] = []
        self.current_action: Optional[AgentAction] = None
        self.action_stack: List[str] = []  # For nested actions
        self.context: Dict[str, Any] = {}
        self.streaming_enabled = True
        self._lock = threading.RLock()
        self._pending_checkpoints: Dict[str, threading.Event] = {}
        
        # File to save session
        self.session_file = Path(f"~/.neuro_sessions/{self.session_id}.json").expanduser()
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
    
    @property
    def session_id_short(self) -> str:
        return self.session_id[:8]
    
    def subscribe(self, name: str, callback: Callable[[StreamEvent], None],
                 filters: List[str] = None) -> str:
        """Subscribe to stream events."""
        subscriber = StreamSubscriber(name, callback, filters)
        self.subscribers.append(subscriber)
        return name
    
    def unsubscribe(self, name: str):
        """Unsubscribe from stream events."""
        self.subscribers = [s for s in self.subscribers if s.name != name]
    
    def _emit(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all subscribers."""
        if not self.streaming_enabled:
            return
        
        event = StreamEvent(event_type, data)
        
        with self._lock:
            for subscriber in self.subscribers:
                if subscriber.shouldReceive(event):
                    subscriber.notify(event)
    
    def set_state(self, new_state: AgentState, context: Dict[str, Any] = None):
        """Change agent state."""
        self.state = new_state
        self.context.update(context or {})
        self._emit('state_change', {
            'old_state': self.state.value,
            'new_state': new_state.value,
            'context': context
        })
    
    def action(self, action_type: ActionType, description: str = "",
               file_path: str = None, line_number: int = None,
               auto_track: bool = True) -> 'ActionContext':
        """
        Context manager for tracking an action.
        
        Usage:
            with state.action(ActionType.EXECUTE, "Running tests"):
                result = subprocess.run(...)
        """
        return ActionContext(self, action_type, description, file_path, line_number, auto_track)
    
    def start_action(self, action_type: ActionType, description: str = "",
                    file_path: str = None, line_number: int = None) -> AgentAction:
        """Start tracking an action."""
        action = AgentAction(
            action_id=str(uuid.uuid4())[:8],
            action_type=action_type,
            timestamp=datetime.now().isoformat(),
            description=description,
            file_path=file_path,
            line_number=line_number
        )
        self.current_action = action
        self.action_stack.append(action.action_id)
        self._emit('action_start', action.to_dict())
        return action
    
    def end_action(self, action: AgentAction, result: str = None, 
                  error: str = None) -> AgentAction:
        """End tracking an action."""
        end_time = datetime.now()
        if action.timestamp:
            start = datetime.fromisoformat(action.timestamp)
            action.duration_ms = (end_time - start).total_seconds() * 1000
        
        action.result = result
        action.error = error
        
        self.actions.append(action)
        self.action_stack.pop()
        
        if action.action_type == ActionType.ERROR:
            self.metrics.failed_actions += 1
            self.set_state(AgentState.FAILED)
        elif action.action_type == ActionType.SUCCESS:
            self.metrics.successful_actions += 1
        elif action.action_type in [ActionType.EXECUTE, ActionType.WRITE, ActionType.EDIT]:
            self.metrics.commands_executed += 1
        
        self.metrics.total_actions += 1
        
        self._emit('action_end', action.to_dict())
        self.current_action = None
        return action
    
    def log_action(self, action_type: ActionType, description: str, 
                   details: Dict[str, Any] = None) -> AgentAction:
        """Log a complete action (start and end together)."""
        action = AgentAction(
            action_id=str(uuid.uuid4())[:8],
            action_type=action_type,
            timestamp=datetime.now().isoformat(),
            description=description,
            details=details or {}
        )
        action.duration_ms = 0
        self.actions.append(action)
        self.metrics.total_actions += 1
        self._emit('action_log', action.to_dict())
        return action
    
    def start_thinking(self, content: str) -> ThinkingBlock:
        """Start a thinking block."""
        block = ThinkingBlock(
            block_id=str(uuid.uuid4())[:8],
            content=content,
            start_time=datetime.now().isoformat()
        )
        self.thinking_blocks.append(block)
        self.state = AgentState.THINKING
        self._emit('thinking_start', block.to_dict())
        return block
    
    def end_thinking(self, block: ThinkingBlock, 
                    reflections: List[str] = None) -> ThinkingBlock:
        """End a thinking block."""
        block.end_time = datetime.now().isoformat()
        block.reflections = reflections or []
        
        if reflections:
            block.iterations = len(reflections)
        
        self._emit('thinking_end', block.to_dict())
        
        if self.state == AgentState.THINKING:
            self.state = AgentState.EXECUTING
        
        return block
    
    def add_reflection(self, block: ThinkingBlock, reflection: str):
        """Add a reflection to a thinking block."""
        block.reflections.append(reflection)
        block.iterations += 1
        self._emit('thinking_reflection', {
            'block_id': block.block_id,
            'reflection': reflection,
            'total_reflections': len(block.reflections)
        })
    
    def create_checkpoint(self, name: str, description: str,
                         state_snapshot: Dict[str, Any] = None,
                         options: List[str] = None,
                         requires_approval: bool = True) -> AgentCheckpoint:
        """Create a checkpoint for human approval."""
        checkpoint = AgentCheckpoint(
            checkpoint_id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            state_snapshot=state_snapshot or self.get_snapshot(),
            options=options or ["Continue", "Cancel"],
            requires_approval=requires_approval,
            created_at=datetime.now().isoformat()
        )
        self.checkpoints.append(checkpoint)
        self.state = AgentState.WAITING
        self._emit('checkpoint_created', {
            'checkpoint_id': checkpoint.checkpoint_id,
            'name': name,
            'description': description,
            'options': checkpoint.options
        })
        
        if requires_approval:
            event = threading.Event()
            self._pending_checkpoints[checkpoint.checkpoint_id] = event
        
        return checkpoint
    
    def approve_checkpoint(self, checkpoint_id: str, choice: str) -> bool:
        """Approve/reject a checkpoint."""
        checkpoint = None
        for cp in self.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                checkpoint = cp
                break
        
        if not checkpoint:
            return False
        
        checkpoint.approved = choice in ["Continue", "Yes", "Approve", "OK"]
        checkpoint.approved_at = datetime.now().isoformat()
        
        self._emit('checkpoint_response', {
            'checkpoint_id': checkpoint_id,
            'approved': checkpoint.approved,
            'choice': choice
        })
        
        if checkpoint.checkpoint_id in self._pending_checkpoints:
            self._pending_checkpoints[checkpoint.checkpoint_id].set()
            del self._pending_checkpoints[checkpoint.checkpoint_id]
        
        if checkpoint.approved:
            self.state = AgentState.EXECUTING
        
        return checkpoint.approved
    
    def wait_for_checkpoint(self, checkpoint_id: str, timeout: float = None) -> bool:
        """Wait for checkpoint approval."""
        if checkpoint_id not in self._pending_checkpoints:
            return True
        
        event = self._pending_checkpoints[checkpoint_id]
        result = event.wait(timeout=timeout)
        return result
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get current state snapshot."""
        return {
            'session_id': self.session_id,
            'state': self.state.value,
            'metrics': {
                'total_actions': self.metrics.total_actions,
                'success_rate': self.metrics.success_rate,
                'commands_executed': self.metrics.commands_executed
            },
            'current_action': self.current_action.to_dict() if self.current_action else None,
            'pending_checkpoints': len(self._pending_checkpoints)
        }
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent action history."""
        return [a.to_dict() for a in list(self.actions)[-limit:]]
    
    def get_thinking_summary(self) -> List[Dict]:
        """Get summary of all thinking blocks."""
        return [b.to_dict() for b in self.thinking_blocks]
    
    def save_session(self, path: Path = None) -> str:
        """Save session to file."""
        path = path or self.session_file
        
        data = {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'end_time': datetime.now().isoformat(),
            'state': self.state.value,
            'actions': [a.to_dict() for a in self.actions],
            'thinking_blocks': [b.to_dict() for b in self.thinking_blocks],
            'checkpoints': [
                {
                    'checkpoint_id': c.checkpoint_id,
                    'name': c.name,
                    'approved': c.approved,
                    'approved_at': c.approved_at
                }
                for c in self.checkpoints
            ],
            'metrics': {
                'total_actions': self.metrics.total_actions,
                'successful_actions': self.metrics.successful_actions,
                'failed_actions': self.metrics.failed_actions,
                'total_thinking_time_ms': self.metrics.total_thinking_time_ms,
                'commands_executed': self.metrics.commands_executed
            }
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(path)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate session report."""
        duration_ms = 0
        if self.start_time:
            start = datetime.fromisoformat(self.start_time)
            duration_ms = (datetime.now() - start).total_seconds() * 1000
        
        return {
            'session_id': self.session_id,
            'duration_ms': duration_ms,
            'total_actions': self.metrics.total_actions,
            'success_rate': f"{self.metrics.success_rate:.1f}%",
            'thinking_blocks': len(self.thinking_blocks),
            'checkpoints_passed': sum(1 for c in self.checkpoints if c.approved),
            'checkpoints_failed': sum(1 for c in self.checkpoints if c.approved is False),
            'files_modified': self.metrics.files_modified,
            'commands_executed': self.metrics.commands_executed,
            'state': self.state.value
        }


class ActionContext:
    """Context manager for actions."""
    
    def __init__(self, manager: AgentStateManager, action_type: ActionType,
                 description: str, file_path: str, line_number: int,
                 auto_track: bool):
        self.manager = manager
        self.action_type = action_type
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.auto_track = auto_track
        self.action: Optional[AgentAction] = None
        self.result = None
        self.error = None
    
    def __enter__(self):
        if self.auto_track:
            self.action = self.manager.start_action(
                self.action_type, self.description,
                self.file_path, self.line_number
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.action:
            self.manager.end_action(
                self.action,
                result=str(self.result) if self.result else None,
                error=str(exc_val) if exc_val else None
            )
        
        if exc_type is not None:
            self.manager.log_action(
                ActionType.ERROR,
                f"Error in {self.description}: {exc_val}",
                {'exception': exc_type.__name__}
            )
        
        return False  # Don't suppress exceptions


class StreamWebSocket:
    """WebSocket adapter for streaming to browsers."""
    
    def __init__(self, ws_handler):
        self.ws = ws_handler
        self.subscriptions: List[str] = []
    
    async def broadcast(self, event: StreamEvent):
        """Broadcast event via WebSocket."""
        if self.ws.connected:
            await self.ws.send(json.dumps(event.to_dict()))


def create_state_manager() -> AgentStateManager:
    """Factory function to create a state manager."""
    return AgentStateManager()


# Global state manager for the current session
_current_manager: Optional[AgentStateManager] = None


def get_current_state() -> AgentStateManager:
    """Get the current global state manager."""
    global _current_manager
    if _current_manager is None:
        _current_manager = AgentStateManager()
    return _current_manager


def set_current_state(manager: AgentStateManager):
    """Set the current global state manager."""
    global _current_manager
    _current_manager = manager


# SKILL.md content
SKILL_MD = """
---
name: agent-state-manager
description: Real-time agent state tracking, streaming, and progress visualization
triggers:
  - state
  - stream
  - progress
  - track
  - thinking
  - checkpoint
---

# Real-Time Agent State & Streaming System

Live agent state tracking and progress visualization system.
Similar to Manus's progress tracking and Kimi's thinking process.

## Features

### 1. Action Streaming
Track all agent actions in real-time:
- Read/write/edit operations
- Command execution
- Search and navigation
- Think and plan activities

### 2. Thinking Process
Visualize agent thinking with named blocks:
- Track reasoning iterations
- Add reflections
- Show depth of analysis

### 3. Checkpoints
Human-in-the-loop checkpoints:
- Ask for approval before critical actions
- Present options to user
- Wait for response

### 4. Metrics
Track performance:
- Success rate
- Action counts
- Timing information

## Usage

```python
from neuro.skills.agent_state_manager import (
    AgentStateManager, AgentState, ActionType, get_current_state
)

# Get global state
state = get_current_state()

# Track actions
with state.action(ActionType.EXECUTE, "Running tests"):
    result = subprocess.run(["pytest"], capture_output=True)

# Thinking blocks
thought = state.start_thinking("Analyzing best approach...")
state.add_reflection(thought, "Consider edge cases")
state.end_thinking(thought, reflections=["Good approach"])

# Checkpoints
checkpoint = state.create_checkpoint(
    "Confirm deletion",
    "Delete all temp files?",
    options=["Yes", "No"]
)
state.wait_for_checkpoint(checkpoint.checkpoint_id)

# Subscribe to events
state.subscribe("ui", my_callback, filters=["action", "checkpoint"])

# Generate report
report = state.generate_report()
```
"""
