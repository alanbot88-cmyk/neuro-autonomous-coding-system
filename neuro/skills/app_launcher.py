# App Launcher - Start Servers, Run Apps, Launch Websites
# Automatically detects and launches different types of applications

import subprocess
import time
import os
import signal
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

@dataclass
class AppConfig:
    """Configuration for an app launch."""
    path: str
    app_type: str  # react, next, vue, express, fastapi, html, etc.
    port: int = 3000
    host: str = "localhost"
    build_command: Optional[str] = None
    start_command: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)

@dataclass
class LaunchResult:
    """Result of app launch."""
    success: bool
    app_type: str
    url: str
    port: int
    message: str
    startup_duration_ms: float
    process_id: Optional[int] = None
    build_output: str = ""
    error: Optional[str] = None

class AppLauncher:
    """
    Automatically detect and launch apps, servers, and websites.
    
    Usage:
        from neuro.skills.app_launcher import AppLauncher
        
        launcher = AppLauncher()
        result = launcher.launch("/path/to/app")
    """
    
    # Known app types and their configurations
    APP_TYPES = {
        "react": {
            "build_cmd": "npm run build",
            "start_cmd": "npm start",
            "dev_cmd": "npm run dev",
            "port": 3000,
            "dev_port": 5173,
        },
        "next": {
            "build_cmd": "npm run build",
            "start_cmd": "npm start",
            "dev_cmd": "npm run dev",
            "port": 3000,
        },
        "vue": {
            "build_cmd": "npm run build",
            "start_cmd": "npm run preview",
            "dev_cmd": "npm run dev",
            "port": 5173,
        },
        "express": {
            "start_cmd": "node index.js",
            "dev_cmd": "nodemon index.js",
            "port": 3000,
        },
        "fastapi": {
            "start_cmd": "uvicorn main:app --reload",
            "port": 8000,
        },
        "flask": {
            "start_cmd": "flask run",
            "port": 5000,
        },
        "django": {
            "start_cmd": "python manage.py runserver",
            "port": 8000,
        },
        "html": {
            "serve_cmd": "python -m http.server {port}",
            "port": 8080,
        },
        "static": {
            "serve_cmd": "npx serve -p {port}",
            "port": 3000,
        },
    }
    
    def __init__(self):
        self.running_processes: Dict[int, subprocess.Popen] = {}
    
    def detect_app_type(self, app_path: str) -> str:
        """
        Auto-detect app type from project structure.
        
        Returns:
            App type string (react, next, vue, express, fastapi, html, etc.)
        """
        path = Path(app_path)
        
        # Check package.json for clues
        package_json = path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                    deps = pkg.get("dependencies", {})
                    scripts = pkg.get("scripts", {})
                    
                    # Check for frameworks
                    if "next" in deps:
                        return "next"
                    if "react" in deps:
                        return "react"
                    if "vue" in deps:
                        return "vue"
                    if "express" in deps:
                        return "express"
                    
                    # Check scripts
                    if "dev" in scripts or "start" in scripts:
                        if "react" in str(deps) or "react-scripts" in deps:
                            return "react"
                        if "nuxt" in deps:
                            return "nuxt"
            except:
                pass
        
        # Check for Python frameworks
        if (path / "main.py").exists() or (path / "app.py").exists():
            requirements = path / "requirements.txt"
            if requirements.exists():
                reqs = requirements.read_text().lower()
                if "fastapi" in reqs:
                    return "fastapi"
                if "flask" in reqs:
                    return "flask"
                if "django" in reqs:
                    return "django"
            return "fastapi"
        
        # Check for Go apps
        if (path / "main.go").exists():
            return "golang"
        
        # Check for static HTML
        if (path / "index.html").exists():
            return "html"
        
        # Check for Java/Maven
        if (path / "pom.xml").exists() or (path / "build.gradle").exists():
            return "java"
        
        return "unknown"
    
    def launch(self, app_path: str, mode: str = "dev",
               port: int = None, build_first: bool = True) -> LaunchResult:
        """
        Launch an app/server.
        
        Args:
            app_path: Path to app directory
            mode: "dev", "build", or "start" (for production)
            port: Specific port to use (auto-detect if None)
            build_first: Whether to build before running
            
        Returns:
            LaunchResult with status and URL
        """
        start_time = time.time()
        
        # Detect app type
        app_type = self.detect_app_type(app_path)
        print(f"   Detected app type: {app_type}")
        
        if app_type == "unknown":
            return LaunchResult(
                success=False,
                app_type="unknown",
                url="",
                port=0,
                error=f"Could not detect app type in {app_path}"
            )
        
        # Get app configuration
        config = self.APP_TYPES.get(app_type, {})
        if not config:
            return LaunchResult(
                success=False,
                app_type=app_type,
                url="",
                port=0,
                error=f"No configuration for app type: {app_type}"
            )
        
        # Determine port
        if port is None:
            port = config.get("port", 3000)
        
        # Build first if requested
        build_output = ""
        if build_first and "build_cmd" in config:
            print(f"   Building app...")
            build_result = self._run_command(
                config["build_cmd"],
                app_path,
                timeout=300
            )
            build_output = build_result.get("stdout", "")
            
            if not build_result.get("success"):
                return LaunchResult(
                    success=False,
                    app_type=app_type,
                    url="",
                    port=port,
                    build_output=build_output,
                    error=f"Build failed: {build_result.get('error')}",
                    startup_duration_ms=(time.time() - start_time) * 1000
                )
            print(f"   Build completed")
        
        # Determine start command
        if mode == "dev":
            cmd_key = "dev_cmd"
        elif mode == "start":
            cmd_key = "start_cmd"
        else:
            cmd_key = "start_cmd"
        
        start_cmd = config.get(cmd_key, config.get("start_cmd"))
        if not start_cmd:
            return LaunchResult(
                success=False,
                app_type=app_type,
                url="",
                port=port,
                error=f"No start command found for {app_type}"
            )
        
        # Replace placeholders
        start_cmd = start_cmd.replace("{port}", str(port))
        
        print(f"   Starting: {start_cmd}")
        
        # Start the process
        process = self._start_process(
            start_cmd,
            app_path,
            port=port,
            env=config.get("env", {})
        )
        
        if process:
            # Wait for server to be ready
            ready = self._wait_for_server(port, timeout=60)
            host = config.get("host", "localhost")
            
            url = f"http://{host}:{port}"
            
            return LaunchResult(
                success=True,
                app_type=app_type,
                url=url,
                port=port,
                process_id=process.pid,
                message=f"App launched at {url}",
                startup_duration_ms=(time.time() - start_time) * 1000,
                build_output=build_output
            )
        else:
            return LaunchResult(
                success=False,
                app_type=app_type,
                url="",
                port=port,
                error="Failed to start process",
                startup_duration_ms=(time.time() - start_time) * 1000
            )
    
    def _run_command(self, command: str, cwd: str, 
                    timeout: int = 120) -> Dict:
        """Run a command and return result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "error": str(e)
            }
    
    def _start_process(self, command: str, cwd: str,
                      port: int, env: Dict = None) -> Optional[subprocess.Popen]:
        """Start a background process."""
        try:
            env = env or {}
            full_env = {**os.environ, **env}
            
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                env=full_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            self.running_processes[process.pid] = process
            return process
            
        except Exception as e:
            print(f"Failed to start process: {e}")
            return None
    
    def _wait_for_server(self, port: int, timeout: int = 60) -> bool:
        """Wait for server to be ready."""
        import socket
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                
                if result == 0:
                    print(f"   Server ready on port {port}")
                    return True
            except:
                pass
            
            time.sleep(1)
        
        print(f"   Server not responding on port {port}")
        return False
    
    def stop(self, process_id: int = None) -> bool:
        """Stop a running app."""
        if process_id and process_id in self.running_processes:
            try:
                process = self.running_processes[process_id]
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                del self.running_processes[process_id]
                return True
            except:
                pass
        
        return False
    
    def stop_all(self):
        """Stop all running apps."""
        for pid in list(self.running_processes.keys()):
            self.stop(pid)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all running apps."""
        status = []
        for pid, proc in self.running_processes.items():
            poll = proc.poll()
            status.append({
                "pid": pid,
                "running": poll is None,
                "return_code": poll
            })
        return {"running_apps": status, "count": len(status)}


