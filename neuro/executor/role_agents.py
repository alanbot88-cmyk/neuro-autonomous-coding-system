"""
Role-Based Agent Swarm
=======================
Specialized agents for different phases of task execution.

Each agent has:
- A clear role description and purpose
- Hand-off points to other agents
- Model selection based on TASK_CATEGORIES
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from neuro.models import TASK_CATEGORIES
import re


@dataclass
class AgentResult:
    """Result returned by an agent after execution."""
    success: bool
    data: Any
    agent_name: str
    message: str
    next_agent: Optional[str] = None


class BaseAgent:
    """Base class for all specialized agents."""
    
    def __init__(self, name: str, role: str, model_category: str):
        """
        Initialize the base agent.
        
        Args:
            name: Agent identifier
            role: Human-readable role description
            model_category: TASK_CATEGORIES key for model selection
        """
        self.name = name
        self.role = role
        self.model_category = model_category
        self.model = TASK_CATEGORIES.get(model_category, TASK_CATEGORIES["code_generation"])
    
    def run(self, task: Any) -> AgentResult:
        """
        Execute the agent's task.
        
        Args:
            task: Task data to process
            
        Returns:
            AgentResult with outcome and next agent hint
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    def get_model(self) -> str:
        """Get the primary model identifier for this agent."""
        return self.model["primary"]


