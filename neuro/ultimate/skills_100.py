"""
Neuro Ultimate 100+ Skills - Complete Auto-Trigger System
==========================================================
The most comprehensive skill integration for AI coding systems.
All 100+ skills are automatically triggered based on task context.
Nothing remains unused - everything activates when needed.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import re


# =============================================================================
# SKILL CATEGORIES
# =============================================================================

class SkillCategory(Enum):
    """All possible skill categories."""
    # Development
    CODING = "coding"
    DEBUGGING = "debugging"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DATABASE = "database"
    API = "api"
    SECURITY = "security"
    
    # Frontend/Design
    FRONTEND = "frontend"
    UI_DESIGN = "ui_design"
    UX_DESIGN = "ux_design"
    ANIMATION = "animation"
    THREE_D = "3d"
    GRAPHICS = "graphics"
    
    # Backend/Server
    BACKEND = "backend"
    MICROSERVICES = "microservices"
    CLOUD = "cloud"
    CONTAINER = "container"
    DEVOPS = "devops"
    
    # AI/ML
    AI_MODELS = "ai_models"
    ML = "machine_learning"
    DATA_SCIENCE = "data_science"
    
    # Tools & Integration
    VERSION_CONTROL = "version_control"
    MONITORING = "monitoring"
    COMMUNICATION = "communication"
    DOCUMENTATION = "documentation"
    
    # Business & Enterprise
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    PRODUCTIVITY = "productivity"


# =============================================================================
# SKILL DEFINITIONS (100+ Skills)
# =============================================================================

@dataclass
class UltimateSkill:
    """A comprehensive skill with auto-trigger capabilities."""
    name: str
    category: SkillCategory
    description: str
    triggers: List[str]  # Keywords that trigger this skill
    priority: int  # 1 = Critical, 2 = High, 3 = Medium
    capabilities: List[str]  # What this skill can do
    code_template: Optional[str] = None
    mcp_server: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    usage_count: int = 0
    
    def matches_task(self, task: str) -> float:
        """Calculate match score for a task."""
        if not task:
            return 0.0
        task_lower = task.lower()
        score = 0.0
        
        # Check triggers (weighted higher)
        for trigger in self.triggers:
            if trigger.lower() in task_lower:
                score += 2.0
                # Bonus for exact word matches
                if trigger.lower() == task_lower:
                    score += 1.0
        
        # Check capabilities
        for cap in self.capabilities:
            cap_words = cap.lower().split()
            for word in cap_words:
                if len(word) > 3 and word in task_lower:
                    score += 0.5
        
        return score


# =============================================================================
# THE ULTIMATE 100+ SKILLS REGISTRY
# =============================================================================

ULTIMATE_SKILLS: List[UltimateSkill] = [
    # ============ CODING & DEVELOPMENT (15 skills) ============
    UltimateSkill(
        name="python_development",
        category=SkillCategory.CODING,
        description="Python 3 development, FastAPI, Django, Flask, async programming",
        triggers=["python", "fastapi", "django", "flask", "async", "pip", "venv"],
        priority=1,
        capabilities=["web development", "APIs", "automation", "scripting", "data processing"]
    ),
    UltimateSkill(
        name="javascript_development",
        category=SkillCategory.CODING,
        description="JavaScript/TypeScript development, Node.js, npm packages",
        triggers=["javascript", "js", "typescript", "ts", "node", "npm", "nodejs", "deno"],
        priority=1,
        capabilities=["frontend", "backend", "node.js", "npm packages", "ES6+"]
    ),
    UltimateSkill(
        name="react_development",
        category=SkillCategory.FRONTEND,
        description="React.js development with hooks, context, state management",
        triggers=["react", "jsx", "hooks", "redux", "zustand", "context api", "react native"],
        priority=1,
        capabilities=["React components", "hooks", "state management", "React Native", "Next.js"]
    ),
    UltimateSkill(
        name="vue_development",
        category=SkillCategory.FRONTEND,
        description="Vue.js 3 development, Composition API, Nuxt.js",
        triggers=["vue", "vuejs", "nuxt", "composition api", "pinia", "vuex"],
        priority=2,
        capabilities=["Vue components", "Composition API", "State management", "Nuxt.js"]
    ),
    UltimateSkill(
        name="angular_development",
        category=SkillCategory.FRONTEND,
        description="Angular development, TypeScript, RxJS, Angular CLI",
        triggers=["angular", "ng", "rxjs", "angular cli", "typescript"],
        priority=2,
        capabilities=["Angular components", "RxJS", "Services", "Modules"]
    ),
    UltimateSkill(
        name="golang_development",
        category=SkillCategory.BACKEND,
        description="Go (Golang) development, concurrency, microservices",
        triggers=["golang", "go ", "goroutine", "channels"],
        priority=2,
        capabilities=["concurrent programming", "microservices", "CLI tools", "web servers"]
    ),
    UltimateSkill(
        name="rust_development",
        category=SkillCategory.CODING,
        description="Rust development, ownership, lifetimes, crates",
        triggers=["rust", "cargo", "rustc", "crate", "ownership", " lifetimes"],
        priority=2,
        capabilities=["systems programming", "memory safety", "performance", "WebAssembly"]
    ),
    UltimateSkill(
        name="java_development",
        category=SkillCategory.BACKEND,
        description="Java development, Spring Boot, Maven, Gradle",
        triggers=["java", "spring", "maven", "gradle", "jvm", "tomcat"],
        priority=2,
        capabilities=["enterprise applications", "Spring Boot", "REST APIs", "microservices"]
    ),
    UltimateSkill(
        name="csharp_dotnet",
        category=SkillCategory.BACKEND,
        description="C# and .NET development, ASP.NET, Entity Framework",
        triggers=["csharp", "c#", "dotnet", "asp.net", "nuget", ".net core"],
        priority=2,
        capabilities=["web applications", "APIs", "desktop apps", "Azure"]
    ),
    UltimateSkill(
        name="ruby_development",
        category=SkillCategory.BACKEND,
        description="Ruby development, Rails, Sinatra",
        triggers=["ruby", "rails", "sinatra", "gem", "rake"],
        priority=3,
        capabilities=["web applications", "scripting", "Rails"]
    ),
    UltimateSkill(
        name="php_development",
        category=SkillCategory.BACKEND,
        description="PHP development, Laravel, WordPress, Composer",
        triggers=["php", "laravel", "wordpress", "composer", "symfony"],
        priority=3,
        capabilities=["web development", "CMS", "WordPress", "Laravel"]
    ),
    UltimateSkill(
        name="swift_development",
        category=SkillCategory.CODING,
        description="Swift and iOS/macOS development, SwiftUI",
        triggers=["swift", "ios", "macos", "swiftui", "xcode", "cocoa"],
        priority=2,
        capabilities=["iOS apps", "macOS apps", "SwiftUI", "ARKit"]
    ),
    UltimateSkill(
        name="kotlin_development",
        category=SkillCategory.CODING,
        description="Kotlin development, Android, Jetpack Compose",
        triggers=["kotlin", "android", "jetpack", "gradle", "sdk"],
        priority=2,
        capabilities=["Android apps", "Kotlin", "Jetpack Compose", "Ktor"]
    ),
    UltimateSkill(
        name="sql_development",
        category=SkillCategory.DATABASE,
        description="SQL development, queries, optimization, migrations",
        triggers=["sql", "mysql", "postgresql", "postgres", "sqlite", "query", "database"],
        priority=1,
        capabilities=["database queries", "optimization", "migrations", "schema design"]
    ),
    UltimateSkill(
        name="graphql_development",
        category=SkillCategory.API,
        description="GraphQL development, Apollo, queries, mutations",
        triggers=["graphql", "apollo", "resolver", "mutation", "query"],
        priority=2,
        capabilities=["GraphQL APIs", "resolvers", "subscriptions", "Apollo Client"]
    ),

    # ============ FRONTEND & UI (15 skills) ============
    UltimateSkill(
        name="html_css",
        category=SkillCategory.FRONTEND,
        description="HTML5, CSS3, modern layouts, responsive design",
        triggers=["html", "css", "responsive", "flexbox", "grid", "tailwind", "sass", "scss"],
        priority=1,
        capabilities=["semantic HTML", "CSS layouts", "responsive design", "Tailwind", "SASS"]
    ),
    UltimateSkill(
        name="nextjs_development",
        category=SkillCategory.FRONTEND,
        description="Next.js development, SSR, SSG, API routes",
        triggers=["nextjs", "next.js", "ssr", "ssg", "server side", "api routes"],
        priority=1,
        capabilities=["React SSR", "SSG", "API routes", "routing", "deployment"]
    ),
    UltimateSkill(
        name="svelte_development",
        category=SkillCategory.FRONTEND,
        description="Svelte and SvelteKit development",
        triggers=["svelte", "sveltekit", "svelte.js"],
        priority=2,
        capabilities=["reactive components", "SvelteKit", "stores"]
    ),
    UltimateSkill(
        name="responsive_design",
        category=SkillCategory.UI_DESIGN,
        description="Mobile-first responsive design, breakpoints, media queries",
        triggers=["responsive", "mobile", "breakpoints", "viewport", "media queries"],
        priority=1,
        capabilities=["mobile-first", "CSS media queries", "flexbox", "grid", "units"]
    ),
    UltimateSkill(
        name="css_animations",
        category=SkillCategory.ANIMATION,
        description="CSS animations, transitions, keyframes",
        triggers=["animation", "transition", "keyframes", "transform", "easing"],
        priority=2,
        capabilities=["CSS transitions", "keyframes", "performance", "accessibility"]
    ),
    UltimateSkill(
        name="web_accessibility",
        category=SkillCategory.UI_DESIGN,
        description="Web accessibility (WCAG), ARIA, screen readers",
        triggers=["accessibility", "a11y", "wcag", "aria", "screen reader", "semantic"],
        priority=2,
        capabilities=["WCAG compliance", "ARIA", "keyboard navigation", "screen readers"]
    ),
    UltimateSkill(
        name="ui_component_design",
        category=SkillCategory.UI_DESIGN,
        description="UI component design systems, patterns, documentation",
        triggers=["component", "design system", "storybook", "atomic design", "pattern"],
        priority=2,
        capabilities=["design systems", "component libraries", "Storybook", "documentation"]
    ),
    UltimateSkill(
        name="icon_design",
        category=SkillCategory.GRAPHICS,
        description="Icon design, SVG icons, icon systems",
        triggers=["icon", "svg icon", "feather", "lucide", "font awesome", "heroicons"],
        priority=2,
        capabilities=["SVG icons", "icon systems", "optimization"]
    ),
    UltimateSkill(
        name="svg_graphics",
        category=SkillCategory.GRAPHICS,
        description="SVG graphics, vector manipulation, SVG animations",
        triggers=["svg", "vector", "scalable", "path", "svg animation"],
        priority=2,
        capabilities=["SVG creation", "optimization", "animations", "filters"]
    ),
    UltimateSkill(
        name="image_optimization",
        category=SkillCategory.GRAPHICS,
        description="Image optimization, formats, compression, lazy loading",
        triggers=["image", "optimization", "compress", "webp", "avif", "lazy load", "png", "jpg"],
        priority=2,
        capabilities=["WebP", "AVIF", "lazy loading", "compression", "formats"]
    ),
    UltimateSkill(
        name="font_typography",
        category=SkillCategory.UI_DESIGN,
        description="Typography, fonts, Google Fonts, variable fonts",
        triggers=["font", "typography", "google fonts", "variable font", "typeface"],
        priority=2,
        capabilities=["web fonts", "font loading", "variable fonts", "typography scale"]
    ),
    UltimateSkill(
        name="color_theory",
        category=SkillCategory.UX_DESIGN,
        description="Color theory, palettes, contrast, accessibility",
        triggers=["color", "palette", "contrast", "theme", "dark mode", "light mode"],
        priority=2,
        capabilities=["color schemes", "contrast ratios", "theming", "dark mode"]
    ),
    UltimateSkill(
        name="design_tokens",
        category=SkillCategory.UI_DESIGN,
        description="Design tokens, CSS custom properties, theming",
        triggers=["design token", "css variable", "custom property", "theme", "semantic"],
        priority=2,
        capabilities=["CSS variables", "theming", "design systems", "tokenization"]
    ),
    UltimateSkill(
        name="figma_integration",
        category=SkillCategory.UI_DESIGN,
        description="Figma to code, design tokens, prototyping",
        triggers=["figma", "design", "mockup", "prototype", "wireframe"],
        priority=1,
        capabilities=["design handoff", "Figma plugins", "auto layout", "components"]
    ),
    UltimateSkill(
        name="responsive_images",
        category=SkillCategory.FRONTEND,
        description="Responsive images, srcset, picture element",
        triggers=["srcset", "picture", "responsive image", "art direction", "densities"],
        priority=2,
        capabilities=["responsive images", "srcset", "art direction", "WebP"]
    ),

    # ============ 3D & ANIMATION (15 skills) ============
    UltimateSkill(
        name="threejs_webgl",
        category=SkillCategory.THREE_D,
        description="Three.js WebGL development, 3D scenes, geometries",
        triggers=["three.js", "threejs", "webgl", "3d", "3d model", "scene", "geometry"],
        priority=1,
        capabilities=["3D rendering", "WebGL", "scene graphs", "materials", "lighting"]
    ),
    UltimateSkill(
        name="react_three_fiber",
        category=SkillCategory.THREE_D,
        description="React Three Fiber, declarative 3D in React",
        triggers=["react three", "r3f", "react-fiber", "drei"],
        priority=1,
        capabilities=["React 3D", "declarative", "drei helpers", "react-spring"]
    ),
    UltimateSkill(
        name="gsap_animation",
        category=SkillCategory.ANIMATION,
        description="GSAP animations, ScrollTrigger, timeline",
        triggers=["gsap", "greensock", "scrolltrigger", "scroll", "timeline", "tween"],
        priority=1,
        capabilities=["animations", "ScrollTrigger", "timelines", "morph SVG"]
    ),
    UltimateSkill(
        name="framer_motion",
        category=SkillCategory.ANIMATION,
        description="Framer Motion React animations, gestures, layout",
        triggers=["framer motion", "layout animation", "gesture", "exit", "variants"],
        priority=1,
        capabilities=["React animations", "gestures", "layout", "shared transitions"]
    ),
    UltimateSkill(
        name="blender_automation",
        category=SkillCategory.THREE_D,
        description="Blender Python scripting, 3D modeling automation",
        triggers=["blender", "bpy", "3d model", "animation", "render", "cycles"],
        priority=1,
        capabilities=["3D modeling", "animation", "rendering", "Python scripting"]
    ),
    UltimateSkill(
        name="lottie_animation",
        category=SkillCategory.ANIMATION,
        description="Lottie animations, After Effects to web",
        triggers=["lottie", "after effects", "json animation", "bodymovin"],
        priority=2,
        capabilities=["Lottie", "animation", "After Effects", "interactive"]
    ),
    UltimateSkill(
        name="webgl_shaders",
        category=SkillCategory.THREE_D,
        description="WebGL shaders, GLSL, post-processing",
        triggers=["shader", "glsl", "fragment", "vertex", "post-processing", "shadertoy"],
        priority=2,
        capabilities=["GLSL", "shaders", "post-processing", "effects"]
    ),
    UltimateSkill(
        name="canvas_animation",
        category=SkillCategory.ANIMATION,
        description="Canvas 2D animation, particle systems",
        triggers=["canvas", "2d", "particle", "drawing", "context"],
        priority=2,
        capabilities=["2D canvas", "particles", "drawing", "animation loop"]
    ),
    UltimateSkill(
        name="sprite_animation",
        category=SkillCategory.ANIMATION,
        description="Sprite sheet animations, game development",
        triggers=["sprite", "sheet", "game", "pixel art", "atlas"],
        priority=2,
        capabilities=["sprite sheets", "game loops", "character animation"]
    ),
    UltimateSkill(
        name="scroll_animation",
        category=SkillCategory.ANIMATION,
        description="Scroll-linked animations, parallax effects",
        triggers=["scroll", "parallax", "sticky", "horizontal scroll", "intersection"],
        priority=1,
        capabilities=["scroll triggers", "parallax", "sticky elements"]
    ),
    UltimateSkill(
        name="micro_interactions",
        category=SkillCategory.ANIMATION,
        description="Micro-interactions, hover effects, button animations",
        triggers=["hover", "click", "micro", "button", "toggle", "focus"],
        priority=1,
        capabilities=["hover effects", "button animations", "feedback", "state"]
    ),
    UltimateSkill(
        name="loading_animations",
        category=SkillCategory.ANIMATION,
        description="Loading spinners, skeleton screens, progress",
        triggers=["loading", "spinner", "skeleton", "progress", "bar", "indicator"],
        priority=2,
        capabilities=["loading states", "skeleton screens", "progress indicators"]
    ),
    UltimateSkill(
        name="page_transitions",
        category=SkillCategory.ANIMATION,
        description="Page transitions, route animations, view morphing",
        triggers=["transition", "page", "route", "enter", "exit", "view"],
        priority=2,
        capabilities=["route transitions", "page morphing", "shared elements"]
    ),
    UltimateSkill(
        name="3d_ui_components",
        category=SkillCategory.THREE_D,
        description="3D UI components, cards, buttons, navigation",
        triggers=["3d card", "3d button", "3d ui", "tilt", "hover 3d"],
        priority=2,
        capabilities=["3D effects", "tilt effect", "perspective", "hover"]
    ),
    UltimateSkill(
        name="particle_effects",
        category=SkillCategory.ANIMATION,
        description="Particle effects, fire, smoke, sparkles",
        triggers=["particle", "fire", "smoke", "sparkle", "snow", "rain"],
        priority=2,
        capabilities=["particle systems", "physics", "performance optimization"]
    ),

    # ============ BACKEND & APIs (10 skills) ============
    UltimateSkill(
        name="rest_api_design",
        category=SkillCategory.API,
        description="REST API design, endpoints, versioning",
        triggers=["rest", "api", "endpoint", "http", "crud", "restful"],
        priority=1,
        capabilities=["REST design", "OpenAPI", "versioning", "documentation"]
    ),
    UltimateSkill(
        name="authentication",
        category=SkillCategory.SECURITY,
        description="Authentication, OAuth, JWT, sessions",
        triggers=["auth", "login", "oauth", "jwt", "token", "session", "sso"],
        priority=1,
        capabilities=["JWT", "OAuth", "sessions", "SSO", "2FA"]
    ),
    UltimateSkill(
        name="websocket_communication",
        category=SkillCategory.API,
        description="WebSocket, real-time communication, Socket.io",
        triggers=["websocket", "socket", "real-time", "ws", "socket.io"],
        priority=2,
        capabilities=["WebSocket", "Socket.io", "real-time", "bidirectional"]
    ),
    UltimateSkill(
        name="serverless_functions",
        category=SkillCategory.CLOUD,
        description="Serverless functions, AWS Lambda, Vercel",
        triggers=["serverless", "lambda", "vercel", "netlify", "function", "edge"],
        priority=2,
        capabilities=["serverless", "edge functions", "AWS Lambda", "cold start"]
    ),
    UltimateSkill(
        name="caching_strategies",
        category=SkillCategory.BACKEND,
        description="Caching, Redis, CDN, performance optimization",
        triggers=["cache", "redis", "memcached", "cdn", "optimization"],
        priority=2,
        capabilities=["Redis", "CDN", "caching", "invalidation", "TTL"]
    ),
    UltimateSkill(
        name="message_queues",
        category=SkillCategory.BACKEND,
        description="Message queues, RabbitMQ, Kafka, Redis queues",
        triggers=["queue", "rabbitmq", "kafka", "message", "async", "worker"],
        priority=2,
        capabilities=["message queues", "event-driven", "workers", "dead letter"]
    ),
    UltimateSkill(
        name="file_upload",
        category=SkillCategory.BACKEND,
        description="File upload handling, storage, S3",
        triggers=["upload", "file", "s3", "storage", "multipart", "cloud storage"],
        priority=2,
        capabilities=["S3", "multipart", "presigned URLs", "validation"]
    ),
    UltimateSkill(
        name="api_rate_limiting",
        category=SkillCategory.API,
        description="API rate limiting, throttling, quotas",
        triggers=["rate limit", "throttle", "quota", "api limit", "requests"],
        priority=2,
        capabilities=["rate limiting", "quotas", "throttling", "headers"]
    ),
    UltimateSkill(
        name="webhook_integration",
        category=SkillCategory.API,
        description="Webhook implementation, delivery, retries",
        triggers=["webhook", "callback", "event", "delivery", "retry"],
        priority=2,
        capabilities=["webhooks", "signatures", "retries", "delivery"]
    ),
    UltimateSkill(
        name="background_jobs",
        category=SkillCategory.BACKEND,
        description="Background jobs, task queues, scheduling",
        triggers=["job", "queue", "background", "cron", "schedule", "worker"],
        priority=2,
        capabilities=["background processing", "scheduling", "cron", "workers"]
    ),

    # ============ DATABASE (10 skills) ============
    UltimateSkill(
        name="postgresql",
        category=SkillCategory.DATABASE,
        description="PostgreSQL database, queries, optimization, migrations",
        triggers=["postgresql", "postgres", "psql", "pg"],
        priority=1,
        capabilities=["SQL", "PostgreSQL", "indexes", "migrations", "performance"]
    ),
    UltimateSkill(
        name="mongodb",
        category=SkillCategory.DATABASE,
        description="MongoDB, document database, aggregations",
        triggers=["mongodb", "mongo", "nosql", "document", "aggregation"],
        priority=2,
        capabilities=["document DB", "aggregation pipeline", "mongoose"]
    ),
    UltimateSkill(
        name="redis_cache",
        category=SkillCategory.DATABASE,
        description="Redis caching, sessions, pub/sub",
        triggers=["redis", "cache", "session", "pubsub", "pub/sub"],
        priority=2,
        capabilities=["caching", "sessions", "pub/sub", "rate limiting"]
    ),
    UltimateSkill(
        name="mysql_database",
        category=SkillCategory.DATABASE,
        description="MySQL database, queries, optimization",
        triggers=["mysql", "mariadb", "sql"],
        priority=2,
        capabilities=["MySQL", "queries", "optimization", "replication"]
    ),
    UltimateSkill(
        name="sqlite_database",
        category=SkillCategory.DATABASE,
        description="SQLite database, embedded, migrations",
        triggers=["sqlite", "embedded", "local database"],
        priority=2,
        capabilities=["SQLite", "embedded DB", "migrations"]
    ),
    UltimateSkill(
        name="database_design",
        category=SkillCategory.DATABASE,
        description="Database schema design, normalization, relationships",
        triggers=["schema", "normalization", "relationship", "erd", "design"],
        priority=1,
        capabilities=["schema design", "normalization", "ERD", "relationships"]
    ),
    UltimateSkill(
        name="orm_usage",
        category=SkillCategory.DATABASE,
        description="ORM usage, Prisma, SQLAlchemy, Eloquent",
        triggers=["orm", "prisma", "sqlalchemy", "eloquent", "sequelize"],
        priority=2,
        capabilities=["ORM", "Prisma", "migrations", "relationships"]
    ),
    UltimateSkill(
        name="data_migrations",
        category=SkillCategory.DATABASE,
        description="Database migrations, rollbacks, seeding",
        triggers=["migration", "rollback", "seed", "populate", "fixture"],
        priority=2,
        capabilities=["migrations", "rollbacks", "seed data", "fixtures"]
    ),
    UltimateSkill(
        name="query_optimization",
        category=SkillCategory.DATABASE,
        description="Query optimization, indexes, EXPLAIN",
        triggers=["optimize", "index", "explain", "query plan", "performance"],
        priority=2,
        capabilities=["indexes", "EXPLAIN", "query optimization", "N+1"]
    ),
    UltimateSkill(
        name="nosql_patterns",
        category=SkillCategory.DATABASE,
        description="NoSQL patterns, document modeling, denormalization",
        triggers=["nosql", "document", "denormalize", "embedded", "reference"],
        priority=2,
        capabilities=["NoSQL design", "document modeling", "flexibility"]
    ),

    # ============ CLOUD & DEVOPS (10 skills) ============
    UltimateSkill(
        name="docker_containerization",
        category=SkillCategory.CONTAINER,
        description="Docker containerization, images, compose",
        triggers=["docker", "container", "dockerfile", "compose", "image", "containerize"],
        priority=1,
        capabilities=["Docker", "containers", "Docker Compose", "multi-stage"]
    ),
    UltimateSkill(
        name="kubernetes_deployment",
        category=SkillCategory.CONTAINER,
        description="Kubernetes deployment, pods, services, Helm",
        triggers=["kubernetes", "k8s", "pod", "service", "helm", "ingress", "deployment"],
        priority=2,
        capabilities=["Kubernetes", "pods", "services", "Helm", "networking"]
    ),
    UltimateSkill(
        name="aws_cloud",
        category=SkillCategory.CLOUD,
        description="AWS cloud services, EC2, S3, Lambda, ECS",
        triggers=["aws", "amazon", "ec2", "s3", "lambda", "ecs", "iam", "cloudwatch"],
        priority=1,
        capabilities=["AWS services", "EC2", "S3", "Lambda", "ECS", "IAM"]
    ),
    UltimateSkill(
        name="gcp_cloud",
        category=SkillCategory.CLOUD,
        description="Google Cloud Platform, GCP services",
        triggers=["gcp", "google cloud", "cloud run", "gke", "bigquery", "firestore"],
        priority=2,
        capabilities=["GCP", "Cloud Run", "GKE", "BigQuery", "Firestore"]
    ),
    UltimateSkill(
        name="azure_cloud",
        category=SkillCategory.CLOUD,
        description="Azure cloud services, functions, container apps",
        triggers=["azure", "functions", "container apps", "app service", "cosmos"],
        priority=2,
        capabilities=["Azure", "Functions", "Container Apps", "Cosmos DB"]
    ),
    UltimateSkill(
        name="ci_cd_pipeline",
        category=SkillCategory.DEVOPS,
        description="CI/CD pipelines, GitHub Actions, Jenkins",
        triggers=["ci", "cd", "pipeline", "github actions", "jenkins", "gitlab ci", "automation"],
        priority=1,
        capabilities=["CI/CD", "automation", "GitHub Actions", "Jenkins"]
    ),
    UltimateSkill(
        name="terraform_infra",
        category=SkillCategory.CLOUD,
        description="Infrastructure as Code, Terraform",
        triggers=["terraform", "iac", "infrastructure", "hcl", "terraform"],
        priority=2,
        capabilities=["Terraform", "IaC", "modules", "state management"]
    ),
    UltimateSkill(
        name="nginx_configuration",
        category=SkillCategory.DEVOPS,
        description="Nginx configuration, reverse proxy, load balancing",
        triggers=["nginx", "proxy", "load balance", "reverse proxy", "ssl"],
        priority=2,
        capabilities=["Nginx", "reverse proxy", "load balancing", "SSL"]
    ),
    UltimateSkill(
        name="ssl_certificates",
        category=SkillCategory.SECURITY,
        description="SSL/TLS certificates, HTTPS, Let's Encrypt",
        triggers=["ssl", "tls", "https", "certificate", "letsencrypt", "certbot"],
        priority=2,
        capabilities=["SSL", "TLS", "certificates", "HTTPS", "Let's Encrypt"]
    ),
    UltimateSkill(
        name="monitoring_observability",
        category=SkillCategory.MONITORING,
        description="Monitoring, logging, tracing, Prometheus, Grafana",
        triggers=["monitor", "log", "trace", "prometheus", "grafana", "datadog", "observability"],
        priority=2,
        capabilities=["monitoring", "logging", "tracing", "dashboards"]
    ),

    # ============ SECURITY (8 skills) ============
    UltimateSkill(
        name="security_scanning",
        category=SkillCategory.SECURITY,
        description="Security scanning, vulnerabilities, SAST, DAST",
        triggers=["security", "scan", "vulnerability", "sast", "dast", "snyk"],
        priority=1,
        capabilities=["SAST", "DAST", "vulnerability scanning", "Snyk"]
    ),
    UltimateSkill(
        name="input_validation",
        category=SkillCategory.SECURITY,
        description="Input validation, sanitization, XSS prevention",
        triggers=["validate", "sanitize", "xss", "injection", "input"],
        priority=1,
        capabilities=["validation", "sanitization", "XSS", "SQL injection"]
    ),
    UltimateSkill(
        name="cors_config",
        category=SkillCategory.SECURITY,
        description="CORS configuration, cross-origin requests",
        triggers=["cors", "cross-origin", "origin", "header", "access-control"],
        priority=1,
        capabilities=["CORS", "headers", "cross-origin", "whitelist"]
    ),
    UltimateSkill(
        name="encryption",
        category=SkillCategory.SECURITY,
        description="Encryption, hashing, password storage, bcrypt",
        triggers=["encrypt", "hash", "bcrypt", "password", "salt", "crypto"],
        priority=1,
        capabilities=["encryption", "hashing", "bcrypt", "AES"]
    ),
    UltimateSkill(
        name="api_security",
        category=SkillCategory.SECURITY,
        description="API security, API keys, scopes, permissions",
        triggers=["api key", "secret", "permission", "scope", "authorize"],
        priority=1,
        capabilities=["API keys", "scopes", "permissions", "OAuth"]
    ),
    UltimateSkill(
        name="dependency_security",
        category=SkillCategory.SECURITY,
        description="Dependency security, npm audit, security updates",
        triggers=["dependency", "npm audit", "vulnerable", "update", "audit"],
        priority=1,
        capabilities=["npm audit", "dependency updates", "vulnerabilities"]
    ),
    UltimateSkill(
        name="penetration_testing",
        category=SkillCategory.SECURITY,
        description="Penetration testing, OWASP, security headers",
        triggers=["pen test", "owasp", "security header", "x-frame", "hsts", "xss"],
        priority=2,
        capabilities=["OWASP", "security headers", "penetration testing"]
    ),
    UltimateSkill(
        name="secrets_management",
        category=SkillCategory.SECURITY,
        description="Secrets management, environment variables, Vault",
        triggers=["secret", "env variable", "vault", "aws secret", "dotenv"],
        priority=1,
        capabilities=["secrets", "environment variables", "Vault", "rotation"]
    ),

    # ============ AI/ML (8 skills) ============
    UltimateSkill(
        name="openai_integration",
        category=SkillCategory.AI_MODELS,
        description="OpenAI API integration, GPT models, embeddings",
        triggers=["openai", "gpt", "chatgpt", "dall-e", "whisper", "embedding"],
        priority=1,
        capabilities=["OpenAI API", "GPT", "embeddings", "fine-tuning"]
    ),
    UltimateSkill(
        name="anthropic_claude",
        category=SkillCategory.AI_MODELS,
        description="Anthropic Claude API integration",
        triggers=["claude", "anthropic", "artifacts"],
        priority=1,
        capabilities=["Claude API", "artifacts", "tool use", "context"]
    ),
    UltimateSkill(
        name="google_gemini",
        category=SkillCategory.AI_MODELS,
        description="Google Gemini API integration",
        triggers=["gemini", "google ai", "palm", "vertex"],
        priority=1,
        capabilities=["Gemini API", "multimodal", "vision", "context"]
    ),
    UltimateSkill(
        name="local_llm_ollama",
        category=SkillCategory.AI_MODELS,
        description="Local LLM with Ollama, self-hosted models",
        triggers=["ollama", "local llm", "llama", "mistral", "qwen", "self-hosted"],
        priority=1,
        capabilities=["Ollama", "local models", "Llama", "Mistral"]
    ),
    UltimateSkill(
        name="mcp_model_context",
        category=SkillCategory.AI_MODELS,
        description="Model Context Protocol integration",
        triggers=["mcp", "model context", "protocol", "tool"],
        priority=1,
        capabilities=["MCP", "protocol", "tool integration", "servers"]
    ),
    UltimateSkill(
        name="rag_implementation",
        category=SkillCategory.AI_MODELS,
        description="RAG (Retrieval Augmented Generation) implementation",
        triggers=["rag", "retrieval", "vector database", "embed", "chunk"],
        priority=2,
        capabilities=["RAG", "vector search", "embeddings", "retrieval"]
    ),
    UltimateSkill(
        name="ai_prompt_engineering",
        category=SkillCategory.AI_MODELS,
        description="AI prompt engineering, chain of thought, few-shot",
        triggers=["prompt", "chain of thought", "few-shot", "zero-shot", "cot"],
        priority=1,
        capabilities=["prompts", "CoT", "few-shot", "system prompts"]
    ),
    UltimateSkill(
        name="vector_database",
        category=SkillCategory.DATA_SCIENCE,
        description="Vector databases, Pinecone, Chroma, pgvector",
        triggers=["vector", "pinecone", "chroma", "pgvector", "embedding", "similarity"],
        priority=2,
        capabilities=["vector DB", "similarity search", "embeddings"]
    ),

    # ============ VERSION CONTROL & COLLABORATION (7 skills) ============
    UltimateSkill(
        name="git_operations",
        category=SkillCategory.VERSION_CONTROL,
        description="Git operations, branching, merging, rebasing",
        triggers=["git", "branch", "merge", "rebase", "commit", "push", "pull"],
        priority=1,
        capabilities=["Git", "branching", "merging", "rebasing"]
    ),
    UltimateSkill(
        name="github_pr_workflow",
        category=SkillCategory.VERSION_CONTROL,
        description="GitHub PR workflow, reviews, CI checks",
        triggers=["pull request", "pr", "review", "github", "merge", "draft"],
        priority=1,
        capabilities=["PR workflow", "code review", "checks", "merge"]
    ),
    UltimateSkill(
        name="code_review",
        category=SkillCategory.VERSION_CONTROL,
        description="Code review practices, feedback, quality",
        triggers=["review", "code review", "feedback", "quality", "linter"],
        priority=1,
        capabilities=["code review", "linting", "formatting", "quality gates"]
    ),
    UltimateSkill(
        name="monorepo_management",
        category=SkillCategory.VERSION_CONTROL,
        description="Monorepo management, Turborepo, Nx",
        triggers=["monorepo", "turborepo", "nx", "workspace", "shared"],
        priority=2,
        capabilities=["monorepo", "Turborepo", "Nx", "workspaces"]
    ),
    UltimateSkill(
        name="semantic_versioning",
        category=SkillCategory.VERSION_CONTROL,
        description="Semantic versioning, changelog, releases",
        triggers=["semver", "version", "release", "changelog", "tag"],
        priority=2,
        capabilities=["semantic versioning", "releases", "changelog"]
    ),
    UltimateSkill(
        name="git_hooks",
        category=SkillCategory.VERSION_CONTROL,
        description="Git hooks, pre-commit, lint-staged",
        triggers=["hook", "pre-commit", "post-commit", "lint-staged"],
        priority=2,
        capabilities=["Git hooks", "pre-commit", "automation"]
    ),
    UltimateSkill(
        name="conflict_resolution",
        category=SkillCategory.VERSION_CONTROL,
        description="Git conflict resolution, merge conflicts",
        triggers=["conflict", "merge conflict", "resolve", "ours", "theirs"],
        priority=1,
        capabilities=["conflict resolution", "merge", "diff"]
    ),

    # ============ DOCUMENTATION (5 skills) ============
    UltimateSkill(
        name="readme_documentation",
        category=SkillCategory.DOCUMENTATION,
        description="README documentation, badges, shields",
        triggers=["readme", "documentation", "badge", "shields", "license"],
        priority=1,
        capabilities=["README", "badges", "shields", "contributing"]
    ),
    UltimateSkill(
        name="api_documentation",
        category=SkillCategory.DOCUMENTATION,
        description="API documentation, Swagger, OpenAPI",
        triggers=["swagger", "openapi", "api doc", "swagger ui", "redoc"],
        priority=2,
        capabilities=["OpenAPI", "Swagger", "interactive docs"]
    ),
    UltimateSkill(
        name="inline_documentation",
        category=SkillCategory.DOCUMENTATION,
        description="Code documentation, JSDoc, docstrings",
        triggers=["jsdoc", "docstring", "comment", "type", "annotation"],
        priority=2,
        capabilities=["JSDoc", "docstrings", "type annotations"]
    ),
    UltimateSkill(
        name="changelog_management",
        category=SkillCategory.DOCUMENTATION,
        description="Changelog management, keep a changelog",
        triggers=["changelog", "keepachangelog", "release notes", "history"],
        priority=2,
        capabilities=["changelog", "releases", "version history"]
    ),
    UltimateSkill(
        name="contributing_guide",
        category=SkillCategory.DOCUMENTATION,
        description="Contributing guidelines, PR templates",
        triggers=["contributing", "pr template", "issue template", "template"],
        priority=2,
        capabilities=["contributing guide", "PR templates", "issue templates"]
    ),

    # ============ BUSINESS & ENTERPRISE (5 skills) ============
    UltimateSkill(
        name="presentation_creation",
        category=SkillCategory.BUSINESS,
        description="Presentation creation, slides, decks",
        triggers=["presentation", "slide", "deck", "powerpoint", "pitch"],
        priority=1,
        capabilities=["presentations", "slides", "deck creation"]
    ),
    UltimateSkill(
        name="email_templates",
        category=SkillCategory.BUSINESS,
        description="Email templates, HTML email, newsletters",
        triggers=["email", "newsletter", "html email", "mail", "campaign"],
        priority=2,
        capabilities=["HTML email", "templates", "responsive email"]
    ),
    UltimateSkill(
        name="business_documentation",
        category=SkillCategory.BUSINESS,
        description="Business documentation, proposals, specs",
        triggers=["proposal", "spec", "requirement", "business", "document"],
        priority=2,
        capabilities=["proposals", "specs", "requirements", "PRD"]
    ),
    UltimateSkill(
        name="markdown_authoring",
        category=SkillCategory.DOCUMENTATION,
        description="Markdown authoring, GitHub flavored markdown",
        triggers=["markdown", "md", "gfm", "github markdown", "readme"],
        priority=1,
        capabilities=["Markdown", "GFM", "tables", "code blocks"]
    ),
    UltimateSkill(
        name="seo_optimization",
        category=SkillCategory.BUSINESS,
        description="SEO optimization, meta tags, sitemap",
        triggers=["seo", "meta tag", "sitemap", "robots", "search"],
        priority=2,
        capabilities=["SEO", "meta tags", "sitemap", "robots.txt"]
    ),
]


# =============================================================================
# AUTO-TRIGGER SYSTEM
# =============================================================================

class SkillAutoTrigger:
    """
    Intelligent skill auto-trigger system.
    Automatically activates skills based on task context.
    Nothing remains unused - everything is called when needed.
    """
    
    def __init__(self):
        self.skills = ULTIMATE_SKILLS
        self.active_skills: List[UltimateSkill] = []
        self.usage_stats: Dict[str, int] = {}
        
    def analyze_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze a task and return all relevant skills with match scores.
        Automatically activates the most appropriate skills.
        """
        context = context or {}
        task_lower = task.lower()
        
        # Calculate match scores for all skills
        scored_skills = []
        for skill in self.skills:
            score = skill.matches_task(task)
            if score > 0:
                scored_skills.append((score, skill))
        
        # Sort by score descending
        scored_skills.sort(key=lambda x: (-x[0], x[1].priority))
        
        # Select top skills (max 10 for complex, 5 for simple)
        max_skills = 10 if context.get("complex", False) else 5
        selected = [skill for _, skill in scored_skills[:max_skills]]
        
        # Update usage stats
        for skill in selected:
            skill.usage_count += 1
            self.usage_stats[skill.name] = self.usage_stats.get(skill.name, 0) + 1
        
        self.active_skills = selected
        
        return {
            "task": task,
            "task_type": self._classify_task(task_lower),
            "selected_skills": [
                {
                    "name": s.name,
                    "category": s.category.value,
                    "description": s.description,
                    "match_score": s.matches_task(task),
                    "priority": s.priority,
                    "capabilities": s.capabilities,
                    "triggers": s.triggers
                }
                for s in selected
            ],
            "mcp_servers_needed": self._get_required_mcp_servers(selected),
            "ready_to_use": True
        }
    
    def _classify_task(self, task: str) -> str:
        """Classify the task type."""
        classifications = {
            "3d": "3D Graphics",
            "animation": "Animation",
            "frontend": "Frontend Development",
            "backend": "Backend Development",
            "database": "Database",
            "api": "API Development",
            "security": "Security",
            "devops": "DevOps",
            "ai": "AI/ML",
            "design": "Design"
        }
        
        for keyword, task_type in classifications.items():
            if keyword in task:
                return task_type
        
        return "General Development"
    
    def _get_required_mcp_servers(self, skills: List[UltimateSkill]) -> List[str]:
        """Get required MCP servers for selected skills."""
        servers = []
        for skill in skills:
            if skill.mcp_server:
                servers.append(skill.mcp_server)
        return list(set(servers))
    
    def get_skill_by_name(self, name: str) -> Optional[UltimateSkill]:
        """Get a specific skill by name."""
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None
    
    def get_skills_by_category(self, category: SkillCategory) -> List[UltimateSkill]:
        """Get all skills in a specific category."""
        return [s for s in self.skills if s.category == category]
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get skill usage statistics."""
        return self.usage_stats.copy()
    
    def suggest_skills_for_goal(self, goal: str) -> List[Dict]:
        """
        Suggest a sequence of skills to achieve a goal.
        Useful for complex multi-step tasks.
        """
        analysis = self.analyze_task(goal, {"complex": True})
        return analysis["selected_skills"]
    
    def generate_skill_report(self) -> str:
        """Generate a comprehensive skill report."""
        report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║             NEURO ULTIMATE - 100+ SKILLS REPORT                        ║
╚══════════════════════════════════════════════════════════════════════════╝

Total Skills: {len(self.skills)}

📊 BY CATEGORY:
"""
        
        categories = {}
        for skill in self.skills:
            cat = skill.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(skill)
        
        for cat, skills in sorted(categories.items()):
            report += f"\n  {cat.upper().replace('_', ' ')}: {len(skills)} skills\n"
        
        report += """
🏆 TOP SKILLS (Priority 1 - Critical):
"""
        
        priority_1 = [s for s in self.skills if s.priority == 1]
        for skill in priority_1[:10]:
            report += f"  • {skill.name} - {skill.description[:50]}...\n"
        
        report += """
🔧 HOW TO USE:
  from neuro.ultimate.skills_100 import SkillAutoTrigger
  trigger = SkillAutoTrigger()
  result = trigger.analyze_task("build a 3D website with GSAP animations")
"""
        
        return report


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_auto_trigger: Optional[SkillAutoTrigger] = None

def get_auto_trigger() -> SkillAutoTrigger:
    """Get or create the global auto-trigger instance."""
    global _auto_trigger
    if _auto_trigger is None:
        _auto_trigger = SkillAutoTrigger()
    return _auto_trigger


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def auto_detect_skills(task: str) -> Dict[str, Any]:
    """Auto-detect and return relevant skills for a task."""
    return get_auto_trigger().analyze_task(task)


def get_all_skills() -> List[UltimateSkill]:
    """Get all available skills."""
    return ULTIMATE_SKILLS


def get_skill_count() -> int:
    """Get total skill count."""
    return len(ULTIMATE_SKILLS)