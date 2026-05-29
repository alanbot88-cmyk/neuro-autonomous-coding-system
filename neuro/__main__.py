"""
Neuro CLI - Command-line interface for the Neuro Autonomous Agent
Usage: python -m neuro --goal "task description"

Shows full agent loop with all 4 roles visible:
  - Planner: Breaks down tasks
  - Coder: Implements solutions
  - Reviewer: Checks quality
  - Executor: Runs and tests
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from neuro.executor.agent_loop import create_agent, run_goal


def main():
    parser = argparse.ArgumentParser(
        description="Neuro Autonomous Agent - Enterprise App Builder System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m neuro --goal "Build a CRM for real estate agents"
  python -m neuro --mode enterprise --goal "Build a SaaS app"
  python -m neuro --mode debug --goal "Fix this app until it runs"
  python -m neuro --mode website --goal "Create a landing page"
  python -m neuro --dry-run -v
  
  # With scenario routing
  python -m neuro --scenario bug_fix --goal "Fix the login error"
  python -m neuro --scenario web_app --goal "Build a dashboard"
  
  # With parallel execution
  python -m neuro --max-steps 100 --goal "Build full-stack app"
  python -m neuro --no-parallel --goal "Sequential build"
  
Working Modes:
  auto        - Auto-detect mode from goal
  enterprise - Build full SaaS applications
  website    - Build landing pages
  debug      - Fix existing broken projects
  presentation - Build presentations
  api        - Build API services
  refactor   - Refactor existing code
  deploy     - Deploy applications

Scenario Handlers:
  bug_fix       - diagnose-fix-verify approach
  new_feature   - plan-implement-test approach
  refactor      - analyze-plan-execute-verify approach
  web_app       - design-backend-frontend-integrate-test approach
  api_build     - design-schema-implement-document approach
  data_pipeline - analyze-design-implement-validate approach
  code_review   - analyze-identify-suggest approach
  research_task - gather-analyze-summarize approach
  long_horizon  - milestone-track-iterate approach
  enterprise_app - architecture-design-implement-test-deploy approach
  mobile_app    - design-implement-test-package approach
  presentation  - outline-design-build-refine approach

Environment Variables:
  GROQ_API_KEYS - Groq API key (free tier)
  OPENROUTER_API_KEYS - OpenRouter API key (free tier)
  HF_TOKEN - HuggingFace token
        """
    )
    
    parser.add_argument(
        "-g", "--goal",
        default=None,
        help="Task goal to accomplish (required unless using --version, --health, or --stats)"
    )
    
    parser.add_argument(
        "-d", "--working-dir",
        default=".",
        help="Working directory (default: current directory)"
    )
    
    parser.add_argument(
        "--max-steps",
        type=int,
        default=50,
        help="Maximum agent steps (default: 50)"
    )
    
    parser.add_argument(
        "--max-passes",
        type=int,
        default=4,
        help="Maximum thinking passes (default: 4)"
    )
    
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use (e.g., groq/llama-3.3-70b-versatile)"
    )
    
    parser.add_argument(
        "--provider",
        default=None,
        help="Preferred provider (groq, openrouter, huggingface, etc.)"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Model temperature (default: 0.1)"
    )
    
    # =========================================================================
    # NEW SECTION 10 FLAGS
    # =========================================================================
    
    parser.add_argument(
        "--scenario",
        default=None,
        choices=[
            "bug_fix", "new_feature", "refactor", "web_app", "api_build",
            "data_pipeline", "code_review", "research_task", "long_horizon",
            "enterprise_app", "mobile_app", "presentation"
        ],
        help="Force specific scenario handler (skip auto-detection)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Show plan without executing"
    )
    
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel execution"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all agent communications"
    )
    
    parser.add_argument(
        "--json-output",
        metavar="FILE",
        help="Save results to JSON file"
    )
    
    # =========================================================================
    # EXISTING FLAGS (preserved for compatibility)
    # =========================================================================
    
    parser.add_argument(
        "--no-test-first",
        action="store_true",
        help="Disable test-first validation"
    )
    
    parser.add_argument(
        "--no-cot",
        action="store_true",
        help="Disable chain-of-thought prompting"
    )
    
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable memory system"
    )
    
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply changes (disables dry-run)"
    )
    
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm before applying changes"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version"
    )
    
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check API provider health"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show router statistics"
    )
    
    parser.add_argument(
        "--mode",
        default="auto",
        choices=["auto", "enterprise", "website", "debug", "presentation", "api", "refactor", "deploy"],
        help="Operation mode (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Version
    if args.version:
        print("Neuro Autonomous Agent v2.0.0")
        print("Target: Enterprise App Builder")
        print("Modes: enterprise, website, debug, deploy, etc.")
        print("Scenarios: bug_fix, web_app, api_build, etc.")
        print("Using free API providers")
        return 0
    
    # Health check
    if args.health:
        from neuro.router import available_providers
        providers = available_providers()
        print("API Provider Health:")
        for provider, count in providers.items():
            status = "✓" if count > 0 else "✗"
            print(f"  {provider}: {status} ({count} keys)")
        return 0
    
    # Stats
    if args.stats:
        from neuro.router import available_providers
        providers = available_providers()
        print("Router Statistics:")
        for provider, count in providers.items():
            print(f"  {provider}: {count} key(s)")
        return 0
    
    # Check for API keys
    has_keys = any([
        os.getenv("GROQ_API_KEYS"),
        os.getenv("OPENROUTER_API_KEYS"),
        os.getenv("HF_TOKEN"),
        os.getenv("TOGETHER_API_KEY"),
    ])
    
    if not has_keys:
        print("⚠️  Warning: No API keys found!", file=sys.stderr)
        print("Set at least one of:", file=sys.stderr)
        print("  GROQ_API_KEYS", file=sys.stderr)
        print("  OPENROUTER_API_KEYS", file=sys.stderr)
        print("  HF_TOKEN", file=sys.stderr)
        print("", file=sys.stderr)
        print("Get free keys:")
        print("  Groq: https://console.groq.com/keys", file=sys.stderr)
        print("  OpenRouter: https://openrouter.ai/keys", file=sys.stderr)
        print("  HuggingFace: https://huggingface.co/settings/inference-tokens", file=sys.stderr)
    
    # Determine dry_run mode
    if args.apply:
        dry_run = False
    elif args.dry_run is not None:
        dry_run = args.dry_run
    else:
        dry_run = True  # Default to dry-run
    
    # Show startup info
    if args.verbose or args.goal:
        print()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          NEURO AUTONOMOUS AGENT v2.0.0                   ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print(f"║ Goal: {args.goal[:50]}{'...' if args.goal and len(args.goal) > 50 else '':<52}║")
        print(f"║ Working Dir: {args.working_dir:<48}║")
        print(f"║ Max Steps: {args.max_steps:<48}║")
        print(f"║ Dry Run: {str(dry_run):<48}║")
        if args.scenario:
            print(f"║ Scenario: {args.scenario:<47}║")
        if args.no_parallel:
            print(f"║ Parallel: DISABLED                                      ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║  4-ROLE AGENT LOOP                                       ║")
        print("║  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        ║")
        print("║  │PLANNER  │→│ CODER   │→│REVIEWER │→│EXECUTOR │        ║")
        print("║  │ Analyze │ │Implement│ │Quality  │ │Run &    │        ║")
        print("║  │ Break   │ │Code     │ │Check    │ │Test     │        ║")
        print("║  └─────────┘ └─────────┘ └─────────┘ └─────────┘        ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
    
    # Show scenario routing info if specified
    if args.scenario:
        try:
            from neuro.router.scenario_router import ScenarioRouter, ScenarioType
            router = ScenarioRouter()
            scenario = ScenarioType(args.scenario)
            handler = router.get_handler(scenario)
            print(f"📋 Scenario: {args.scenario}")
            print(f"   Approach: {handler.approach}")
            print(f"   Tools: {', '.join(handler.tools)}")
            print(f"   Primary Model: {handler.model_primary}")
            print()
        except Exception as e:
            print(f"⚠️  Scenario routing error: {e}")
            print()
    
    # Show dry-run notice
    if dry_run:
        print("🔍 DRY-RUN MODE: Showing plan without executing")
        print()
    
    try:
        agent = create_agent(
            goal=args.goal,
            working_dir=args.working_dir,
            max_steps=args.max_steps,
            max_passes=args.max_passes,
            model=args.model,
            test_first=not args.no_test_first,
            use_cot=not args.no_cot,
            use_memory=not args.no_memory,
            dry_run=dry_run,
            verbose=args.verbose,
        )
        
        result = agent.run()
        
        # Output
        print()
        print("═" * 60)
        print("RESULT")
        print("═" * 60)
        print(f"Success: {result.success}")
        print(f"Status: {result.status}")
        print(f"Steps: {result.steps}")
        print(f"Passes: {result.passes_used}")
        print(f"Duration: {result.duration_ms/1000:.1f}s")
        
        if result.files_changed:
            print(f"Files changed: {', '.join(result.files_changed)}")
        
        if result.error:
            print(f"Error: {result.error}")
        
        if result.validation_passed:
            print("Validation: PASSED ✓")
        else:
            print("Validation: FAILED ✗")
        
        print("═" * 60)
        
        # JSON output
        if args.json_output:
            output = {
                "success": result.success,
                "status": result.status,
                "goal": result.goal,
                "steps": result.steps,
                "passes_used": result.passes_used,
                "duration_ms": result.duration_ms,
                "files_changed": result.files_changed,
                "validation_passed": result.validation_passed,
                "error": result.error,
                "model_used": result.model_used,
                "provider_used": result.provider_used,
                "test_results": result.test_results,
            }
            
            with open(args.json_output, 'w') as f:
                json.dump(output, f, indent=2)
            
            print(f"\n📄 JSON output saved: {args.json_output}")
        
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