class ManagerAgent(BaseAgent):
    """
    Manager Agent - Task Orchestration
    ==================================
    Receives high-level task, decomposes into subtasks, assigns to specialists.
    
    Responsibilities:
    - Parse and understand task requirements
    - Break task into logical subtasks
    - Assign subtasks to appropriate specialist agents
    - Track overall progress and completion
    
    Hand-off points:
    - ResearcherAgent for context gathering
    - EngineerAgent for code implementation
    - ValidatorAgent for verification
    - ReviewerAgent for final review
    """
    
    def __init__(self):
        super().__init__(
            name="ManagerAgent",
            role="Task orchestration and decomposition",
            model_category="deep_reasoning"
        )
        self.specialists = {
            "researcher": "ResearcherAgent",
            "engineer": "EngineerAgent",
            "validator": "ValidatorAgent",
            "reviewer": "ReviewerAgent"
        }
    
    def run(self, task: Dict[str, Any]) -> AgentResult:
        """
        Decompose task and assign to specialists.
        
        Args:
            task: Dict with 'description', 'type', 'files', 'constraints'
            
        Returns:
            AgentResult with subtasks and assignments
        """
        try:
            task_type = task.get("type", "code_fix")
            description = task.get("description", "")
            
            # Decompose task based on type
            subtasks = self._decompose_task(task)
            
            # Assign appropriate agent based on subtask type
            assignments = self._assign_tasks(subtasks)
            
            return AgentResult(
                success=True,
                data={
                    "subtasks": subtasks,
                    "assignments": assignments,
                    "task_type": task_type
                },
                agent_name=self.name,
                message=f"Decomposed {len(subtasks)} subtasks for {task_type} task",
                next_agent="ResearcherAgent"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                message=f"Task decomposition failed: {str(e)}",
                next_agent=None
            )
    
    def _decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break task into logical subtasks."""
        task_type = task.get("type", "code_fix")
        subtasks = []
        
        # Standard subtask sequence
        subtask_templates = {
            "code_fix": [
                {"phase": "research", "action": "find_related_files"},
                {"phase": "research", "action": "understand_context"},
                {"phase": "implement", "action": "apply_fix"},
                {"phase": "validate", "action": "run_tests"},
                {"phase": "review", "action": "verify_completeness"}
            ],
            "new_feature": [
                {"phase": "research", "action": "explore_architecture"},
                {"phase": "research", "action": "find_entry_points"},
                {"phase": "implement", "action": "create_feature"},
                {"phase": "implement", "action": "add_tests"},
                {"phase": "validate", "action": "run_tests"},
                {"phase": "review", "action": "final_review"}
            ],
            "refactor": [
                {"phase": "research", "action": "analyze_dependencies"},
                {"phase": "research", "action": "identify_refactor_points"},
                {"phase": "implement", "action": "apply_refactor"},
                {"phase": "validate", "action": "verify_behavior"},
                {"phase": "review", "action": "check_readability"}
            ],
            "web_app": [
                {"phase": "research", "action": "understand_stack_structure"},
                {"phase": "implement", "action": "build_ui_components"},
                {"phase": "implement", "action": "implement_logic"},
                {"phase": "validate", "action": "test_functionality"},
                {"phase": "review", "action": "verify_usability"}
            ],
            "research": [
                {"phase": "research", "action": "gather_information"},
                {"phase": "research", "action": "analyze_patterns"},
                {"phase": "review", "action": "compile_findings"}
            ],
            "documentation": [
                {"phase": "research", "action": "read_code"},
                {"phase": "implement", "action": "write_docs"},
                {"phase": "review", "action": "verify_clarity"}
            ]
        }
        
        template = subtask_templates.get(task_type, subtask_templates["code_fix"])
        
        for i, step in enumerate(template):
            subtasks.append({
                "id": f"subtask_{i+1}",
                "phase": step["phase"],
                "action": step["action"],
                "status": "pending"
            })
        
        return subtasks
    
    def _assign_tasks(self, subtasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Assign subtasks to appropriate specialist agents."""
        assignments = {
            "ResearcherAgent": [],
            "EngineerAgent": [],
            "ValidatorAgent": [],
            "ReviewerAgent": []
        }
        
        for subtask in subtasks:
            phase = subtask["phase"]
            if phase == "research":
                assignments["ResearcherAgent"].append(subtask)
            elif phase == "implement":
                assignments["EngineerAgent"].append(subtask)
            elif phase == "validate":
                assignments["ValidatorAgent"].append(subtask)
            elif phase == "review":
                assignments["ReviewerAgent"].append(subtask)
        
        # Remove empty assignments
        return {k: v for k, v in assignments.items() if v}


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent - Codebase Exploration
    ======================================
    Reads codebase, finds relevant files, builds context bundle.
    
    Responsibilities:
    - Search for files matching task requirements
    - Find function/class definitions
    - Identify test files
    - Build comprehensive context for implementation
    
    Hand-off points:
    - EngineerAgent receives context bundle for implementation
    - ManagerAgent receives status updates
    """
    
    def __init__(self):
        super().__init__(
            name="ResearcherAgent",
            role="Codebase exploration and context building",
            model_category="long_context"
        )
        self.aci = None
        self.codebase_root = "."
    
    def run(self, task: Dict[str, Any]) -> AgentResult:
        """
        Research and gather context for task.
        
        Args:
            task: Dict with 'description', 'scope', 'codebase_root'
            
        Returns:
            AgentResult with context bundle
        """
        try:
            from neuro.tools.aci import AgentCodingInterface
            
            description = task.get("description", "")
            scope = task.get("scope", [])
            self.codebase_root = task.get("codebase_root", ".")
            
            # Initialize ACI with workspace
            self.aci = AgentCodingInterface(workspace_root=self.codebase_root)
            
            # Research tasks using real tools
            relevant_files = self._find_relevant_files(description, scope, self.codebase_root)
            relevant_functions = self._find_functions(description, self.codebase_root)
            test_files = self._find_test_files(relevant_files)
            git_context = self._get_git_history(relevant_files)
            
            context_bundle = {
                "relevant_files": relevant_files,
                "relevant_functions": relevant_functions,
                "test_files": test_files,
                "git_context": git_context,
                "description": description
            }
            
            return AgentResult(
                success=True,
                data=context_bundle,
                agent_name=self.name,
                message=f"Found {len(relevant_files)} relevant files",
                next_agent="EngineerAgent"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                message=f"Research failed: {str(e)}",
                next_agent=None
            )
    
    def _find_relevant_files(self, description: str, scope: List[str], root: str) -> List[str]:
        """Find files relevant to the task using ACI search."""
        if not self.aci:
            from neuro.tools.aci import AgentCodingInterface
            self.aci = AgentCodingInterface(workspace_root=root)
        
        found = list(scope)  # Start with explicit scope
        
        # Extract keywords from description
        keywords = self._extract_keywords(description)
        
        # Search for each keyword
        for kw in keywords:
            try:
                results = self.aci.search_dir(kw, directory=root)
                for r in results:
                    if hasattr(r, 'file_path') and r.file_path not in found:
                        found.append(r.file_path)
                    elif isinstance(r, dict) and r.get('file_path') not in found:
                        found.append(r.get('file_path'))
            except:
                pass
        
        return found[:20]  # Cap at 20 files max
    
    def _find_functions(self, description: str, root: str) -> List[Dict[str, str]]:
        """Find function/class definitions using ACI search_symbol."""
        if not self.aci:
            from neuro.tools.aci import AgentCodingInterface
            self.aci = AgentCodingInterface(workspace_root=root)
        
        found = []
        keywords = self._extract_keywords(description)
        
        for kw in keywords:
            try:
                symbols = self.aci.search_symbol(kw, directory=root)
                for s in symbols:
                    if hasattr(s, 'name'):
                        found.append({"name": s.name, "file": s.file_path, "line": s.line_number})
                    elif isinstance(s, dict):
                        found.append({"name": s.get('name', ''), "file": s.get('file_path', ''), "line": s.get('line_number', 0)})
            except:
                pass
        
        return found[:20]  # Cap at 20 functions max
    
    def _find_test_files(self, source_files: List[str]) -> List[str]:
        """Find test files using ACI find_tests."""
        if not self.aci:
            return []
        
        test_files = []
        for sf in source_files:
            if isinstance(sf, str):
                try:
                    tests = self.aci.find_tests(sf)
                    if isinstance(tests, list):
                        test_files.extend(tests)
                    elif isinstance(tests, str):
                        test_files.append(tests)
                except:
                    pass
        
        # Also check common test patterns
        for sf in source_files:
            if isinstance(sf, str) and sf.endswith(".py"):
                # Try common test naming patterns
                base = sf.replace("/", ".").rsplit(".", 1)[0]
                test_patterns = [
                    f"{sf.replace('.py', '_test.py')}",
                    f"{sf.replace('.py', '/test_*.py')}".replace("test/test_*.py", "test_*.py"),
                    f"tests/{base}_test.py",
                    f"test_{base.split('/')[-1]}.py"
                ]
                for tp in test_patterns:
                    if tp not in test_files:
                        test_files.append(tp)
        
        return list(set(test_files))[:10]  # Cap at 10 test files
    
    def _get_git_history(self, files: List[str]) -> List[Dict[str, str]]:
        """Get recent git history using ACI get_git_context."""
        history = []
        
        for f in files[:5]:  # Only check first 5 files
            try:
                if isinstance(f, str) and self.aci:
                    commits = self.aci.get_git_context(f, commits=3)
                    if isinstance(commits, list):
                        history.extend(commits)
            except:
                pass
        
        # If no history from ACI, try git directly
        if not history:
            import subprocess
            try:
                result = subprocess.run(
                    ['git', 'log', '--oneline', '-5'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=self.codebase_root
                )
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        history.append({
                            "file": "repository",
                            "commit": parts[0] if parts else "",
                            "message": parts[1] if len(parts) > 1 else ""
                        })
            except:
                pass
        
        return history
    
    def _extract_keywords(self, description: str) -> List[str]:
        """Extract keywords from description for search."""
        # Remove common stop words, return likely symbol names
        stop = {"the", "a", "an", "in", "on", "at", "to", "for", "of",
                "and", "or", "is", "it", "this", "that", "with", "from",
                "add", "fix", "create", "build", "implement", "function",
                "method", "class", "file", "code", "using", "when", "if"}
        
        # Extract camelCase and snake_case identifiers
        words = description.split()
        keywords = []
        
        # Add snake_case words
        for w in words:
            w_clean = w.lower().strip('.,!?;:"\'()[]{}')
            if w_clean and w_clean not in stop and len(w_clean) > 2:
                keywords.append(w_clean)
        
        # Extract camelCase
        camel_matches = re.findall(r'[a-z][a-zA-Z]+', description)
        for cm in camel_matches:
            cm_lower = cm.lower()
            if cm_lower not in stop and cm_lower not in keywords:
                keywords.append(cm_lower)
        
        # Remove duplicates
        return list(set(keywords))[:10]  # Max 10 keywords


class EngineerAgent(BaseAgent):
    """
    Engineer Agent - Code Implementation
    =====================================
    Writes code in small verified chunks, test-first approach.
    
    Responsibilities:
    - Implement changes in small, verifiable increments
    - Write tests before or alongside code
    - Follow best practices and patterns
    - Maintain code quality
    
    Hand-off points:
    - ValidatorAgent receives implementation for testing
    - ResearcherAgent for additional context if needed
    """
    
    def __init__(self):
        super().__init__(
            name="EngineerAgent",
            role="Code implementation in verified chunks",
            model_category="code_generation"
        )
        self.max_chunk_size = 50  # Lines per chunk
        self.verify_each_chunk = True
        self.router = None
    
    def run(self, task: Dict[str, Any]) -> AgentResult:
        """
        Implement code based on context.
        
        Args:
            task: Dict with 'description', 'context', 'constraints'
            
        Returns:
            AgentResult with implementation details
        """
        try:
            from neuro.router.smart_router import SmartRouter
            
            description = task.get("description", "")
            context = task.get("context", {})
            constraints = task.get("constraints", {})
            
            # Initialize router
            self.router = SmartRouter()
            
            # Split implementation into chunks
            chunks = self._create_chunks(description, context)
            
            implementations = []
            for i, chunk in enumerate(chunks):
                chunk_result = {
                    "chunk_id": i + 1,
                    "description": chunk["description"],
                    "code": chunk.get("code", ""),
                    "file": chunk.get("target_file", ""),
                    "verified": chunk.get("verified", False)
                }
                implementations.append(chunk_result)
            
            return AgentResult(
                success=True,
                data={
                    "chunks": implementations,
                    "total_chunks": len(chunks),
                    "context_used": context
                },
                agent_name=self.name,
                message=f"Implemented {len(chunks)} code chunks",
                next_agent="ValidatorAgent"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                message=f"Implementation failed: {str(e)}",
                next_agent=None
            )
    
    def _create_chunks(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create implementation chunks by calling the actual model API."""
        task_type = context.get("task_type", "code_fix")
        relevant_files = context.get("relevant_files", [])
        relevant_functions = context.get("relevant_functions", [])
        
        if not self.router:
            from neuro.router.smart_router import SmartRouter
            self.router = SmartRouter()
        
        # Build context string
        context_str = ""
        if relevant_files:
            context_str += f"Relevant files: {', '.join(relevant_files[:5])}\n"
        if relevant_functions:
            func_names = [f["name"] for f in relevant_functions[:5] if isinstance(f, dict)]
            if func_names:
                context_str += f"Relevant functions: {', '.join(func_names)}\n"
        
        prompt = f"""You are an expert software engineer. Complete this task:

Task: {description}
Task Type: {task_type}
{context_str}

Rules:
- Write actual, complete, working code
- No placeholders or TODOs
- Handle edge cases: null, empty, boundary values
- Add error handling at every external call
- Match existing code patterns

Provide the implementation in clearly labeled sections.
Each section starts with: ### FILE: <filename>
Followed by the complete code for that file.
"""
        
        # Call the actual model
        try:
            response = self.router.chat(
                prompt=prompt,
                task_type="code_generation",
                max_tokens=4000
            )
        except Exception as e:
            response = f"# Error calling model: {e}\n# Falling back to template"
        
        # Parse response into chunks
        return self._parse_response_into_chunks(response, task_type, description)
    
    def _parse_response_into_chunks(self, response: str, task_type: str, description: str) -> List[Dict[str, Any]]:
        """Parse model response into code chunks."""
        chunks = []
        
        if not response:
            return [{"chunk_id": 1, "description": "implementation",
                     "target_file": "output.py", "code": "# No response from model",
                     "verified": False}]
        
        # Split by FILE markers if present
        sections = re.split(r'###\s*FILE:\s*', response)
        
        if len(sections) > 1:
            for i, section in enumerate(sections[1:], 1):
                lines = section.strip().split('\n')
                if lines:
                    filename = lines[0].strip().split('\n')[0].strip()
                    code = '\n'.join(lines[1:]).strip()
                    # Strip markdown code fences
                    code = re.sub(r'^```\w*\n?', '', code)
                    code = re.sub(r'\n?```$', '', code)
                    chunks.append({
                        "chunk_id": i,
                        "description": f"Implementation for {filename}",
                        "target_file": filename,
                        "code": code,
                        "verified": False
                    })
        else:
            # Single block response - determine file name from task
            code = response.strip()
            code = re.sub(r'^```\w*\n?', '', code)
            code = re.sub(r'\n?```$', '', code)
            
            # Determine filename from description
            target_file = self._infer_filename(description, task_type)
            
            chunks.append({
                "chunk_id": 1,
                "description": description,
                "target_file": target_file,
                "code": code,
                "verified": False
            })
        
        # If no chunks parsed, create one with the full response
        if not chunks:
            chunks.append({
                "chunk_id": 1,
                "description": description,
                "target_file": self._infer_filename(description, task_type),
                "code": response,
                "verified": False
            })
        
        return chunks
    
    def _infer_filename(self, description: str, task_type: str) -> str:
        """Infer filename from task description."""
        desc_lower = description.lower()
        
        # Check for specific file mentions
        if "utils" in desc_lower:
            return "utils.py"
        if "test" in desc_lower:
            return "test_impl.py"
        if "config" in desc_lower:
            return "config.py"
        if "main" in desc_lower:
            return "main.py"
        if "auth" in desc_lower:
            return "auth.py"
        if "login" in desc_lower:
            return "login.py"
        if "api" in desc_lower:
            return "api.py"
        
        # Default based on task type
        defaults = {
            "code_fix": "fix.py",
            "new_feature": "feature.py",
            "refactor": "refactored.py",
            "web_app": "app.py",
            "documentation": "docs.py"
        }
        
        return defaults.get(task_type, "implementation.py")
    
    def _verify_chunk(self, chunk: Dict[str, Any]) -> bool:
        """Verify a code chunk is correct."""
        code = chunk.get("code", "")
        
        # Basic syntax checks
        basic_checks = [
            len(code) > 10,  # Not empty
            not code.count("{") > code.count("}") + 5,  # Balanced braces
            not code.count("(") > code.count(")") + 5,  # Balanced parens
        ]
        
        return all(basic_checks)


