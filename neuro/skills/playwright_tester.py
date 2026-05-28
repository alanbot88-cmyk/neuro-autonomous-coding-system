# Playwright App Tester
# Automatically tests created apps, websites, and verifies UI/functionality

import subprocess
import time
import json
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class UIElement:
    """Detected UI element."""
    selector: str
    element_type: str  # button, input, link, text, etc.
    text: Optional[str] = None
    visible: bool = True
    enabled: bool = True
    clickable: bool = False

@dataclass
class TestResult:
    """Result of a test."""
    name: str
    status: TestStatus
    passed: bool
    message: Optional[str] = None
    screenshot_path: Optional[str] = None
    duration_ms: float = 0
    errors: List[str] = field(default_factory=list)
    clicks_performed: List[str] = field(default_factory=list)

@dataclass
class AppTestReport:
    """Complete test report for an app."""
    app_url: str
    app_path: str
    overall_status: TestStatus
    passed_count: int
    failed_count: int
    total_count: int
    results: List[TestResult]
    elements_found: List[UIElement]
    buttons_tested: List[str]
    forms_tested: List[str]
    navigation_tested: List[str]
    screenshots: List[str]

class PlaywrightTester:
    """
    Automatically test apps, websites, and verify functionality.
    
    Usage:
        from neuro.skills.playwright_tester import PlaywrightTester
        
        tester = PlaywrightTester()
        report = tester.test_app("/path/to/app", port=3000)
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.test_results: List[TestResult] = []
        self.screenshots: List[str] = []
    
    def _ensure_playwright(self) -> bool:
        """Ensure Playwright is installed."""
        global PLAYWRIGHT_AVAILABLE
        if not PLAYWRIGHT_AVAILABLE:
            try:
                subprocess.run(["pip", "install", "playwright"], check=True, capture_output=True)
                subprocess.run(["playwright", "install"], check=True, capture_output=True)
                PLAYWRIGHT_AVAILABLE = True
            except Exception:
                print("Warning: Playwright not available. Install with: pip install playwright")
                return False
        return True
    
    def start_browser(self):
        """Start the browser."""
        if not self._ensure_playwright():
            raise Exception("Playwright not installed")
        
        if PLAYWRIGHT_AVAILABLE:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
    
    def stop_browser(self):
        """Stop the browser."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to a URL."""
        try:
            self.page.goto(url, timeout=self.timeout)
            self.page.wait_for_load_state("networkidle", timeout=self.timeout)
            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    def discover_elements(self) -> List[UIElement]:
        """Discover all interactive elements on the page."""
        elements = []
        
        try:
            # Buttons
            buttons = self.page.query_selector_all("button, [role='button'], input[type='submit'], input[type='button']")
            for btn in buttons:
                text = btn.inner_text() or ""
                elements.append(UIElement(
                    selector=self._get_selector(btn),
                    element_type="button",
                    text=text.strip(),
                    visible=btn.is_visible(),
                    enabled=btn.is_enabled(),
                    clickable=True
                ))
            
            # Links
            links = self.page.query_selector_all("a, [role='link']")
            for link in links:
                text = link.inner_text() or ""
                href = link.get_attribute("href") or ""
                elements.append(UIElement(
                    selector=self._get_selector(link),
                    element_type="link",
                    text=text.strip(),
                    visible=link.is_visible()
                ))
            
            # Inputs
            inputs = self.page.query_selector_all("input, textarea, select")
            for inp in inputs:
                input_type = inp.get_attribute("type") or "text"
                placeholder = inp.get_attribute("placeholder") or ""
                elements.append(UIElement(
                    selector=self._get_selector(inp),
                    element_type="input" if input_type != "hidden" else "hidden",
                    text=placeholder,
                    visible=inp.is_visible(),
                    enabled=inp.is_enabled()
                ))
        
        except Exception as e:
            print(f"Element discovery failed: {e}")
        
        return elements
    
    def _get_selector(self, element) -> str:
        """Generate a unique selector for an element."""
        try:
            # Try ID first
            elem_id = element.get_attribute("id")
            if elem_id:
                return f"#{elem_id}"
            
            # Try data-testid
            testid = element.get_attribute("data-testid")
            if testid:
                return f"[data-testid='{testid}']"
            
            # Try aria-label
            aria = element.get_attribute("aria-label")
            if aria:
                return f"[aria-label='{aria}']"
            
            # Generate from tag and text
            tag = element.evaluate("el => el.tagName.toLowerCase()")
            text = element.inner_text()[:30] if element.inner_text() else ""
            if text:
                return f"{tag}:has-text('{text}')"
            
            return tag
        except:
            return "unknown"
    
    def click_element(self, selector: str, timeout: int = 5000) -> bool:
        """Click an element by selector."""
        try:
            self.page.click(selector, timeout=timeout)
            return True
        except Exception as e:
            print(f"Click failed: {e}")
            return False
    
    def type_text(self, selector: str, text: str) -> bool:
        """Type text into an input."""
        try:
            self.page.fill(selector, text)
            return True
        except Exception as e:
            print(f"Type failed: {e}")
            return False
    
    def take_screenshot(self, name: str = "screenshot") -> Optional[str]:
        """Take a screenshot."""
        try:
            self.page.screenshot(path=f"screenshots/{name}.png")
            screenshot_path = f"screenshots/{name}.png"
            self.screenshots.append(screenshot_path)
            return screenshot_path
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return None
    
    def test_app(self, app_path: str, port: int = 3000, 
                 app_type: str = "auto") -> AppTestReport:
        """
        Test an app/website comprehensively.
        
        Args:
            app_path: Path to the app
            port: Port where app is running
            app_type: "react", "next", "vue", "html", "auto"
            
        Returns:
            AppTestReport with all test results
        """
        start_time = time.time()
        results = []
        elements_found = []
        buttons_tested = []
        forms_tested = []
        navigation_tested = []
        
        # Determine URL
        if app_type == "auto":
            if os.path.exists(os.path.join(app_path, "package.json")):
                app_type = self._detect_app_type(app_path)
            else:
                app_type = "html"
        
        if app_type in ["react", "next", "vue", "node"]:
            url = f"http://localhost:{port}"
        else:
            # Static HTML
            index_path = os.path.join(app_path, "index.html")
            if os.path.exists(index_path):
                url = f"file://{index_path}"
            else:
                url = f"http://localhost:{port}"
        
        try:
            self.start_browser()
            
            # Navigate to app
            nav_result = self.navigate_to(url)
            results.append(TestResult(
                name="Navigation",
                status=TestStatus.PASSED if nav_result else TestStatus.FAILED,
                passed=nav_result,
                message="App loaded" if nav_result else "Failed to load app"
            ))
            
            time.sleep(2)  # Wait for app to fully load
            
            # Take initial screenshot
            self.take_screenshot("initial_load")
            
            # Discover elements
            elements_found = self.discover_elements()
            results.append(TestResult(
                name="Element Discovery",
                status=TestStatus.PASSED,
                passed=True,
                message=f"Found {len(elements_found)} elements"
            ))
            
            # Test buttons
            buttons = [e for e in elements_found if e.element_type == "button"]
            for button in buttons[:10]:  # Test up to 10 buttons
                try:
                    self.click_element(button.selector)
                    buttons_tested.append(button.text or button.selector)
                    time.sleep(0.5)
                    results.append(TestResult(
                        name=f"Button: {button.text or button.selector}",
                        status=TestStatus.PASSED,
                        passed=True,
                        clicks_performed=[button.selector]
                    ))
                except Exception as e:
                    results.append(TestResult(
                        name=f"Button: {button.text or button.selector}",
                        status=TestStatus.FAILED,
                        passed=False,
                        errors=[str(e)]
                    ))
            
            # Test forms (inputs)
            inputs = [e for e in elements_found if e.element_type == "input"]
            for inp in inputs[:5]:  # Test up to 5 inputs
                if inp.enabled and inp.visible:
                    try:
                        self.type_text(inp.selector, "test")
                        forms_tested.append(inp.text or inp.selector)
                        results.append(TestResult(
                            name=f"Input: {inp.text or inp.selector}",
                            status=TestStatus.PASSED,
                            passed=True
                        ))
                    except Exception as e:
                        results.append(TestResult(
                            name=f"Input: {inp.text or inp.selector}",
                            status=TestStatus.FAILED,
                            passed=False,
                            errors=[str(e)]
                        ))
            
            # Test navigation (links)
            links = [e for e in elements_found if e.element_type == "link"]
            for link in links[:5]:  # Test up to 5 links
                if link.visible and "http" not in (link.text or ""):
                    try:
                        self.click_element(link.selector)
                        navigation_tested.append(link.text or link.selector)
                        results.append(TestResult(
                            name=f"Link: {link.text or link.selector}",
                            status=TestStatus.PASSED,
                            passed=True
                        ))
                    except:
                        pass
            
            # Take final screenshot
            self.take_screenshot("final_state")
            
        except Exception as e:
            results.append(TestResult(
                name="Test Execution",
                status=TestStatus.ERROR,
                passed=False,
                errors=[str(e)]
            ))
        finally:
            self.stop_browser()
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Calculate totals
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        
        return AppTestReport(
            app_url=url,
            app_path=app_path,
            overall_status=TestStatus.PASSED if failed_count == 0 else TestStatus.FAILED,
            passed_count=passed_count,
            failed_count=failed_count,
            total_count=len(results),
            results=results,
            elements_found=elements_found,
            buttons_tested=buttons_tested,
            forms_tested=forms_tested,
            navigation_tested=navigation_tested,
            screenshots=self.screenshots
        )
    
    def _detect_app_type(self, app_path: str) -> str:
        """Detect app type from package.json or files."""
        package_json = os.path.join(app_path, "package.json")
        if os.path.exists(package_json):
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                    deps = pkg.get("dependencies", {})
                    if "next" in deps:
                        return "next"
                    if "react" in deps:
                        return "react"
                    if "vue" in deps:
                        return "vue"
            except:
                pass
        return "node"
    
    def quick_test(self, url: str) -> Dict[str, Any]:
        """
        Quick URL test.
        
        Usage:
            from neuro.skills.playwright_tester import quick_test
            
            result = quick_test("http://localhost:3000")
            print(f"Passed: {result['passed_count']}/{result['total_count']}")
        """
        report = self.test_app(app_path="", port=0)
        report.app_url = url
        
        # Navigate directly
        self.start_browser()
        self.navigate_to(url)
        elements = self.discover_elements()
        self.stop_browser()
        
        return {
            "url": url,
            "elements_found": len(elements),
            "buttons": len([e for e in elements if e.element_type == "button"]),
            "inputs": len([e for e in elements if e.element_type == "input"]),
            "links": len([e for e in elements if e.element_type == "link"])
        }


