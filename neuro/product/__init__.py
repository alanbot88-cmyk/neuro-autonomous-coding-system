"""
Product Intake System - Understand what Neuro is building
Converts vague prompts into structured product specs
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import re


@dataclass
class ProductSpec:
    """Structured product specification."""
    app_type: str = "webapp"  # webapp, saas, api, landing, presentation
    users: List[str] = field(default_factory=list)
    core_features: List[str] = field(default_factory=list)
    tech_stack: Dict[str, str] = field(default_factory=dict)
    deployment: str = "vercel"
    constraints: Dict[str, Any] = field(default_factory=dict)
    raw_goal: str = ""


class RequirementParser:
    """Parse vague user goals into structured requirements."""
    
    APP_TYPE_PATTERNS = {
        "saas": r"\bSAAS|SaaS|subscription|multi-tenant|tenant\b",
        "landing": r"\blanding page|marketing|landingpage|promo\b",
        "presentation": r"\bpresentation|slide|deck|demo\b",
        "api": r"\bapi|REST|backend|endpoint\b",
        "dashboard": r"\bdashboard|admin|analytics|reporting\b",
        "crm": r"\bCRM|customer|leads?|clients?\b",
        "ecommerce": r"\becomm?|shop|store|cart|checkout\b",
        "blog": r"\bblog|posts?|articles?|cms\b",
        "social": r"\bsocial|community|forum|users\b",
    }
    
    USER_PATTERNS = {
        "admin": r"\badmin|administrator|manager\b",
        "agent": r"\bagent|sales|employee|staff\b",
        "client": r"\bclient|customer|guest|visitor\b",
        "user": r"\buser|member|subscriber\b",
        "developer": r"\bdeveloper|programmer|engineer\b",
    }
    
    def parse(self, goal: str) -> ProductSpec:
        """Parse goal into structured product spec."""
        spec = ProductSpec(raw_goal=goal)
        
        # Detect app type
        for app_type, pattern in self.APP_TYPE_PATTERNS.items():
            if re.search(pattern, goal, re.IGNORECASE):
                spec.app_type = app_type
                break
        
        # Detect users
        for user_type, pattern in self.USER_PATTERNS.items():
            if re.search(pattern, goal, re.IGNORECASE):
                if user_type not in spec.users:
                    spec.users.append(user_type)
        
        # Default users if none detected
        if not spec.users:
            spec.users = ["user", "admin"]
        
        # Detect core features based on app type
        spec.core_features = self._detect_features(goal, spec.app_type)
        
        # Set default tech stack
        spec.tech_stack = self._select_stack(goal, spec.app_type)
        
        # Detect deployment preference
        spec.deployment = self._detect_deployment(goal)
        
        return spec
    
    def _detect_features(self, goal: str, app_type: str) -> List[str]:
        """Detect required features from goal and app type."""
        features = []
        
        feature_keywords = {
            "authentication": r"\bauth|login|signup|register|password\b",
            "dashboard": r"\bdashboard|home|overview|summary\b",
            "crud": r"\bcreate|read|update|delete|crud|manage\b",
            "forms": r"\bform|input|submit|validation\b",
            "search": r"\bsearch|filter|find|query\b",
            "upload": r"\bupload|file|image|media\b",
            "export": r"\bexport|download|csv|pdf\b",
            "permissions": r"\bpermissions?|roles?|access\b",
            "notifications": r"\bnotif|email|alert|broadcast\b",
            "payments": r"\bpayment|stripe|billing|subscription\b",
            "chat": r"\bchat|messaging|realtime|socket\b",
            "api": r"\bapi|endpoint|webhook\b",
        }
        
        for feature, pattern in feature_keywords.items():
            if re.search(pattern, goal, re.IGNORECASE):
                features.append(feature)
        
        # Add default features based on app type
        defaults = {
            "saas": ["authentication", "dashboard", "crud", "forms"],
            "landing": ["forms", "notifications"],
            "api": ["api", "crud"],
            "Dashboard": ["authentication", "dashboard"],
        }
        if app_type in defaults:
            for f in defaults[app_type]:
                if f not in features:
                    features.append(f)
        
        return features
    
    def _select_stack(self, goal: str, app_type: str) -> Dict[str, str]:
        """Select appropriate tech stack."""
        # Check for explicit stack mentions
        stacks = {
            "nextjs": r"\bnextjs|next\.js\b",
            "react": r"\breact\b",
            "vue": r"\bvue|laravel\b",
            "django": r"\bdjango|python\b",
            "fastapi": r"\bfastapi|fast\.api\b",
            "flask": r"\bflask\b",
            "express": r"\bexpress|node\b",
            "supabase": r"\bsupabase\b",
            "postgres": r"\bpostgres|postgresql\b",
            "mongo": r"\bmongo|mongodb\b",
            "sqlite": r"\bsqlite\b",
        }
        
        selected = {}
        for stack, pattern in stacks.items():
            if re.search(pattern, goal, re.IGNORECASE):
                if "frontend" not in selected and stack in ["nextjs", "react", "vue"]:
                    selected["frontend"] = stack
                elif "backend" not in selected and stack in ["django", "fastapi", "flask", "express"]:
                    selected["backend"] = stack
                elif "database" not in selected and stack in ["supabase", "postgres", "mongo", "sqlite"]:
                    selected["database"] = stack
        
        # Default stack
        if not selected:
            selected = {
                "frontend": "nextjs",
                "backend": "nextjs",
                "database": "sqlite",
            }
        
        return selected
    
    def _detect_deployment(self, goal: str) -> str:
        """Detect deployment target."""
        deploy_patterns = {
            "vercel": r"\bvercel\b",
            "railway": r"\brailway\b",
            "render": r"\brender\b",
            "docker": r"\bdocker|container|k8s\b",
            "static": r"\bstatic|hosting\b",
        }
        
        for deploy, pattern in deploy_patterns.items():
            if re.search(pattern, goal, re.IGNORECASE):
                return deploy
        
        return "auto"


def parse_goal(goal: str) -> ProductSpec:
    """Quick function to parse a goal into product spec."""
    parser = RequirementParser()
    return parser.parse(goal)