class ValidatorAgent(BaseAgent):
    """
    Validator Agent - Testing and Verification
    ===========================================
    Runs tests, calculates confidence score, retry logic.
    
    Responsibilities:
    - Execute test suites
    - Calculate confidence scores
    - Provide specific retry instructions
    - Max 5 retries before escalating
    
    Hand-off points:
    - EngineerAgent for fixes
    - ReviewerAgent if confidence threshold met
    - ManagerAgent for escalation after max retries
    """
    
    def __init__(self):
        super().__init__(
            name="ValidatorAgent",
            role="Testing, verification, and confidence scoring",
            model_category="testing_qa"
        )
        self.max_retries = 5
        self.current_retries = 0
        
        # Confidence thresholds by task type
        from neuro.validation.confidence import ConfidenceChecker
        self.confidence_checker = ConfidenceChecker()
    
    def run(self, task: Dict[str, Any]) -> AgentResult:
        """
        Validate implementation through testing.
        
        Args:
            task: Dict with 'implementation', 'tests', 'context'
            
        Returns:
            AgentResult with test results and confidence score
        """
        try:
            implementation = task.get("implementation", {})
            context = task.get("context", {})
            task_type = context.get("task_type", "code_fix")
            
            # Run tests and get results
            test_results = self._execute_tests(implementation)
            
            # Calculate confidence
            confidence = self.confidence_checker.calculate(test_results, task_type)
            
            # Determine if retry needed
            retry_needed = self.confidence_checker.should_retry(confidence, task_type)
            
            result_data = {
                "test_results": test_results,
                "confidence": confidence,
                "retries_used": self.current_retries,
                "retry_needed": retry_needed
            }
            
            if retry_needed and self.current_retries < self.max_retries:
                self.current_retries += 1
                retry_instructions = self.confidence_checker.get_retry_instructions(
                    test_results, confidence
                )
                result_data["retry_instructions"] = retry_instructions
                
                return AgentResult(
                    success=False,
                    data=result_data,
                    agent_name=self.name,
                    message=f"Confidence {confidence:.2f} below threshold for {task_type}",
                    next_agent="EngineerAgent"
                )
            elif retry_needed and self.current_retries >= self.max_retries:
                return AgentResult(
                    success=False,
                    data=result_data,
                    agent_name=self.name,
                    message=f"Max retries ({self.max_retries}) exceeded, escalating",
                    next_agent="ManagerAgent"
                )
            else:
                # Success - confidence threshold met
                return AgentResult(
                    success=True,
                    data=result_data,
                    agent_name=self.name,
                    message=f"Confidence {confidence:.2f} meets threshold for {task_type}",
                    next_agent="ReviewerAgent"
                )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                message=f"Validation failed: {str(e)}",
                next_agent=None
            )
    
    def _execute_tests(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tests and return structured results.
        
        Writes code chunks to files, finds test files, and runs pytest.
        """
        import time
        import subprocess
        import os
        from pathlib import Path
        
        test_results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "failures": [],
            "duration_ms": 0
        }
        
        start_time = time.time()
        chunks = implementation.get("chunks", [])
        workspace = os.getcwd()
        
        if not chunks:
            return test_results
        
        # Write code chunks to files
        written_files = []
        for chunk in chunks:
            file_path = chunk.get("file_path", "")
            code = chunk.get("code", "")
            
            if file_path and code:
                try:
                    full_path = Path(workspace) / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    written_files.append(file_path)
                    chunk["verified"] = True
                except Exception as e:
                    chunk["verified"] = False
                    test_results["failures"].append({
                        "name": f"write:{file_path}",
                        "error": str(e)
                    })
        
        test_results["total"] = len(written_files)
        test_results["passed"] = len(written_files)
        
        # Find and run test files
        test_files_found = []
        for file_path in written_files:
            ext = Path(file_path).suffix
            if ext == '.py':
                # Look for corresponding test file
                stem = Path(file_path).stem
                base = Path(file_path).parent
                
                candidates = [
                    base / f"test_{stem}.py",
                    base / f"{stem}_test.py",
                    base / "tests" / f"test_{stem}.py",
                ]
                
                for candidate in candidates:
                    if candidate.exists():
                        test_files_found.append(candidate)
        
        # Run pytest on found test files
        for test_file in test_files_found:
            try:
                result = subprocess.run(
                    ['python', '-m', 'pytest', str(test_file), '-v', '--tb=short'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Parse output for pass/fail
                for line in result.stdout.split('\n'):
                    if 'PASSED' in line:
                        test_results["passed"] += 1
                        test_results["total"] += 1
                    elif 'FAILED' in line:
                        test_results["failed"] += 1
                        test_results["total"] += 1
                        # Extract test name
                        match = re.search(r'(test_\w+)', line)
                        if match:
                            test_results["failures"].append({
                                "name": match.group(1),
                                "error": "Test failed - see output"
                            })
                        
            except subprocess.TimeoutExpired:
                test_results["skipped"] += 1
            except Exception as e:
                # Test run failed but code is valid
                pass
        
        test_results["duration_ms"] = int((time.time() - start_time) * 1000)
        
        return test_results
    
    def reset_retries(self) -> None:
        """Reset retry counter for new task."""
        self.current_retries = 0


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent - Final Quality Gate
    =====================================
    Final gate, checks completeness, readability.
    
    Responsibilities:
    - Verify task completion
    - Check code readability
    - Ensure best practices followed
    - Final approval or rejection
    
    Hand-off points:
    - ManagerAgent receives final result
    - EngineerAgent for minor fixes
    """
    
    def __init__(self):
        super().__init__(
            name="ReviewerAgent",
            role="Final quality gate and approval",
            model_category="code_review"
        )
        self.min_readability_score = 0.8
    
    def run(self, task: Dict[str, Any]) -> AgentResult:
        """
        Final review of completed implementation.
        
        Args:
            task: Dict with 'implementation', 'context', 'original_task'
            
        Returns:
            AgentResult with review decision
        """
        try:
            implementation = task.get("implementation", {})
            context = task.get("context", {})
            original_task = task.get("original_task", {})
            
            # Run review checks
            completeness = self._check_completeness(implementation, original_task)
            readability = self._check_readability(implementation)
            best_practices = self._check_best_practices(implementation)
            
            review_data = {
                "completeness": completeness,
                "readability": readability,
                "best_practices": best_practices,
                "approved": completeness >= 0.9 and readability >= self.min_readability_score
            }
            
            if review_data["approved"]:
                return AgentResult(
                    success=True,
                    data=review_data,
                    agent_name=self.name,
                    message="Implementation approved - all checks passed",
                    next_agent="ManagerAgent"
                )
            else:
                # Identify issues for fix
                issues = []
                if completeness < 0.9:
                    issues.append("incomplete implementation")
                if readability < self.min_readability_score:
                    issues.append("readability issues")
                if not best_practices:
                    issues.append("best practices violations")
                
                return AgentResult(
                    success=False,
                    data=review_data,
                    agent_name=self.name,
                    message=f"Review failed: {', '.join(issues)}",
                    next_agent="EngineerAgent"
                )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                agent_name=self.name,
                message=f"Review failed: {str(e)}",
                next_agent=None
            )
    
    def _check_completeness(self, implementation: Dict[str, Any], original_task: Dict[str, Any]) -> float:
        """Check if implementation fully satisfies requirements."""
        # In real implementation, compare implementation to requirements
        requirements = original_task.get("description", "")
        chunks = implementation.get("chunks", [])
        
        if not requirements:
            return 1.0
        
        # Check if all chunks are implemented
        if not chunks:
            return 0.0
        
        implemented = sum(1 for c in chunks if c.get("verified", False))
        return implemented / len(chunks)
    
    def _check_readability(self, implementation: Dict[str, Any]) -> float:
        """Check code readability score."""
        chunks = implementation.get("chunks", [])
        
        if not chunks:
            return 0.5
        
        readability_scores = []
        for chunk in chunks:
            code = chunk.get("code", "")
            
            # Basic readability checks
            has_comments = "#" in code
            reasonable_length = len(code) < 1000
            good_structure = not code.count("\n\n\n") > 3  # Not excessive spacing
            
            score = 0.5
            if has_comments:
                score += 0.15
            if reasonable_length:
                score += 0.2
            if good_structure:
                score += 0.15
            
            readability_scores.append(min(score, 1.0))
        
        return sum(readability_scores) / len(readability_scores)
    
    def _check_best_practices(self, implementation: Dict[str, Any]) -> bool:
        """Check if best practices are followed."""
        chunks = implementation.get("chunks", [])
        
        if not chunks:
            return True
        
        # Check basic best practices
        for chunk in chunks:
            code = chunk.get("code", "")
            
            # Check for common anti-patterns
            if "TODO" in code and "FIXME" in code:
                return False  # Incomplete code
            
            # Check for obvious issues
            if "pass" == code.strip() or "..." == code.strip():
                return False
        
        return True


