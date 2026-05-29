"""
Self-Healing System - Auto-fix common errors
"""

import re
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ErrorFix:
    """A fix for a specific error."""
    pattern: str
    cause: str
    fix: str
    commands: List[str] = None


class ErrorClassifier:
    """Classify errors into categories."""
    
    PATTERNS = {
        "missing_package": r"(?:ImportError|ModuleNotFoundError)(?::|\s+)(.*?)(?:'|\")",
        "npm_install": r"(?:npm install|npm i|npm ci)",
        "python_install": r"(?:pip install|poetry add)",
        "port_conflict": r"(?:port|address|socket)(?:\s+is\s+)?(?:already|in\s+use|bind)",
        "env_missing": r"(?:environment|ENV|env)(?:\s+variable)?(?:.*?)(?:not found|missing|undefined)",
        "typescript_error": r"TS\d+:",
        "syntax_error": r"SyntaxError",
        "type_error": r"TypeError",
        "import_error": r"ImportError",
        "cors_error": r"CORS|cross-origin",
        "nextjs_error": r"(?:Next\.js|NextJS|getServerSideProps|app router)",
        "docker_error": r"(?:docker|container|podman)",
        "auth_error": r"(?:auth|jwt|token|cookie)",
    }
    
    def classify(self, error: str) -> str:
        """Classify error type."""
        for category, pattern in self.PATTERNS.items():
            if re.search(pattern, error, re.IGNORECASE):
                return category
        return "unknown"
    
    def get_fix_suggestions(self, error: str) -> List[str]:
        """Get fix suggestions for an error."""
        category = self.classify(error)
        suggestions = {
            "missing_package": [
                "Run: pip install <package>",
                "Check requirements.txt",
                "Verify virtual environment",
            ],
            "npm_install": [
                "Run: npm install",
                "Try: npm ci",
                "Clear cache: npm cache clean --force",
            ],
            "port_conflict": [
                "Find and kill process on port",
                "Change port in config",
                "Use: lsof -i :PORT",
            ],
            "env_missing": [
                "Create .env file",
                "Check .env.example",
                "Add required variables",
            ],
            "typescript_error": [
                "Run: npx tsc --noEmit",
                "Check type definitions",
                "Use @ts-ignore as last resort",
            ],
            "syntax_error": [
                "Check line number in error",
                "Verify Python/JS syntax",
                "Check for missing brackets",
            ],
            "unknown": [
                "Read error message carefully",
                "Search the error online",
                "Check recent code changes",
            ],
        }
        return suggestions.get(category, ["Unknown error type"])


class NPMErrorFixer:
    """Fix common npm/node errors."""
    
    def fix(self, error: str, cwd: str = ".") -> List[str]:
        """Attempt to fix npm errors."""
        fixes = []
        
        if "node_modules" in str(error) or "npm install" in str(error):
            fixes.append("npm install")
        
        if "@" in error:
            package = re.search(r"(@[\w-]+/[\w-]+)", error)
            if package:
                fixes.append(f"npm install {package.group(1)}")
        
        if "peer" in error.lower():
            fixes.append("npm install --legacy-peer-deps")
        
        return fixes


class PythonErrorFixer:
    """Fix common Python errors."""
    
    def fix(self, error: str, cwd: str = ".") -> List[str]:
        """Attempt to fix Python errors."""
        fixes = []
        
        # Missing package
        match = re.search(r"ModuleNotFoundError: No module named '(\w+)'", error)
        if match:
            fixes.append(f"pip install {match.group(1)}")
        
        # Syntax error
        if "SyntaxError" in error:
            fixes.append("Check syntax: python -m py_compile <file>")
        
        # Common fixes
        if "psycopg2" in error:
            fixes.append("pip install psycopg2-binary")
        if "sqlite3" in error:
            fixes.append("Python's sqlite3 is built-in - check import")
        
        return fixes


class PortResolver:
    """Resolve port conflicts."""
    
    def find_process(self, port: int) -> Optional[Dict[str, Any]]:
        """Find process using a port."""
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-P", "-n"],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    parts = lines[1].split()
                    return {
                        "pid": parts[1],
                        "command": parts[0],
                        "port": port,
                    }
        except:
            pass
        return None
    
    def kill_process(self, port: int) -> bool:
        """Kill process on port."""
        proc = self.find_process(port)
        if proc:
            try:
                subprocess.run(["kill", proc["pid"]])
                return True
            except:
                return False
        return False


class DependencyResolver:
    """Resolve missing dependencies."""
    
    def resolve(self, error: str, cwd: str = ".") -> Dict[str, Any]:
        """Try to resolve missing dependencies."""
        missing = re.findall(r"No module named '(\w+)'", error)
        
        results = {
            "pip_packages": [],
            "npm_packages": [],
            "commands": [],
        }
        
        for pkg in missing:
            if pkg.isascii():
                results["pip_packages"].append(pkg)
                results["commands"].append(f"pip install {pkg}")
        
        return results


def auto_fix(error: str, cwd: str = ".") -> Dict[str, Any]:
    """Try to auto-fix an error."""
    classifier = ErrorClassifier()
    category = classifier.classify(error)
    suggestions = classifier.get_fix_suggestions(error)
    
    return {
        "category": category,
        "suggestions": suggestions,
        "fix_commands": [],
    }