def launch_app(app_path: str, mode: str = "dev",
                port: int = None) -> Dict[str, Any]:
    """
    Quick app launcher.
    
    Usage:
        from neuro.skills.app_launcher import launch_app
        
        result = launch_app("/path/to/app", port=3000)
        print(f"URL: {result['url']}")
        print(f"Success: {result['success']}")
    """
    launcher = AppLauncher()
    result = launcher.launch(app_path, mode=mode, port=port)
    
    return {
        "success": result.success,
        "app_type": result.app_type,
        "url": result.url,
        "port": result.port,
        "process_id": result.process_id,
        "message": result.message,
        "duration_ms": result.startup_duration_ms,
        "error": result.error
    }


def stop_app(process_id: int):
    """Stop a running app."""
    launcher = AppLauncher()
    return launcher.stop(process_id)


# SKILL.md content
SKILL_MD = """
---
name: app-launcher
description: Automatically detect and launch apps, servers, and websites
triggers:
  - launch
  - start
  - run
  - server
  - app
  - serve
---

# App Launcher

Automatically detects and launches apps, servers, and websites.

## Supported App Types

| Type | Command | Port |
|------|---------|------|
| React | npm run dev | 5173 |
| Next.js | npm run dev | 3000 |
| Vue | npm run dev | 5173 |
| Express | node index.js | 3000 |
| FastAPI | uvicorn main:app | 8000 |
| Flask | flask run | 5000 |
| Django | python manage.py runserver | 8000 |
| HTML | python -m http.server | 8080 |

## Usage

```python
from neuro.skills.app_launcher import AppLauncher, launch_app

# Quick launch
result = launch_app("/path/to/app", port=3000)
print(f"URL: {result['url']}")

# Custom launcher
launcher = AppLauncher()
result = launcher.launch("/path/to/app", mode="dev", port=8080)

# Check status
status = launcher.get_status()
print(f"Running apps: {status['count']}")

# Stop app
launcher.stop(process_id=result['process_id'])
```

## Auto-Detection

The launcher automatically detects:
- React/Next.js/Vue from package.json
- FastAPI/Flask/Django from Python files
- Static HTML files
- Go applications

## Flow

1. Detect app type
2. Build (if needed)
3. Start server
4. Wait for ready
5. Return URL
"""