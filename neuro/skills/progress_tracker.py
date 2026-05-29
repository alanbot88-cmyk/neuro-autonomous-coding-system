"""
Real-time Progress Tracker - Visual browser state capture
Competitor: Real-time progress with screenshots

Features:
- Live progress updates
- Screenshot capture at each step
- Visual state display
- Step-by-step visualization
- Error highlighting
"""

import os
import json
import time
import base64
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import asyncio
from neuro.skills.skill_middleware import register_skill


class ProgressStatus(Enum):
    """Status of a progress step"""
    PENDING = "pending"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProgressStep:
    """Single progress step"""
    step_id: int
    name: str
    description: str
    status: ProgressStatus = ProgressStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    screenshot: Optional[str] = None  # Base64 encoded or path
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgressSnapshot:
    """Complete progress snapshot"""
    session_id: str
    total_steps: int
    completed_steps: int
    current_step: int
    overall_progress: float  # 0.0 to 1.0
    steps: List[ProgressStep]
    started_at: str
    estimated_time_remaining: float = 0.0
    current_screenshot: Optional[str] = None


class RealTimeProgressTracker:
    """
    Real-time Progress Tracker with visual state capture
    
    Features:
    - Live progress updates with percentage
    - Screenshot capture at each step
    - Visual state display (HTML/json)
    - Step-by-step history
    - Error highlighting
    - Estimated time remaining
    """
    
    def __init__(self, session_name: str = "default", output_dir: Optional[Path] = None):
        self.session_id = f"{session_name}_{int(time.time())}"
        self.output_dir = output_dir or Path("./progress_tracking")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.steps: List[ProgressStep] = []
        self.started_at = datetime.now().isoformat()
        self.step_templates: List[Dict[str, Any]] = []
        
        # Callbacks for live updates
        self._update_callbacks: List[Callable] = []
        self._screenshot_callbacks: List[Callable] = []
    
    def add_step(self, step: Dict[str, Any]) -> int:
        """Add a step to track"""
        step_id = len(self.steps)
        
        progress_step = ProgressStep(
            step_id=step_id,
            name=step.get('name', f"Step {step_id}"),
            description=step.get('description', ''),
            status=ProgressStatus.PENDING,
            data=step.get('data', {})
        )
        
        self.steps.append(progress_step)
        return step_id
    
    def add_steps(self, steps: List[Dict[str, Any]]):
        """Add multiple steps at once"""
        for step in steps:
            self.add_step(step)
    
    def start_step(self, step_id: int, screenshot: Optional[str] = None):
        """Mark a step as started"""
        if step_id < len(self.steps):
            self.steps[step_id].status = ProgressStatus.STARTED
            self.steps[step_id].started_at = datetime.now().isoformat()
            self.steps[step_id].screenshot = screenshot
            self._emit_update()
    
    def update_step(
        self,
        step_id: int,
        status: Optional[ProgressStatus] = None,
        screenshot: Optional[str] = None,
        error: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Update step progress"""
        if step_id < len(self.steps):
            step = self.steps[step_id]
            
            if status:
                step.status = status
            
            if screenshot:
                step.screenshot = screenshot
                self._emit_screenshot(step_id, screenshot)
            
            if error:
                step.error = error
            
            if data:
                step.data.update(data)
            
            # Mark completed if done
            if status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.SKIPPED]:
                step.completed_at = datetime.now().isoformat()
                if step.started_at:
                    start = datetime.fromisoformat(step.started_at)
                    step.duration_ms = (datetime.now() - start).total_seconds() * 1000
            
            self._emit_update()
    
    def complete_step(self, step_id: int, screenshot: Optional[str] = None):
        """Mark step as completed"""
        self.update_step(step_id, ProgressStatus.COMPLETED, screenshot)
    
    def fail_step(self, step_id: int, error: str, screenshot: Optional[str] = None):
        """Mark step as failed"""
        self.update_step(step_id, ProgressStatus.FAILED, screenshot, error)
    
    def skip_step(self, step_id: int):
        """Mark step as skipped"""
        self.update_step(step_id, ProgressStatus.SKIPPED)
    
    def add_screenshot_callback(self, callback: Callable):
        """Add callback for screenshot updates"""
        self._screenshot_callbacks.append(callback)
    
    def add_update_callback(self, callback: Callable):
        """Add callback for progress updates"""
        self._update_callbacks.append(callback)
    
    def _emit_update(self):
        """Emit progress update to callbacks"""
        snapshot = self.get_snapshot()
        for callback in self._update_callbacks:
            try:
                callback(snapshot)
            except Exception:
                pass
    
    def _emit_screenshot(self, step_id: int, screenshot: str):
        """Emit screenshot to callbacks"""
        for callback in self._screenshot_callbacks:
            try:
                callback(step_id, screenshot)
            except Exception:
                pass
    
    def get_snapshot(self) -> ProgressSnapshot:
        """Get current progress snapshot"""
        completed = sum(1 for s in self.steps if s.status == ProgressStatus.COMPLETED)
        total = len(self.steps)
        progress = completed / total if total > 0 else 0
        
        # Estimate remaining time
        completed_steps = [s for s in self.steps if s.duration_ms > 0]
        if completed_steps:
            avg_duration = sum(s.duration_ms for s in completed_steps) / len(completed_steps)
            remaining = sum(1 for s in self.steps if s.status not in [
                ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.SKIPPED
            ])
            estimated_ms = avg_duration * remaining
        else:
            estimated_ms = 0
        
        # Current screenshot
        current = next(
            (s.screenshot for s in reversed(self.steps) if s.screenshot),
            None
        )
        
        return ProgressSnapshot(
            session_id=self.session_id,
            total_steps=total,
            completed_steps=completed,
            current_step=len([s for s in self.steps if s.status != ProgressStatus.PENDING]),
            overall_progress=progress,
            steps=self.steps,
            started_at=self.started_at,
            estimated_time_remaining=estimated_ms / 1000,
            current_screenshot=current
        )
    
    def generate_html_report(self) -> str:
        """Generate HTML progress report with visual state"""
        snapshot = self.get_snapshot()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Progress: {snapshot.session_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: #0f172a; color: #f1f5f9; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        h1 {{ color: #6366f1; }}
        .progress-bar {{ background: #1e293b; height: 24px; border-radius: 12px; overflow: hidden; margin-bottom: 20px; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #6366f1, #22d3ee); transition: width 0.5s; }}
        .progress-text {{ text-align: center; font-size: 14px; margin-top: -20px; padding-top: 20px; }}
        .stats {{ display: flex; gap: 30px; margin-bottom: 30px; }}
        .stat {{ background: #1e293b; padding: 20px; border-radius: 12px; text-align: center; }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #6366f1; }}
        .stat-label {{ font-size: 0.8rem; opacity: 0.7; margin-top: 5px; }}
        .steps {{ display: flex; flex-direction: column; gap: 15px; }}
        .step {{ background: #1e293b; border-radius: 12px; padding: 20px; border-left: 4px solid #334155; }}
        .step.completed {{ border-left-color: #22c55e; }}
        .step.failed {{ border-left-color: #ef4444; }}
        .step.in_progress {{ border-left-color: #f59e0b; }}
        .step-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .step-name {{ font-weight: bold; }}
        .step-status {{ font-size: 0.8rem; padding: 4px 12px; border-radius: 20px; }}
        .status-pending {{ background: #334155; }}
        .status-completed {{ background: #22c55e; color: #0f172a; }}
        .status-failed {{ background: #ef4444; }}
        .status-in_progress {{ background: #f59e0b; color: #0f172a; }}
        .step-desc {{ font-size: 0.9rem; opacity: 0.8; margin-bottom: 15px; }}
        .step-screenshot {{ max-width: 100%; border-radius: 8px; margin-top: 15px; }}
        .step-error {{ color: #ef4444; font-size: 0.9rem; margin-top: 10px; }}
        .step-duration {{ font-size: 0.8rem; opacity: 0.6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Progress: {snapshot.session_id}</h1>
            <span>{datetime.now().strftime('%H:%M:%S')}</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {snapshot.overall_progress * 100}%"></div>
        </div>
        <div class="progress-text">{snapshot.overall_progress * 100:.1f}% complete</div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{snapshot.completed_steps}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat">
                <div class="stat-value">{snapshot.total_steps}</div>
                <div class="stat-label">Total Steps</div>
            </div>
            <div class="stat">
                <div class="stat-value">{snapshot.estimated_time_remaining:.0f}s</div>
                <div class="stat-label">Est. Remaining</div>
            </div>
        </div>
        
        <div class="steps">
"""
        
        for step in snapshot.steps:
            status_class = step.status.name.lower().replace('_', '-')
            
            html += f'''
            <div class="step {status_class}">
                <div class="step-header">
                    <span class="step-name">{step.step_id + 1}. {step.name}</span>
                    <span class="step-status status-{status_class}">{step.status.value}</span>
                </div>
                <div class="step-desc">{step.description}</div>
'''
            
            if step.error:
                html += f'<div class="step-error">❌ {step.error}</div>\n'
            
            if step.screenshot:
                html += f'<img class="step-screenshot" src="{step.screenshot}" alt="Step {step.step_id + 1}">\n'
            
            if step.duration_ms > 0:
                html += f'<div class="step-duration">⏱ {step.duration_ms / 1000:.1f}s</div>\n'
            
            html += '</div>\n'
        
        html += '''
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def generate_json_report(self) -> str:
        """Generate JSON progress report"""
        return json.dumps(self.get_snapshot().__dict__, indent=2, default=str)
    
    def save_report(self, format: str = 'html') -> str:
        """Save progress report to file"""
        snapshot = self.get_snapshot()
        
        if format == 'html':
            content = self.generate_html_report()
            filepath = self.output_dir / f"{snapshot.session_id}.html"
        else:
            content = self.generate_json_report()
            filepath = self.output_dir / f"{snapshot.session_id}.json"
        
        filepath.write_text(content, encoding='utf-8')
        return str(filepath)
    
    def render_current_state(self) -> Dict[str, Any]:
        """Get current visual state for display"""
        snapshot = self.get_snapshot()
        
        current_step = next(
            (s for s in reversed(snapshot.steps) if s.status in [
                ProgressStatus.STARTED, ProgressStatus.IN_PROGRESS
            ]),
            snapshot.steps[-1] if snapshot.steps else None
        )
        
        return {
            'session_id': snapshot.session_id,
            'progress_percent': round(snapshot.overall_progress * 100, 1),
            'completed': snapshot.completed_steps,
            'total': snapshot.total_steps,
            'current_step_name': current_step.name if current_step else None,
            'current_step_description': current_step.description if current_step else None,
            'current_screenshot': current_step.screenshot if current_step else None,
            'last_error': next(
                (s.error for s in reversed(snapshot.steps) if s.error),
                None
            ),
            'estimated_remaining': round(snapshot.estimated_time_remaining),
            'steps_summary': [
                {'id': s.step_id, 'name': s.name, 'status': s.status.value}
                for s in snapshot.steps
            ]
        }


@register_skill
def track_progress(steps: List[Dict[str, Any]]) -> str:
    """
    Create a progress tracker for multi-step workflows.
    
    Args:
        steps: List of step definitions with 'name' and 'description'
    
    Returns:
        Progress tracker ID for tracking
    """
    tracker = RealTimeProgressTracker()
    tracker.add_steps(steps)
    
    snapshot = tracker.get_snapshot()
    return f"Progress tracker created: {snapshot.session_id} ({len(steps)} steps)"


@register_skill
def get_progress_state(tracker_id: str) -> Dict[str, Any]:
    """
    Get current state of a progress tracker.
    
    Args:
        tracker_id: Session ID of the tracker
    
    Returns:
        Current progress state
    """
    # This would need to be retrieved from persistent storage in real implementation
    return {
        'tracker_id': tracker_id,
        'message': 'Tracker state would be retrieved from session storage'
    }


# Example usage function
def create_tracker_for_workflow(workflow_name: str, steps: List[str]) -> RealTimeProgressTracker:
    """Create a tracker for a workflow with named steps"""
    tracker = RealTimeProgressTracker(session_name=workflow_name)
    
    for i, step_name in enumerate(steps):
        tracker.add_step({
            'name': step_name,
            'description': f"Step {i+1}: {step_name}",
            'data': {'index': i}
        })
    
    return tracker


# Skill metadata
progress_tracker_meta = {
    'name': 'progress-tracker',
    'description': 'Real-time progress tracking with visual screenshots and state display',
    'category': 'visualization',
    'keywords': ['progress', 'tracker', 'screenshot', 'visual', 'state', 'status'],
    'competitor': 'Real-time progress tracking',
    'free': True
}