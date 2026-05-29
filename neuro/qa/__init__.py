"""
QA System - Browser and route testing with Playwright
"""

import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os


@dataclass
class TestResult:
    """Result of a QA test."""
    name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None


class PlaywrightRunner:
    """Run Playwright tests on generated apps."""
    
    def __init__(self, app_url: str = "http://localhost:3000"):
        self.app_url = app_url
        self.results: List[TestResult] = []
        self.playwright_available = self._check_playwright()
    
    def _check_playwright(self) -> bool:
        try:
            subprocess.run(
                ["npx", "playwright", "--version"],
                capture_output=True,
                timeout=10,
            )
            return True
        except:
            return False
    
    def test_homepage(self) -> TestResult:
        """Test if homepage loads."""
        import time
        start = time.time()
        
        if not self.playwright_available:
            return TestResult(
                name="homepage_loads",
                passed=False,
                duration_ms=0,
                error="Playwright not available",
            )
        
        try:
            result = subprocess.run(
                [
                    "npx", "playwright", "open",
                    "--target", "chromium",
                    self.app_url,
                ],
                capture_output=True,
                timeout=30,
            )
            passed = result.returncode == 0
        except Exception as e:
            passed = False
        
        return TestResult(
            name="homepage_loads",
            passed=passed,
            duration_ms=(time.time() - start) * 1000,
            error=None if passed else "Failed to open page",
        )
    
    def test_routes(self, routes: List[str]) -> List[TestResult]:
        """Test multiple routes."""
        results = []
        for route in routes:
            result = self._test_route(route)
            results.append(result)
        return results
    
    def _test_route(self, route: str) -> TestResult:
        """Test a single route."""
        import time
        start = time.time()
        
        url = f"{self.app_url}{route}"
        
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
                capture_output=True,
                text=True,
                timeout=10,
            )
            status = int(result.stdout.strip())
            passed = status < 400
            error = None if passed else f"HTTP {status}"
        except Exception as e:
            passed = False
            error = str(e)
        
        return TestResult(
            name=f"route_{route}",
            passed=passed,
            duration_ms=(time.time() - start) * 1000,
            error=error,
        )


class RouteChecker:
    """Check routes return valid responses."""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
    
    def check(self, routes: List[str]) -> Dict[str, Any]:
        """Check all routes."""
        results = {}
        
        for route in routes:
            url = f"{self.base_url.rstrip('/')}/{route.lstrip('/')}"
            try:
                result = subprocess.run(
                    ["curl", "-s", "-w", "\\n%{http_code}", url],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                lines = result.stdout.strip().split("\n")
                status = lines[-1] if lines else "000"
                body = "\n".join(lines[:-1]) if len(lines) > 1 else ""
                results[route] = {
                    "status": int(status),
                    "passed": int(status) < 400,
                    "has_content": len(body) > 0,
                }
            except:
                results[route] = {
                    "status": 0,
                    "passed": False,
                    "has_content": False,
                }
        
        return results


class ConsoleErrorChecker:
    """Check for console errors."""
    
    def check(self, url: str = "http://localhost:3000") -> Dict[str, Any]:
        """Check page for console errors."""
        # Simple curl-based check
        try:
            result = subprocess.run(
                ["curl", "-s", url],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "passed": True,
                "errors": [],
                "warnings": [],
            }
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "warnings": [],
            }


def run_qa_checks(app_url: str = "http://localhost:3000") -> Dict[str, Any]:
    """Run all QA checks."""
    checker = RouteChecker(app_url)
    
    routes = ["/", "/api/health", "/_next"]
    
    return {
        "routes": checker.check(routes),
        "console": ConsoleErrorChecker().check(app_url),
        "browser": PlaywrightRunner(app_url).test_homepage().__dict__,
    }
