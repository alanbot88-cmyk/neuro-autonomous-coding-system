"""
Neuro CLI - Command-line interface for the Neuro Autonomous Agent
Usage: python -m neuro --goal "task description"
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
  python -m neuro --mode deploy --goal "Deploy to Vercel"
  python -m neuro --dry-run -v
  
Working Modes:
  auto        - Auto-detect mode from goal
  enterprise - Build full SaaS applications
  website    - Build landing pages
  debug      - Fix existing broken projects
  presentation - Build presentations
  api        - Build API services
  refactor   - Refactor existing code
  deploy     - Deploy applications
  
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
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without applying (default: True)"
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
        "--json-output",
        metavar="FILE",
        help="Output result as JSON to file"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
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
        print("Using free API providers")
        return 0
    
    # Health check
    if args.health:
        from neuro.router.smart_router import health_check
        health = health_check()
        print("API Provider Health:")
        for provider, status in health.items():
            key_status = "✓" if status["has_key"] else "✗"
            healthy = "✓" if status["available"] else "✗"
            cooldown = " (cooldown)" if status["in_cooldown"] else ""
            print(f"  {provider}: {healthy} available, {key_status} key {cooldown}")
        return 0
    
    # Stats
    if args.stats:
        from neuro.router.smart_router import get_stats
        stats = get_stats()
        print("Router Statistics:")
        print(f"  Total calls: {stats['total_calls']}")
        for provider, count in stats.get("provider_calls", {}).items():
            print(f"  {provider}: {count} calls")
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
    
    # Create and run agent
    dry_run = not args.apply
    
    if args.verbose:
        print(f"🚀 Neuro Agent")
        print(f"   Goal: {args.goal}")
        print(f"   Working dir: {args.working_dir}")
        print(f"   Dry run: {dry_run}")
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
        if args.verbose or not args.json_output:
            print()
            print("=" * 60)
            print("RESULT")
            print("=" * 60)
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
            
            print("=" * 60)
        
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
            
            if args.verbose:
                print(f"\n📄 JSON output: {args.json_output}")
        
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