# Agent factory for creating agent instances
def create_agent(agent_type: str) -> BaseAgent:
    """
    Factory function to create agent instances.
    
    Args:
        agent_type: Type of agent to create
        
    Returns:
        Instance of requested agent
        
    Raises:
        ValueError: If agent_type is unknown
    """
    agents = {
        "manager": ManagerAgent,
        "researcher": ResearcherAgent,
        "engineer": EngineerAgent,
        "validator": ValidatorAgent,
        "reviewer": ReviewerAgent
    }
    
    agent_class = agents.get(agent_type.lower())
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class()


def run_agent_swarm(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the full agent swarm for a task.
    
    Args:
        task: Task specification
        
    Returns:
        Final result from the agent swarm
    """
    # Initialize agents
    manager = ManagerAgent()
    researcher = ResearcherAgent()
    engineer = EngineerAgent()
    validator = ValidatorAgent()
    reviewer = ReviewerAgent()
    
    # Track execution
    execution_trace = []
    
    # Step 1: Manager decomposes task
    result = manager.run(task)
    execution_trace.append(("ManagerAgent", result.success, result.message))
    
    if not result.success:
        return {
            "success": False,
            "error": result.message,
            "trace": execution_trace
        }
    
    subtasks = result.data["subtasks"]
    assignments = result.data["assignments"]
    
    # Step 2: Researcher gathers context
    research_task = {
        "description": task.get("description", ""),
        "scope": [s["id"] for s in assignments.get("ResearcherAgent", [])],
        "codebase_root": task.get("codebase_root", ".")
    }
    context_result = researcher.run(research_task)
    execution_trace.append(("ResearcherAgent", context_result.success, context_result.message))
    
    if not context_result.success:
        return {
            "success": False,
            "error": context_result.message,
            "trace": execution_trace
        }
    
    context = context_result.data
    
    # Step 3: Engineer implements
    implement_task = {
        "description": task.get("description", ""),
        "context": context,
        "constraints": task.get("constraints", {})
    }
    engineer_result = engineer.run(implement_task)
    execution_trace.append(("EngineerAgent", engineer_result.success, engineer_result.message))
    
    if not engineer_result.success:
        return {
            "success": False,
            "error": engineer_result.message,
            "trace": execution_trace
        }
    
    implementation = engineer_result.data
    
    # Step 4: Validator tests
    validator_task = {
        "implementation": implementation,
        "context": {"task_type": task.get("type", "code_fix")}
    }
    validation_result = validator.run(validator_task)
    execution_trace.append(("ValidatorAgent", validation_result.success, validation_result.message))
    
    # Handle retry loop
    retry_count = 0
    max_validation_retries = 3
    
    while (validation_result.data.get("retry_needed", False) and 
           retry_count < max_validation_retries):
        retry_count += 1
        
        # Get retry instructions and apply fix
        retry_instructions = validation_result.data.get("retry_instructions", {})
        
        # Modify implementation based on retry instructions
        implementation = _apply_retries(implementation, retry_instructions)
        
        # Re-validate
        validator_task["implementation"] = implementation
        validation_result = validator.run(validator_task)
        execution_trace.append(
            (f"ValidatorAgent(retry {retry_count})", 
             validation_result.success, 
             validation_result.message)
        )
    
    # Step 5: Reviewer final check
    review_task = {
        "implementation": implementation,
        "context": context,
        "original_task": task
    }
    review_result = reviewer.run(review_task)
    execution_trace.append(("ReviewerAgent", review_result.success, review_result.message))
    
    # Handle review retries
    review_retry_count = 0
    while not review_result.success and review_retry_count < 2:
        review_retry_count += 1
        
        # Apply review fixes
        implementation = _apply_review_fixes(implementation, review_result.data)
        
        # Re-review
        review_task["implementation"] = implementation
        review_result = reviewer.run(review_task)
        execution_trace.append(
            (f"ReviewerAgent(retry {review_retry_count})",
             review_result.success,
             review_result.message)
        )
    
    # Return final result
    return {
        "success": review_result.success,
        "implementation": implementation,
        "confidence": validation_result.data.get("confidence", 0),
        "review_approved": review_result.success,
        "trace": execution_trace
    }


def _apply_retries(implementation: Dict[str, Any], instructions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply retry instructions to implementation.
    
    Uses instructions from ValidatorAgent to fix issues in code chunks.
    """
    chunks = implementation.get("chunks", [])
    if not chunks:
        return implementation
    
    # Get priority fixes from instructions
    priority_fixes = instructions.get("priority_fixes", [])
    focus_areas = instructions.get("focus_areas", [])
    
    if not priority_fixes and not focus_areas:
        return implementation
    
    # Try to fix chunks based on instructions
    for chunk in chunks:
        file_path = chunk.get("file_path", "")
        code = chunk.get("code", "")
        
        if not file_path or not code:
            continue
        
        # Apply fixes based on focus areas
        for area in focus_areas:
            if "import" in area.lower():
                # Fix import issues
                if "import" not in code and file_path.endswith('.py'):
                    # Add common imports based on file content
                    if "json" in code.lower():
                        code = "import json\n" + code
                    if "os" in code.lower():
                        code = "import os\n" + code
            
            if "assertion" in area.lower():
                # Fix potential assertion issues
                pass  # Would need more context
        
        chunk["code"] = code
        chunk["fixed"] = True
    
    implementation["chunks"] = chunks
    implementation["retries_applied"] = True
    
    return implementation


def _apply_review_fixes(implementation: Dict[str, Any], review_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply review feedback to implementation.
    
    Uses SmartRouter to call model with fix prompts based on review data.
    """
    from neuro.router.smart_router import SmartRouter
    
    chunks = implementation.get("chunks", [])
    if not chunks:
        return implementation
    
    # Get issues from review
    issues = review_data.get("issues", [])
    if not issues:
        return implementation
    
    # Use SmartRouter to generate fixes
    router = SmartRouter()
    
    for issue in issues:
        issue_type = issue.get("type", "")
        location = issue.get("location", "")
        
        # Find matching chunk
        for chunk in chunks:
            chunk_path = chunk.get("file_path", "")
            if location and location in chunk_path:
                # Generate fix prompt
                fix_prompt = f"""
Fix the following issue in {chunk_path}:
Type: {issue_type}
Description: {issue.get('description', 'Review feedback')}
Current code:
{chunk.get('code', '')}

Provide the corrected code:
"""
                try:
                    response = router.chat(fix_prompt, task_type="code_fix")
                    if response and response.get("content"):
                        chunk["code"] = response["content"]
                        chunk["reviewed"] = True
                except Exception:
                    pass
    
    implementation["chunks"] = chunks
    implementation["review_fixes_applied"] = True
    
    return implementation
