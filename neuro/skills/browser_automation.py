"""
Neuro Browser Automation Skill (Playwright)
Web automation and scraping capabilities
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio

class BrowserType(Enum):
    """Supported browsers"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"

class BrowserAction(Enum):
    """Browser automation actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCREENSHOT = "screenshot"
    SCRAPE = "scrape"
    WAIT = "wait"
    SCROLL = "scroll"
    HOVER = "hover"
    SELECT = "select"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    EVALUATE = "evaluate"
    GO_BACK = "go_back"
    RELOAD = "reload"

@dataclass
class BrowserConfig:
    """Browser configuration"""
    browser_type: BrowserType = BrowserType.CHROMIUM
    headless: bool = True
    viewport: tuple = (1920, 1080)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    timeout: int = 30000
    slow_mo: int = 0

@dataclass
class BrowserActionStep:
    """Single browser action step"""
    action: BrowserAction
    selector: Optional[str] = None
    value: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)
    wait_for: Optional[str] = None

@dataclass
class BrowserTask:
    """Browser automation task definition"""
    url: str
    steps: List[BrowserActionStep]
    name: Optional[str] = None

class BrowserAutomation:
    """
    Browser Automation Skill (Playwright)
    Provides web automation, scraping, and testing capabilities
    """
    
    NAME = "browser_automation"
    DESCRIPTION = "Playwright-based browser automation for web scraping, testing, and automation"
    TRIGGERS = ["browser", "playwright", "web", "scrape", "crawl", "navigate", "click", "automation"]
    
    # Default configuration
    DEFAULT_CONFIG = BrowserConfig()
    
    # Common selectors
    COMMON_SELECTORS = {
        "button": ["button", "[role='button']", "input[type='submit']", "input[type='button']"],
        "link": ["a", "[role='link']"],
        "input": ["input", "textarea", "[contenteditable='true']"],
        "form": ["form", "[role='form']"],
        "image": ["img", "picture", "[role='img']"],
        "heading": ["h1", "h2", "h3", "h4", "h5", "h6"],
    }
    
    @classmethod
    def create_config(
        cls,
        browser: str = "chromium",
        headless: bool = True,
        viewport: tuple = (1920, 1080),
        **kwargs
    ) -> BrowserConfig:
        """Create browser configuration"""
        browser_map = {
            "chromium": BrowserType.CHROMIUM,
            "firefox": BrowserType.FIREFOX,
            "webkit": BrowserType.WEBKIT,
        }
        
        return BrowserConfig(
            browser_type=browser_map.get(browser, BrowserType.CHROMIUM),
            headless=headless,
            viewport=viewport,
            **{k: v for k, v in kwargs.items() if k in ["user_agent", "proxy", "timeout", "slow_mo"]}
        )
    
    @classmethod
    def create_task(
        cls,
        url: str,
        actions: List[Dict[str, Any]],
        name: Optional[str] = None
    ) -> BrowserTask:
        """Create a browser automation task"""
        steps = []
        
        for action_dict in actions:
            action = BrowserAction(action_dict.get("action", "navigate"))
            step = BrowserActionStep(
                action=action,
                selector=action_dict.get("selector"),
                value=action_dict.get("value"),
                options=action_dict.get("options", {}),
                wait_for=action_dict.get("wait_for")
            )
            steps.append(step)
        
        return BrowserTask(url=url, steps=steps, name=name)
    
    @classmethod
    def parse_natural_language(cls, task_description: str) -> BrowserTask:
        """Parse natural language task description into browser task"""
        # Extract URL
        import re
        url_match = re.search(r'https?://[^\s]+', task_description)
        url = url_match.group(0) if url_match else "https://example.com"
        
        steps = []
        
        # Parse actions from natural language
        action_patterns = {
            r'click\s+(?:on\s+)?(.+)': (BrowserAction.CLICK, "selector"),
            r'type\s+"([^"]+)"\s+(?:in|into)\s+(.+)': (BrowserAction.TYPE, "value", "selector"),
            r'navigate\s+to\s+(.+)': (BrowserAction.NAVIGATE, "value"),
            r'go\s+to\s+(.+)': (BrowserAction.NAVIGATE, "value"),
            r'screenshot': (BrowserAction.SCREENSHOT, None),
            r'scrape': (BrowserAction.SCRAPE, None),
            r'scroll\s+(up|down)': (BrowserAction.SCROLL, "value"),
            r'hover\s+(?:over\s+)?(.+)': (BrowserAction.HOVER, "selector"),
            r'wait\s+(?:for\s+)?(.+)': (BrowserAction.WAIT, "selector"),
            r'select\s+"([^"]+)"\s+(?:from|in)\s+(.+)': (BrowserAction.SELECT, "value", "selector"),
        }
        
        for pattern, action_info in action_patterns.items():
            match = re.search(pattern, task_description, re.IGNORECASE)
            if match:
                action = action_info[0]
                
                if action == BrowserAction.SCRAPE:
                    steps.append(BrowserActionStep(action=BrowserAction.SCRAPE))
                elif action == BrowserAction.SCREENSHOT:
                    steps.append(BrowserActionStep(action=BrowserAction.SCREENSHOT))
                elif action == BrowserAction.NAVIGATE:
                    steps.append(BrowserActionStep(
                        action=action,
                        value=match.group(1) if match.groups() else None
                    ))
                elif action == BrowserAction.SCROLL:
                    steps.append(BrowserActionStep(
                        action=action,
                        value=match.group(1)
                    ))
                elif len(action_info) == 2:
                    steps.append(BrowserActionStep(
                        action=action,
                        selector=match.group(1)
                    ))
                elif len(action_info) == 3:
                    steps.append(BrowserActionStep(
                        action=action,
                        value=match.group(1),
                        selector=match.group(2)
                    ))
        
        if not steps:
            # Default to navigation if no specific action
            steps.append(BrowserActionStep(action=BrowserAction.NAVIGATE, value=url))
        
        return BrowserTask(url=url, steps=steps, name=task_description[:50])
    
    @classmethod
    def generate_playwright_script(cls, task: BrowserTask, config: BrowserConfig) -> str:
        """Generate Playwright Python script for the task"""
        
        script_parts = [
            '"""Generated Playwright script"""',
            'from playwright.sync_api import sync_playwright',
            '',
            f'def run_task():',
            f'    with sync_playwright() as p:',
            f'        browser = p.{config.browser_type.value}.launch(headless={config.headless})',
        ]
        
        if config.viewport:
            script_parts.append(
                f'        context = browser.new_context(viewport={config.viewport})'
            )
        else:
            script_parts.append('        context = browser.new_context()')
        
        if config.user_agent:
            script_parts.append(f'        context.set_extra_http_headers({{"User-Agent": "{config.user_agent}"}})')
        
        script_parts.append('        page = context.new_page()')
        script_parts.append('')
        
        for i, step in enumerate(task.steps):
            if step.action == BrowserAction.NAVIGATE:
                if step.value:
                    script_parts.append(f'        page.goto("{step.value}")')
                elif i == 0:
                    script_parts.append(f'        page.goto("{task.url}")')
            
            elif step.action == BrowserAction.CLICK:
                script_parts.append(f'        page.click("{step.selector}")')
            
            elif step.action == BrowserAction.TYPE:
                script_parts.append(f'        page.fill("{step.selector}", "{step.value}")')
            
            elif step.action == BrowserAction.SCREENSHOT:
                script_parts.append(f'        page.screenshot(path="screenshot_{i}.png")')
            
            elif step.action == BrowserAction.SCRAPE:
                script_parts.append(f'        content = page.content()')
                script_parts.append(f'        # Process scraped content')
            
            elif step.action == BrowserAction.WAIT:
                wait_time = step.value or "1000"
                script_parts.append(f'        page.wait_for_timeout({wait_time})')
            
            elif step.action == BrowserAction.SCROLL:
                direction = step.value or "down"
                scroll_expr = 'window.innerHeight' if direction == "down" else '-window.innerHeight'
                script_parts.append(
                    f'        page.evaluate("window.scrollBy(0, {scroll_expr})")'
                )
            
            elif step.action == BrowserAction.HOVER:
                script_parts.append(f'        page.hover("{step.selector}")')
            
            elif step.action == BrowserAction.WAIT_FOR:
                if step.selector:
                    script_parts.append(f'        page.wait_for_selector("{step.selector}")')
            
            elif step.action == BrowserAction.EVALUATE:
                script_parts.append(f'        page.evaluate("""{step.value or "() => {{}}"}""")')
        
        script_parts.extend([
            '        browser.close()',
            '',
            'if __name__ == "__main__":',
            '    run_task()'
        ])
        
        return '\n'.join(script_parts)
    
    @classmethod
    def get_capabilities(cls) -> List[str]:
        """Return browser automation capabilities"""
        return [
            "Multi-browser support (Chromium, Firefox, WebKit)",
            "Page navigation and interaction",
            "Element clicking and typing",
            "Screenshot capture",
            "Web scraping and content extraction",
            "Form filling and submission",
            "Drag and drop",
            "File upload/download",
            "JavaScript execution",
            "Network interception",
            "Mobile device emulation",
            "Headless and headed modes"
        ]
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for browser automation skill
        Returns task definition and generated script
        """
        config = cls.create_config(
            **(context.get("config", {}) if context else {})
        )
        
        browser_task = cls.parse_natural_language(task)
        
        script = cls.generate_playwright_script(browser_task, config)
        
        return {
            "skill": cls.NAME,
            "task": browser_task.name or task[:50],
            "url": browser_task.url,
            "steps": [{"action": s.action.value, "selector": s.selector, "value": s.value} for s in browser_task.steps],
            "config": {
                "browser": config.browser_type.value,
                "headless": config.headless,
                "viewport": config.viewport
            },
            "capabilities": cls.get_capabilities(),
            "playwright_script": script,
            "note": "Install playwright: pip install playwright && playwright install"
        }

# Convenience functions
def create_browser_task(url: str, actions: List[Dict]) -> BrowserTask:
    """Create a browser automation task"""
    return BrowserAutomation.create_task(url, actions)

def generate_script(task: BrowserTask, config: Optional[BrowserConfig] = None) -> str:
    """Generate Playwright script"""
    return BrowserAutomation.generate_playwright_script(
        task, config or BrowserAutomation.DEFAULT_CONFIG
    )

def parse_task(task: str) -> BrowserTask:
    """Parse natural language into browser task"""
    return BrowserAutomation.parse_natural_language(task)
