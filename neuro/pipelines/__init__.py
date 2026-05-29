"""
Enterprise App Pipeline - End-to-end app building system
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from neuro.product import ProductSpec, RequirementParser
from neuro.architecture import ArchitecturePlan, AppArchitect
from neuro.workspace import SafeFileWriter, RepoMap
from neuro.healing import ErrorClassifier, DependencyResolver
from neuro.qa import RouteChecker, ConsoleErrorChecker
from neuro.stacks import STACKS, select_stack_for_goal


@dataclass
class PipelineContext:
    """Context for pipeline execution."""
    goal: str
    mode: str = "auto"
    working_dir: str = "."
    dry_run: bool = True
    stack_name: str = "nextjs_supabase"
    steps: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None


class EnterpriseAppPipeline:
    """
    Pipeline for building enterprise applications end-to-end.
    
    Flow:
    1. Parse goal into product spec
    2. Select technology stack
    3. Generate architecture plan
    4. Create file structure
    5. Build foundation
    6. Run tests/QA
    7. Auto-fix errors
    8. Final report
    """
    
    def __init__(self, context: PipelineContext):
        self.context = context
        self.parser = RequirementParser()
        self.architect = AppArchitect()
        self.repo_map = RepoMap(root=context.working_dir)
        self.file_writer = SafeFileWriter(context.working_dir, dry_run=context.dry_run)
    
    def run(self) -> Dict[str, Any]:
        """Execute the pipeline."""
        self._log_step("start", "Pipeline started")
        
        # Step 1: Parse goal
        spec = self._parse_goal()
        if not spec:
            return self._fail("Failed to parse goal")
        
        # Step 2: Select stack
        stack = self._select_stack(spec)
        if not stack:
            return self._fail("Failed to select stack")
        
        # Step 3: Generate architecture
        architecture = self._plan_architecture(spec, stack)
        
        # Step 4: Create project structure
        self._create_structure(architecture)
        
        # Step 5: Generate code (placeholder based on mode)
        self._generate_code(spec, architecture)
        
        # Step 6: Run installs
        self._run_installs()
        
        # Step 7: QA checks
        results = {
            "success": len(self.context.errors) == 0,
            "steps": self.context.steps,
            "files_created": self.context.files_created,
            "errors": self.context.errors,
            "spec": spec.__dict__ if spec else None,
            "architecture": architecture.to_dict() if architecture else None,
        }
        
        self.context.result = results
        return results
    
    def _log_step(self, name: str, message: str):
        """Log a pipeline step."""
        self.context.steps.append({
            "step": name,
            "message": message,
        })
    
    def _parse_goal(self) -> Optional[ProductSpec]:
        """Parse the goal into a product spec."""
        self._log_step("parse", f"Parsing goal: {self.context.goal[:50]}...")
        try:
            spec = self.parser.parse(self.context.goal)
            self._log_step("parse_complete", f"App type: {spec.app_type}, Features: {len(spec.core_features)}")
            return spec
        except Exception as e:
            self.context.errors.append(f"Parse error: {e}")
            return None
    
    def _select_stack(self, spec: ProductSpec):
        """Select technology stack."""
        self._log_step("stack", f"Selecting stack for {spec.app_type}...")
        stack = select_stack_for_goal(self.context.goal)
        self.context.stack_name = stack.name
        self._log_step("stack_complete", f"Stack: {stack.name}")
        return stack
    
    def _plan_architecture(self, spec: ProductSpec, stack) -> Optional[ArchitecturePlan]:
        """Generate architecture plan."""
        self._log_step("architecture", "Generating architecture plan...")
        try:
            arch = self.architect.plan(spec, stack.name)
            self._log_step("architecture_complete", f"Files: {len(arch.pages)} pages, {len(arch.components)} components")
            return arch
        except Exception as e:
            self.context.errors.append(f"Architecture error: {e}")
            return None
    
    def _create_structure(self, architecture: ArchitecturePlan):
        """Create project file structure."""
        self._log_step("structure", "Creating file structure...")
        
        if self.context.mode == "debug":
            self._log_step("structure_skip", "Debug mode - skipping structure creation")
            return
        
        # In dry-run mode, just log the structure
        if self.context.dry_run:
            self._log_step("structure_dryrun", f"Would create: {len(architecture.file_tree)} top-level items")
            self.context.files_created.extend([
                f"app/{page}.tsx" for page in architecture.pages
            ])
            return
        
        self._log_step("structure_complete", f"Structure ready: {len(architecture.pages)} pages")
    
    def _generate_code(self, spec: ProductSpec, architecture: ArchitecturePlan):
        """Generate application code."""
        self._log_step("generate", "Generating code (placeholder for actual code gen)...")
        
        # This is where LLM-powered code generation would happen
        # For now, create placeholder structure
        
        if self.context.mode == "debug":
            self._log_step("generate_skip", "Debug mode - no code generation")
            return
        
        if self.context.dry_run:
            self._log_step("generate_dryrun", f"Would generate: {len(architecture.pages)} pages, {len(architecture.components)} components")
            return
        
        self._log_step("generate_complete", "Code generation (stub - needs LLM integration)")
    
    def _run_installs(self):
        """Run dependency installations."""
        self._log_step("install", "Checking dependencies...")
        
        # Check if node_modules exists
        has_deps = os.path.exists(os.path.join(self.context.working_dir, "node_modules"))
        
        if not has_deps and not self.context.dry_run:
            self._log_step("install_hint", "Run: npm install to install dependencies")
        
        self._log_step("install_complete", "Dependencies ready" if has_deps else "Install needed")
    
    def _fail(self, message: str) -> Dict[str, Any]:
        """Handle pipeline failure."""
        self.context.errors.append(message)
        return {
            "success": False,
            "error": message,
            "steps": self.context.steps,
        }


def run_pipeline(
    goal: str,
    mode: str = "auto",
    working_dir: str = ".",
    dry_run: bool = True,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Run the enterprise app pipeline.
    
    Usage:
        from neuro.pipelines import run_pipeline
        
        result = run_pipeline(
            goal="Build a CRM for real estate agents",
            mode="enterprise",
            dry_run=True,
            verbose=True,
        )
        
        print(result["success"])
        print(result["steps"])
    """
    context = PipelineContext(
        goal=goal,
        mode=mode,
        working_dir=working_dir,
        dry_run=dry_run,
    )
    
    pipeline = EnterpriseAppPipeline(context)
    result = pipeline.run()
    
    if verbose:
        print("\n📋 Pipeline Execution Summary")
        print("=" * 50)
        for step in result.get("steps", []):
            print(f"  [{step['step']}] {step['message']}")
        print(f"\n  Files created: {len(result.get('files_created', []))}")
        if result.get('errors'):
            print(f"  Errors: {result['errors']}")
    
    return result