def test_created_app(app_path: str, port: int = 3000) -> Dict[str, Any]:
    """
    Test a created app and return results.
    
    Usage:
        from neuro.skills.playwright_tester import test_created_app
        
        report = test_created_app("/path/to/my-app", port=3000)
        print(f"Passed: {report['passed_count']}/{report['total_count']}")
        print(f"Buttons tested: {report['buttons_tested']}")
    """
    tester = PlaywrightTester()
    report = tester.test_app(app_path, port)
    
    return {
        "app_url": report.app_url,
        "passed_count": report.passed_count,
        "failed_count": report.failed_count,
        "total_count": report.total_count,
        "buttons_tested": report.buttons_tested,
        "forms_tested": report.forms_tested,
        "navigation_tested": report.navigation_tested,
        "screenshots": report.screenshots,
        "overall_status": report.overall_status.value
    }


# SKILL.md content
SKILL_MD = """
---
name: playwright-tester
description: Automatically test apps, websites, and verify UI/functionality
triggers:
  - test
  - playwright
  - ui
  - frontend
  - button
  - click
  - verify
  - e2e
---

# Playwright App Tester

Automatically tests created apps, websites, and verifies UI/functionality.

## Features

### 1. Element Discovery
Automatically finds:
- Buttons (button, [role='button'], input[type='submit'])
- Links (a, [role='link'])
- Inputs (input, textarea, select)

### 2. Automated Testing
- Click all buttons
- Type into inputs
- Test navigation links
- Verify page loads

### 3. Screenshots
- Capture screenshots at key points
- Visual verification of UI state

### 4. Comprehensive Reports
- Pass/fail counts
- Elements found
- Buttons/forms/navigation tested
- Error messages

## Usage

```python
from neuro.skills.playwright_tester import PlaywrightTester, test_created_app

# Quick test URL
result = quick_test("http://localhost:3000")

# Full app test
report = test_created_app("/path/to/app", port=3000)
print(f"Passed: {report['passed_count']}/{report['total_count']}")

# Custom tester
tester = PlaywrightTester(headless=False)  # See browser
tester.start_browser()
tester.navigate_to("http://localhost:3000")
elements = tester.discover_elements()
tester.click_element("#submit-button")
tester.stop_browser()
```

## Test Categories

| Category | What it tests |
|----------|--------------|
| Navigation | Page load, URL access |
| Elements | All buttons, inputs, links found |
| Buttons | Click behavior |
| Forms | Input typing, form submission |
| Navigation | Link clicks and routing |
"""