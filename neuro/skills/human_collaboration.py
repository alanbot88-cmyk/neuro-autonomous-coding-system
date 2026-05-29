"""
User Collaboration Features - Human-agent interaction loops
Competitor: Human-agent collaboration loops

Features:
- Real-time human feedback integration
- Interactive confirmation loops
- Human-in-the-loop checkpoints
- Suggestion and approval workflow
- Task delegation and handoff
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4
from neuro.skills.skill_middleware import register_skill


class FeedbackType(Enum):
    """Types of human feedback"""
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    CLARIFY = "clarify"
    CONFIRM = "confirm"
    CANCEL = "cancel"


@dataclass
class HumanFeedback:
    """Human feedback on agent action"""
    feedback_id: str
    timestamp: str
    feedback_type: FeedbackType
    comment: str
    suggested_modification: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Checkpoint:
    """Human-in-the-loop checkpoint"""
    checkpoint_id: str
    name: str
    description: str
    awaiting_response: bool = False
    response: Optional[HumanFeedback] = None
    approved: bool = False


@dataclass
class CollaborationSession:
    """Active collaboration session"""
    session_id: str
    task_description: str
    created_at: str
    checkpoints: List[Checkpoint] = field(default_factory=list)
    human_approved: bool = True  # Requires human approval
    feedback_history: List[HumanFeedback] = field(default_factory=list)
    status: str = "active"


class HumanAgentCollaboration:
    """
    User Collaboration Features - Human-agent interaction loops
    
    Features:
    - Real-time human feedback integration
    - Interactive confirmation loops
    - Human-in-the-loop checkpoints
    - Suggestion and approval workflow
    - Task delegation and handoff
    """
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.checkpoint_callbacks: List[Callable] = []
        self.approval_callbacks: List[Callable] = []
    
    def create_session(
        self,
        task_description: str,
        require_approval: bool = True,
        checkpoints: Optional[List[str]] = None
    ) -> CollaborationSession:
        """
        Create a new collaboration session.
        
        Args:
            task_description: What the agent is trying to accomplish
            require_approval: Whether human approval is required
            checkpoints: List of checkpoint names
        
        Returns:
            CollaborationSession object
        """
        session_id = str(uuid4())[:8]
        
        checkpoint_list = []
        if checkpoints:
            for i, cp_name in enumerate(checkpoints):
                checkpoint_list.append(Checkpoint(
                    checkpoint_id=f"cp_{i}_{session_id}",
                    name=cp_name,
                    description=f"Checkpoint: {cp_name}",
                    created_at=datetime.now().isoformat()
                ))
        
        session = CollaborationSession(
            session_id=session_id,
            task_description=task_description,
            checkpoints=checkpoint_list,
            human_approved=require_approval,
            created_at=datetime.now().isoformat()
        )
        
        self.sessions[session_id] = session
        return session
    
    def add_checkpoint(
        self,
        session_id: str,
        checkpoint_name: str,
        description: str = ""
    ) -> Checkpoint:
        """Add a checkpoint to a session"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        checkpoint = Checkpoint(
            checkpoint_id=f"cp_{len(session.checkpoints)}_{session_id}",
            name=checkpoint_name,
            description=description or f"Checkpoint: {checkpoint_name}",
            created_at=datetime.now().isoformat()
        )
        
        session.checkpoints.append(checkpoint)
        return checkpoint
    
    def await_approval(
        self,
        session_id: str,
        checkpoint_id: str,
        prompt: str,
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Await human approval at a checkpoint.
        
        Returns pending status and awaits human response.
        """
        session = self.sessions.get(session_id)
        if not session:
            return {'error': f"Session {session_id} not found"}
        
        checkpoint = next(
            (cp for cp in session.checkpoints if cp.checkpoint_id == checkpoint_id),
            None
        )
        
        if not checkpoint:
            return {'error': f"Checkpoint {checkpoint_id} not found"}
        
        checkpoint.awaiting_response = True
        
        response = {
            'session_id': session_id,
            'checkpoint_id': checkpoint_id,
            'prompt': prompt,
            'options': options or ['Approve', 'Reject', 'Modify'],
            'status': 'awaiting_response',
            'timestamp': datetime.now().isoformat()
        }
        
        # Notify callbacks
        for callback in self.checkpoint_callbacks:
            try:
                callback(response)
            except Exception:
                pass
        
        return response
    
    def submit_feedback(
        self,
        session_id: str,
        checkpoint_id: str,
        feedback_type: str,
        comment: str = "",
        modification: Optional[str] = None
    ) -> HumanFeedback:
        """
        Submit human feedback at a checkpoint.
        
        Args:
            session_id: Session ID
            checkpoint_id: Checkpoint ID
            feedback_type: Type of feedback (approve, reject, modify, etc.)
            comment: Human's comment
            modification: Suggested modification if feedback_type is 'modify'
        
        Returns:
            HumanFeedback object
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        checkpoint = next(
            (cp for cp in session.checkpoints if cp.checkpoint_id == checkpoint_id),
            None
        )
        
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        # Parse feedback type
        try:
            fb_type = FeedbackType(feedback_type.lower())
        except ValueError:
            fb_type = FeedbackType.APPROVE
        
        feedback = HumanFeedback(
            feedback_id=str(uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            feedback_type=fb_type,
            comment=comment,
            suggested_modification=modification,
            context={'checkpoint': checkpoint_id}
        )
        
        # Update checkpoint
        checkpoint.response = feedback
        checkpoint.awaiting_response = False
        checkpoint.approved = feedback_type.lower() in ['approve', 'confirm']
        
        # Add to history
        session.feedback_history.append(feedback)
        
        # Notify callbacks
        for callback in self.approval_callbacks:
            try:
                callback(feedback, session)
            except Exception:
                pass
        
        return feedback
    
    def can_proceed(self, session_id: str, checkpoint_id: str) -> bool:
        """Check if agent can proceed past checkpoint"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        checkpoint = next(
            (cp for cp in session.checkpoints if cp.checkpoint_id == checkpoint_id),
            None
        )
        
        if not checkpoint:
            return True  # No checkpoint means can proceed
        
        if checkpoint.awaiting_response:
            return False  # Still waiting for response
        
        return checkpoint.approved
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status"""
        session = self.sessions.get(session_id)
        if not session:
            return {'error': f"Session {session_id} not found"}
        
        checkpoints_status = []
        for cp in session.checkpoints:
            checkpoints_status.append({
                'id': cp.checkpoint_id,
                'name': cp.name,
                'status': 'awaiting' if cp.awaiting_response else ('approved' if cp.approved else 'rejected'),
                'response': cp.response.feedback_type.value if cp.response else None
            })
        
        return {
            'session_id': session_id,
            'task': session.task_description,
            'checkpoints': checkpoints_status,
            'approval_required': session.human_approved,
            'total_feedback': len(session.feedback_history),
            'status': session.status
        }
    
    def suggest_action(
        self,
        session_id: str,
        action: str,
        reasoning: str,
        code_preview: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Agent suggests an action and awaits human confirmation.
        
        Args:
            session_id: Session ID
            action: What the agent wants to do
            reasoning: Why the agent wants to do this
            code_preview: Preview of code changes
        
        Returns:
            Suggestion awaiting human response
        """
        session = self.sessions.get(session_id)
        if not session:
            return {'error': f"Session {session_id} not found"}
        
        suggestion = {
            'suggestion_id': str(uuid4())[:8],
            'action': action,
            'reasoning': reasoning,
            'code_preview': code_preview,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Notify human
        for callback in self.approval_callbacks:
            try:
                callback({'type': 'suggestion', 'data': suggestion}, session)
            except Exception:
                pass
        
        return suggestion
    
    def approve_suggestion(self, suggestion_id: str) -> bool:
        """Approve a suggestion (human action)"""
        # In real implementation, this would be triggered by human
        return True
    
    def get_pending_items(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all pending checkpoints and suggestions"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        items = []
        
        for cp in session.checkpoints:
            if cp.awaiting_response:
                items.append({
                    'type': 'checkpoint',
                    'id': cp.checkpoint_id,
                    'name': cp.name,
                    'description': cp.description
                })
        
        return items
    
    def add_checkpoint_callback(self, callback: Callable):
        """Add callback for checkpoint notifications"""
        self.checkpoint_callbacks.append(callback)
    
    def add_approval_callback(self, callback: Callable):
        """Add callback for approval events"""
        self.approval_callbacks.append(callback)


# Global collaboration manager
_collaboration = HumanAgentCollaboration()


def create_collaboration_session(
    task: str,
    require_approval: bool = True,
    checkpoints: Optional[List[str]] = None
) -> str:
    """Create a new collaboration session"""
    session = _collaboration.create_session(task, require_approval, checkpoints)
    return session.session_id


def request_approval(
    session_id: str,
    action: str,
    reasoning: str,
    code_preview: Optional[str] = None
) -> Dict[str, Any]:
    """Request human approval for an action"""
    return _collaboration.suggest_action(session_id, action, reasoning, code_preview)


def submit_human_feedback(
    session_id: str,
    checkpoint_id: str,
    response: str,
    comment: str = ""
) -> str:
    """Submit human feedback"""
    feedback = _collaboration.submit_feedback(
        session_id, checkpoint_id, response, comment
    )
    return feedback.feedback_id


# Skill functions
@register_skill
def start_collaboration(
    task: str,
    checkpoints: Optional[List[str]] = None,
    require_approval: bool = True
) -> str:
    """
    Start a human-agent collaboration session.
    
    Args:
        task: Task description
        checkpoints: Optional checkpoint names
        require_approval: Whether to require human approval
    
    Returns:
        Session ID
    """
    session = _collaboration.create_session(task, require_approval, checkpoints)
    return f"Collaboration started: {session.session_id}"


@register_skill
def add_human_checkpoint(
    session_id: str,
    checkpoint_name: str,
    description: str = ""
) -> str:
    """
    Add a human-in-the-loop checkpoint.
    
    Args:
        session_id: Collaboration session ID
        checkpoint_name: Name of checkpoint
        description: What to check
    
    Returns:
        Checkpoint ID
    """
    checkpoint = _collaboration.add_checkpoint(session_id, checkpoint_name, description)
    return f"Checkpoint added: {checkpoint.checkpoint_id}"


@register_skill
def await_human(
    session_id: str,
    checkpoint_id: str,
    prompt: str = "Please confirm to proceed"
) -> str:
    """
    Pause and wait for human response at a checkpoint.
    
    Args:
        session_id: Session ID
        checkpoint_id: Checkpoint ID
        prompt: What to ask human
    
    Returns:
        Status message
    """
    result = _collaboration.await_approval(session_id, checkpoint_id, prompt)
    return json.dumps(result, indent=2)


@register_skill
def submit_feedback(
    session_id: str,
    checkpoint_id: str,
    response: str,
    comment: str = ""
) -> str:
    """
    Submit human feedback at a checkpoint.
    
    Args:
        session_id: Session ID
        checkpoint_id: Checkpoint ID
        response: 'approve', 'reject', 'modify', or 'clarify'
        comment: Human's comment
    
    Returns:
        Feedback confirmation
    """
    feedback = _collaboration.submit_feedback(
        session_id, checkpoint_id, response, comment
    )
    
    response_msg = "approved" if feedback.feedback_type.value == "approve" else feedback.feedback_type.value
    return f"Feedback recorded: {response_msg} at {checkpoint_id}"


@register_skill
def get_collaboration_status(session_id: str) -> str:
    """
    Get current collaboration session status.
    
    Args:
        session_id: Session ID
    
    Returns:
        Status summary
    """
    status = _collaboration.get_session_status(session_id)
    return json.dumps(status, indent=2)


@register_skill
def suggest_and_wait(
    session_id: str,
    action: str,
    reasoning: str,
    code_preview: Optional[str] = None
) -> str:
    """
    Suggest an action and wait for human approval.
    
    Args:
        session_id: Session ID
        action: What you want to do
        reasoning: Why you want to do it
        code_preview: Optional code preview
    
    Returns:
        Suggestion awaiting approval
    """
    suggestion = _collaboration.suggest_action(session_id, action, reasoning, code_preview)
    return json.dumps(suggestion, indent=2)


# Skill metadata
human_collaboration_meta = {
    'name': 'human-collaboration',
    'description': 'Human-agent collaboration with checkpoints, approval workflow, and feedback loops',
    'category': 'collaboration',
    'keywords': ['collaboration', 'human', 'approval', 'feedback', 'checkpoint', 'confirm'],
    'competitor': 'Human-agent collaboration loops',
    'free': True
}