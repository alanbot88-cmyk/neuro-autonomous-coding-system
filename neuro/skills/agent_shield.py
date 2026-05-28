# AgentShield Security Scanner Skill
# Integration with ECC's AgentShield for vulnerability detection
# Scans Neuro configurations, hooks, and MCP servers

import os
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SecurityFinding:
    """A security vulnerability finding."""
    severity: str  # "critical", "high", "medium", "low", "info"
    category: str
    file: str
    line: Optional[int]
    description: str
    recommendation: str
    test_id: Optional[str] = None

class AgentShieldSkill:
    """
    Security scanning skill for Neuro.
    Integrates with ECC's AgentShield (1,282 tests, 102 rules).
    
    Usage:
        from neuro.skills.agent_shield import AgentShieldSkill
        
        scanner = AgentShieldSkill()
        findings = scanner.scan_directory(".")
        report = scanner.generate_report(findings)
    """
    
    # Built-in vulnerability patterns (fallback if AgentShield CLI unavailable)
    VULNERABILITY_PATTERNS = {
        "api_key_exposure": {
            "severity": "critical",
            "patterns": [
                r'api_key\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']',  # Hardcoded key
                r'API_KEY\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']',
                r'sk-[A-Za-z0-9]{20,}',  # OpenAI style
                r'ghp_[A-Za-z0-9]{36}',  # GitHub token
                r'gsk_[A-Za-z0-9_-]{48}',  # Groq key
                r'sk-or-v1-[A-Za-z0-9_-]{48}',  # OpenRouter key
            ],
            "category": "key_leakage",
            "description": "Hardcoded API key detected",
            "recommendation": "Use environment variables: os.getenv('API_KEY')"
        },
        "command_injection": {
            "severity": "high",
            "patterns": [
                r'subprocess\.\w+\(.*["\'];\s*\w',  # Shell injection
                r'os\.system\(.*\+',  # String concatenation
                r'eval\(',  # eval usage
                r'exec\(',  # exec usage
            ],
            "category": "injection",
            "description": "Potential command injection vulnerability",
            "recommendation": "Use subprocess.run with list args, avoid shell=True"
        },
        "sql_injection": {
            "severity": "high",
            "patterns": [
                r'execute\([^)]+',  # String concatenation in SQL
                r'cursor\.execute\([^)]+%',  # % formatting
                r'f"SELECT.*{',  # f-string in SQL
            ],
            "category": "injection",
            "description": "Potential SQL injection vulnerability",
            "recommendation": "Use parameterized queries"
        },
        "path_traversal": {
            "severity": "medium",
            "patterns": [
                r'open\([^)]+',  # Path concatenation
                r'Path\([^)]+',  # Pathlib concatenation
                r'\.\./',  # Directory traversal
            ],
            "category": "path_security",
            "description": "Potential path traversal vulnerability",
            "recommendation": "Use os.path.join with sanitized input, validate paths"
        },
        "yaml_deserialization": {
            "severity": "high",
            "patterns": [
                r'yaml\.load\([^)]*\)',  # Unsafe yaml load
                r'yaml\.unsafe_load',  # Explicit unsafe
            ],
            "category": "deserialization",
            "description": "Unsafe YAML deserialization (CVE-2020-14343)",
            "recommendation": "Use yaml.safe_load()"
        },
        "pickle_deserialization": {
            "severity": "critical",
            "patterns": [
                r'pickle\.load\(',
                r'pickle\.loads\(',
                r'cloudpickle',
            ],
            "category": "deserialization",
            "description": "Pickle deserialization vulnerability",
            "recommendation": "Use JSON or safer serialization formats"
        },
        "mcp_tool_injection": {
            "severity": "medium",
            "patterns": [
                r'ToolUse.*tool_name.*\+',  # Dynamic tool name
                r'execute.*shell',  # Shell in MCP
            ],
            "category": "agent_security",
            "description": "Potential tool injection in agent configuration",
            "recommendation": "Validate tool names, avoid dynamic execution"
        },
        "weak_crypto": {
            "severity": "medium",
            "patterns": [
                r'md5',
                r'sha1',
                r'DES\.new\(',
                r'RC4',
            ],
            "category": "crypto",
            "description": "Weak cryptographic algorithm detected",
            "recommendation": "Use SHA-256, AES-256-GCM, or modern algorithms"
        },
        "insecure_random": {
            "severity": "low",
            "patterns": [
                r'random\.(random|randint|choice)',  # Not cryptographically secure
            ],
            "category": "crypto",
            "description": "Using non-cryptographic random for security purposes",
            "recommendation": "Use secrets.randbelow() or os.urandom()"
        },
        "debug_mode": {
            "severity": "info",
            "patterns": [
                r'debug\s*=\s*True',
                r'DEBUG\s*=\s*True',
                r'--debug',
            ],
            "category": "configuration",
            "description": "Debug mode enabled in production code",
            "recommendation": "Disable debug mode in production"
        },
        "hook_injection": {
            "severity": "critical",
            "patterns": [
                r'PostToolUse.*eval\(',
                r'PreToolUse.*exec\(',
                r'eval\(.*process\(',
            ],
            "category": "agent_security",
            "description": "Potential hook injection vulnerability",
            "recommendation": "Never use eval/exec in hooks, validate all inputs"
        },
    }
    
    def __init__(self):
        self.findings: List[SecurityFinding] = []
    
    def scan_file(self, file_path: str) -> List[SecurityFinding]:
        """Scan a single file for vulnerabilities."""
        findings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            for category, config in self.VULNERABILITY_PATTERNS.items():
                for pattern in config["patterns"]:
                    import re
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            findings.append(SecurityFinding(
                                severity=config["severity"],
                                category=config["category"],
                                file=file_path,
                                line=i,
                                description=config["description"],
                                recommendation=config["recommendation"]
                            ))
        
        except Exception as e:
            pass  # Skip unreadable files
        
        return findings
    
    def scan_directory(self, directory: str = ".") -> List[SecurityFinding]:
        """
        Scan entire directory for security issues.
        Focuses on Neuro's core files.
        """
        findings = []
        scan_paths = []
        
        # Focus on Neuro's Python files
        neuro_dir = Path(directory) / "neuro"
        if neuro_dir.exists():
            scan_paths.extend(neuro_dir.glob("**/*.py"))
        
        # Also scan config files
        scan_paths.extend(Path(directory).glob("*.json"))
        scan_paths.extend(Path(directory).glob("*.yaml"))
        scan_paths.extend(Path(directory).glob("*.yml"))
        
        for path in scan_paths:
            file_findings = self.scan_file(str(path))
            findings.extend(file_findings)
        
        self.findings = findings
        return findings
    
    def check_agent_config(self, config_path: str = ".agents/skills") -> List[SecurityFinding]:
        """Check agent configuration for security issues."""
        findings = []
        
        config_dir = Path(config_path)
        if not config_dir.exists():
            return findings
        
        # Check for hook injection in SKILL.md files
        for skill_file in config_dir.glob("**/SKILL.md"):
            try:
                content = skill_file.read_text()
                
                # Check for suspicious patterns
                import re
                
                # Eval/exec in skill content
                if re.search(r'eval\s*\(', content):
                    findings.append(SecurityFinding(
                        severity="critical",
                        category="skill_injection",
                        file=str(skill_file),
                        description="Eval detected in skill content",
                        recommendation="Remove eval from skill content"
                    ))
                
                # Dynamic import injection
                if re.search(r'import\s+\w+\s*\(\s*', content):
                    findings.append(SecurityFinding(
                        severity="high",
                        category="skill_injection",
                        file=str(skill_file),
                        description="Dynamic import in skill content",
                        recommendation="Use static imports only"
                    ))
                
                # Secret access patterns
                if re.search(r'secret|password|token', content, re.IGNORECASE):
                    if re.search(r'["\'].{20,}["\']', content):
                        findings.append(SecurityFinding(
                            severity="critical",
                            category="skill_secrets",
                            file=str(skill_file),
                            description="Potential hardcoded secret in skill",
                            recommendation="Use environment variables"
                        ))
            
            except Exception:
                pass
        
        return findings
    
    def check_mcp_security(self, mcp_config_path: str = ".mcp.json") -> List[SecurityFinding]:
        """Check MCP server configurations for security issues."""
        findings = []
        
        mcp_file = Path(mcp_config_path)
        if not mcp_file.exists():
            return findings
        
        try:
            with open(mcp_file) as f:
                config = json.load(f)
            
            # Check for dangerous tool permissions
            if "tools" in config:
                for tool in config["tools"]:
                    if tool.get("dangerous", False):
                        findings.append(SecurityFinding(
                            severity="high",
                            category="mcp_permissions",
                            file=mcp_config_path,
                            description=f"Tool '{tool.get('name')}' marked as dangerous",
                            recommendation="Review tool permissions, limit access"
                        ))
            
            # Check for shell execution tools
            if "tools" in config:
                shell_tools = ["bash", "shell", "exec", "run"]
                for tool in config["tools"]:
                    name = tool.get("name", "").lower()
                    if any(s in name for s in shell_tools):
                        findings.append(SecurityFinding(
                            severity="medium",
                            category="mcp_shell",
                            file=mcp_config_path,
                            description=f"Shell tool '{tool.get('name')}' in MCP config",
                            recommendation="Limit shell tool usage, add validation"
                        ))
        
        except Exception as e:
            pass
        
        return findings
    
    def run_agent_shield_cli(self) -> Optional[Dict]:
        """
        Run AgentShield CLI if available.
        Falls back to built-in patterns if not installed.
        """
        try:
            # Check if AgentShield CLI is available
            result = subprocess.run(
                ["npx", "ecc-agentshield", "scan", "--json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                # Fall back to built-in scanner
                return {"using_fallback": True}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"using_fallback": True}
    
    def generate_report(self, findings: List[SecurityFinding] = None) -> Dict[str, Any]:
        """Generate security report."""
        findings = findings or self.findings
        
        if not findings:
            return {
                "status": "clean",
                "summary": "No security vulnerabilities detected",
                "findings": []
            }
        
        # Group by severity
        by_severity = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        
        for f in findings:
            by_severity[f.severity].append(vars(f))
        
        # Calculate score (A-F grading like AgentShield)
        critical_count = len(by_severity["critical"])
        high_count = len(by_severity["high"])
        
        if critical_count > 0:
            grade = "F"
        elif high_count > 2:
            grade = "D"
        elif high_count > 0 or len(by_severity["medium"]) > 3:
            grade = "C"
        elif len(by_severity["medium"]) > 0 or len(by_severity["low"]) > 0:
            grade = "B"
        else:
            grade = "A"
        
        return {
            "status": "vulnerabilities_found",
            "grade": grade,
            "summary": f"{len(findings)} findings - {critical_count} critical, {high_count} high",
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "findings": findings,
            "recommendations": self._generate_recommendations(findings)
        }
    
    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []
        seen = set()
        
        # Prioritize critical recommendations
        sorted_findings = sorted(findings, key=lambda x: 
            {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}[x.severity]
        )
        
        for f in sorted_findings:
            if f.recommendation not in seen:
                recommendations.append(f"[{f.severity.upper()}] {f.description}: {f.recommendation}")
                seen.add(f.recommendation)
        
        return recommendations[:10]  # Top 10 recommendations


def run_security_scan(directory: str = ".") -> Dict[str, Any]:
    """
    Run complete security scan on Neuro system.
    Integrates with your existing validation pipeline.
    """
    scanner = AgentShieldSkill()
    
    # Scan Python files
    python_findings = scanner.scan_directory(directory)
    
    # Check agent configs
    agent_findings = scanner.check_agent_config()
    
    # Check MCP configs
    mcp_findings = scanner.check_mcp_security()
    
    # Combine findings
    all_findings = python_findings + agent_findings + mcp_findings
    
    # Generate report
    report = scanner.generate_report(all_findings)
    
    return report


# SKILL.md content
SKILL_MD = """
---
name: agent-shield
description: Security scanner for Neuro configurations and code
triggers:
  - security
  - scan
  - vulnerability
  - audit
  - agent-shield
---

# AgentShield Security Scanner

Security scanning skill for Neuro, inspired by ECC's AgentShield (1,282 tests, 102 rules).

## Capabilities

### 1. Vulnerability Detection
- API key exposure (hardcoded keys)
- Command injection
- SQL injection
- Path traversal
- YAML/Pickle deserialization
- MCP tool injection
- Hook injection
- Weak cryptography

### 2. Agent Configuration Security
- Skill file validation
- Hook safety checks
- Secret detection
- Dynamic import detection

### 3. MCP Server Security
- Tool permission auditing
- Shell execution checks
- Dangerous function detection

## Usage

```python
from neuro.skills.agent_shield import AgentShieldSkill, run_security_scan

# Quick scan
report = run_security_scan(".")

# Detailed scan
scanner = AgentShieldSkill()
scanner.scan_directory("neuro")
scanner.check_agent_config(".agents/skills")
scanner.check_mcp_security(".mcp.json")
report = scanner.generate_report()

# Check grade
print(f"Security Grade: {report['grade']}")
```

## Grading System

| Grade | Description |
|-------|-------------|
| A | No vulnerabilities |
| B | Minor issues only |
| C | Medium severity findings |
| D | Multiple high severity |
| F | Critical vulnerabilities |

## Integration with Neuro

Add to your validation pipeline:
```python
# After code generation
security_report = run_security_scan(".")
if security_report['grade'] not in ['A', 'B']:
    # Block deployment, show warnings
    pass
```
"""