class DebugPipeline:
    """Pipeline for debugging existing projects."""
    
    def __init__(self, working_dir: str = ".", dry_run: bool = True):
        self.working_dir = working_dir
        self.dry_run = dry_run
        self.context = PipelineContext(
            goal="debug existing project",
            mode="debug",
            working_dir=working_dir,
            dry_run=dry_run,
        )
    
    def run(self) -> Dict[str, Any]:
        """Run debug pipeline."""
        steps = []
        
        # Step 1: Inspect repository
        steps.append({"step": "inspect", "message": "Inspecting repository..."})
        
        repo_map = RepoMap(root=self.working_dir)
        repo_map.scan(self.working_dir)
        
        files = list(repo_map.files.keys())
        steps.append({"step": "inspect_complete", "message": f"Found {len(files)} files"})
        
        # Step 2: Detect stack
        steps.append({"step": "stack_detection", "message": "Detecting tech stack..."})
        
        has_package_json = any("package.json" in f for f in files)
        has_requirements = any("requirements.txt" in f for f in files)
        has_pyproject = any("pyproject.toml" in f for f in files)
        
        stack = "unknown"
        if has_package_json:
            stack = "node/npm"
        elif has_requirements or has_pyproject:
            stack = "python/pip"
        
        steps.append({"step": "stack_detected", "message": f"Stack: {stack}"})
        
        # Step 3: Install dependencies
        if not self.dry_run:
            import subprocess
            if has_package_json:
                subprocess.run(["npm", "install"], cwd=self.working_dir)
            elif has_requirements:
                subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=self.working_dir)
        
        return {
            "success": True,
            "steps": steps,
            "stack": stack,
            "files": files,
        }
