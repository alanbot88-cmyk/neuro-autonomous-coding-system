"""
Stack Profiles - Predefined tech stacks for different app types

Each stack includes recommended deployment platform:
- Vercel: Next.js, static sites, React apps
- Railway: FastAPI, Django, Express with Postgres
- Render: Flask, Express, generic web apps
- Docker: Any containerized application
- Netlify: Static sites, Hugo, Jekyll
- Replit: Quick prototypes, educational projects
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class StackProfile:
    """Tech stack configuration."""
    name: str
    frontend: str
    backend: str
    database: str
    auth: str
    testing: str
    deployment: str
    package_manager: str = "npm"
    common_deps: List[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "frontend": self.frontend,
            "backend": self.backend,
            "database": self.database,
            "auth": self.auth,
            "testing": self.testing,
            "deployment": self.deployment,
            "package_manager": self.package_manager,
        }


# Predefined stack profiles
STACKS = {
    "nextjs_supabase": StackProfile(
        name="nextjs_supabase",
        frontend="Next.js + Tailwind + shadcn/ui",
        backend="Next.js API routes",
        database="Supabase (Postgres)",
        auth="Supabase Auth",
        testing="Playwright + Vitest",
        deployment="Vercel",
        package_manager="npm",
        common_deps=["next", "react", "tailwindcss", "@supabase/supabase-js"],
    ),
    
    "nextjs_fastapi": StackProfile(
        name="nextjs_fastapi",
        frontend="Next.js + Tailwind",
        backend="FastAPI (Python)",
        database="Postgres + SQLAlchemy",
        auth="JWT + FastAPI-Login",
        testing="Playwright + pytest",
        deployment="Railway",
        package_manager="npm + pip",
        common_deps=["fastapi", "uvicorn", "sqlalchemy", "psycopg2"],
    ),
    
    "react_express": StackProfile(
        name="react_express",
        frontend="React + Vite",
        backend="Express.js",
        database="MongoDB",
        auth="Passport.js + JWT",
        testing="Jest + Cypress",
        deployment="Render",
        package_manager="npm",
        common_deps=["express", "mongoose", "passport", "jsonwebtoken"],
    ),
    
    "django_htmx": StackProfile(
        name="django_htmx",
        frontend="Django + HTMX + Tailwind",
        backend="Django",
        database="Postgres",
        auth="Django Auth",
        testing="pytest",
        deployment="Railway",
        package_manager="pip",
        common_deps=["django", "psycopg2", "djangorestframework"],
    ),
    
    "flask_sqlite": StackProfile(
        name="flask_sqlite",
        frontend="Vanilla JS or React",
        backend="Flask",
        database="SQLite",
        auth="Flask-Login",
        testing="pytest",
        deployment="Render",
        package_manager="pip",
        common_deps=["flask", "flask-sqlalchemy", "flask-login"],
    ),
    
    "static_landing": StackProfile(
        name="static_landing",
        frontend="HTML + Tailwind",
        backend="None",
        database="None",
        auth="None",
        testing="None",
        deployment="Vercel/Netlify",
        package_manager="npm",
        common_deps=["tailwindcss", "@tailwindcss/forms"],
    ),
    
    "presentation": StackProfile(
        name="presentation",
        frontend="HTML + CSS + JS",
        backend="None",
        database="None",
        auth="None",
        testing="None",
        deployment="GitHub Pages",
        package_manager="npm",
        common_deps=["reveal.js"],
    ),
}


def get_stack(name: str) -> StackProfile:
    """Get a stack profile by name."""
    return STACKS.get(name.lower(), STACKS["nextjs_supabase"])


def select_stack_for_goal(goal: str) -> StackProfile:
    """Auto-select stack based on goal text."""
    goal_lower = goal.lower()
    
    if any(k in goal_lower for k in ["next", "react", "frontend"]):
        if "supabase" in goal_lower:
            return STACKS["nextjs_supabase"]
        return STACKS["nextjs_supabase"]
    
    if any(k in goal_lower for k in ["fastapi", "python", "api"]):
        return STACKS["nextjs_fastapi"]
    
    if any(k in goal_lower for k in ["django"]):
        return STACKS["django_htmx"]
    
    if any(k in goal_lower for k in ["landing", "static", "marketing"]):
        return STACKS["static_landing"]
    
    if any(k in goal_lower for k in ["presentation", "slide", "deck"]):
        return STACKS["presentation"]
    
    if any(k in goal_lower for k in ["flask", "simple"]):
        return STACKS["flask_sqlite"]
    
    # Default to Next.js + Supabase
    return STACKS["nextjs_supabase"]


def list_stacks() -> List[str]:
    """List all available stacks."""
    return list(STACKS.keys())
