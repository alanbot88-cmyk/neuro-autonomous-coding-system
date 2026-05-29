"""
Architecture Planner - Generate application architecture
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ArchitecturePlan:
    """Complete application architecture."""
    project_name: str
    file_tree: Dict[str, Any] = field(default_factory=dict)
    database_schema: Dict[str, Any] = field(default_factory=dict)
    api_routes: List[str] = field(default_factory=list)
    pages: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    test_plan: List[str] = field(default_factory=list)
    deployment_plan: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "file_tree": self.file_tree,
            "database_schema": self.database_schema,
            "api_routes": self.api_routes,
            "pages": self.pages,
            "components": self.components,
            "services": self.services,
            "test_plan": self.test_plan,
            "deployment_plan": self.deployment_plan,
        }


class AppArchitect:
    """Generate application architecture from product spec."""
    
    def plan(self, spec, stack: str = "nextjs") -> ArchitecturePlan:
        """Generate architecture plan."""
        plan = ArchitecturePlan(project_name=self._slugify(spec.raw_goal))
        
        if stack == "nextjs":
            plan.file_tree = self._nextjs_tree(spec)
            plan.components = self._nextjs_components(spec)
            plan.api_routes = self._nextjs_routes(spec)
            plan.pages = self._nextjs_pages(spec)
        elif stack == "fastapi":
            plan.file_tree = self._fastapi_tree(spec)
            plan.api_routes = self._fastapi_routes(spec)
        elif stack == "django":
            plan.file_tree = self._django_tree(spec)
        
        plan.test_plan = self._default_tests(spec)
        plan.deployment_plan = self._deployment_plan(stack)
        
        return plan
    
    def _slugify(self, text: str) -> str:
        import re
        text = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[-\s]+', '-', text).strip('-')
    
    def _nextjs_tree(self, spec) -> Dict[str, Any]:
        return {
            "src/": {
                "app/": {
                    "layout.tsx": "Root layout",
                    "page.tsx": "Home page",
                    "globals.css": "Global styles",
                },
                "components/": {
                    "ui/": "{shadcn components}",
                    "layout/": "{layout components}",
                },
                "lib/": {
                    "utils.ts": "Utility functions",
                    "db.ts": "Database client",
                },
            },
            "package.json": "Dependencies",
            "tailwind.config.ts": "Tailwind config",
            "next.config.js": "Next.js config",
        }
    
    def _nextjs_pages(self, spec) -> List[str]:
        pages = ["_app", "_document", "index"]
        for user in spec.users:
            pages.append(f"{user}/dashboard")
        if "authentication" in spec.core_features:
            pages.extend(["auth/login", "auth/register"])
        if "search" in spec.core_features:
            pages.append("search")
        return pages
    
    def _nextjs_components(self, spec) -> List[str]:
        components = ["Button", "Card", "Input", "Form"]
        if "forms" in spec.core_features:
            components.append("FormField")
        if "search" in spec.core_features:
            components.append("SearchBar")
        if "dashboard" in spec.core_features:
            components.append("DataTable")
        return components
    
    def _nextjs_routes(self, spec) -> List[str]:
        routes = ["/api/health"]
        if "authentication" in spec.core_features:
            routes.extend(["/api/auth/login", "/api/auth/register"])
        if "crud" in spec.core_features:
            routes.append("/api/[resource]")
        return routes
    
    def _fastapi_tree(self, spec) -> Dict[str, Any]:
        return {
            "app/": {
                "main.py": "FastAPI app",
                "api/": {
                    "__init__.py": "",
                    "routes.py": "API routes",
                },
                "models/": {
                    "__init__.py": "",
                    "schemas.py": "Pydantic models",
                },
                "db/": {
                    "__init__.py": "",
                    "database.py": "DB connection",
                },
            },
            "requirements.txt": "Dependencies",
        }
    
    def _fastapi_routes(self, spec) -> List[str]:
        routes = ["/health", "/docs"]
        if "crud" in spec.core_features:
            routes.append("/{resource}")
        return routes
    
    def _django_tree(self, spec) -> Dict[str, Any]:
        return {
            "config/": {
                "settings.py": "Settings",
                "urls.py": "URLs",
            },
            "apps/": {},
            "templates/": {},
            "static/": {},
        }
    
    def _default_tests(self, spec) -> List[str]:
        return [
            "test_homepage_loads",
            "test_health_check",
            "test_crud_operations" if "crud" in spec.core_features else None,
            "test_forms_validate" if "forms" in spec.core_features else None,
        ]
    
    def _deployment_plan(self, stack: str) -> Dict[str, Any]:
        plans = {
            "nextjs": {
                "platform": "vercel",
                "build": "npm run build",
                "env_vars": ["DATABASE_URL"],
            },
            "fastapi": {
                "platform": "railway",
                "build": "pip install -r requirements.txt",
                "env_vars": ["DATABASE_URL", "SECRET_KEY"],
            },
        }
        return plans.get(stack, {"platform": "auto"})


def create_architecture(spec, stack: str = "nextjs") -> ArchitecturePlan:
    """Quick function to create architecture."""
    architect = AppArchitect()
    return architect.plan(spec, stack)
