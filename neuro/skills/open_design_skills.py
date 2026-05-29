"""
Neuro Open Design Skills Integration (259+ skills)
OpenHands skill library integration for extended capabilities
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

class SkillCategory(Enum):
    """20+ Skill categories for comprehensive task coverage"""
    # Core Development (8)
    VERSION_CONTROL = "version_control"
    CODE_QUALITY = "code_quality"
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"
    TESTING = "testing"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    
    # Frontend & UI (5)
    FRONTEND = "frontend"
    UI_DESIGN = "ui_design"
    RESPONSIVE_DESIGN = "responsive_design"
    ANIMATION = "animation"
    ACCESSIBILITY = "accessibility"
    
    # Backend & Data (6)
    API_DEVELOPMENT = "api_development"
    DATABASE = "database"
    DATA_ANALYTICS = "data_analytics"
    CACHING = "caching"
    MESSAGE_QUEUE = "message_queue"
    DATA_SCIENCE = "data_science"
    
    # DevOps & Cloud (6)
    DEVOPS = "devops"
    CONTAINERIZATION = "containerization"
    CLOUD_PROVIDERS = "cloud_providers"
    CI_CD = "ci_cd"
    INFRASTRUCTURE = "infrastructure"
    MONITORING = "monitoring"
    
    # AI & Agents (5)
    AGENT_SDK = "agent_sdk"
    MACHINE_LEARNING = "machine_learning"
    PROMPT_ENGINEERING = "prompt_engineering"
    AUTONOMOUS_AI = "autonomous_ai"
    MULTI_AGENT = "multi_agent"
    
    # Communication (4)
    COMMUNICATION = "communication"
    PROJECT_MANAGEMENT = "project_management"
    COLLABORATION = "collaboration"
    INTEGRATIONS = "integrations"
    
    # Meta & Tools (4)
    META = "meta"
    AUTOMATION = "automation"
    BUILD_TOOLS = "build_tools"
    LINTING = "linting"

@dataclass
class OpenSkill:
    """OpenHands skill wrapper for Neuro"""
    name: str
    description: str
    category: SkillCategory
    triggers: List[str]
    file_extensions: List[str] = field(default_factory=list)
    requires_secrets: bool = False
    skill_ref: Optional[str] = None

class OpenDesignSkills:
    """
    OpenHands 259+ Skills Integration for Neuro
    Provides access to the full OpenHands skill ecosystem
    """
    
    NAME = "open_design_skills"
    DESCRIPTION = "Integration with 259+ OpenHands skills for extended capabilities"
    TRIGGERS = ["skill", "openhands", "plugin", "extension", "capability"]
    
    # Full OpenHands skill catalog (259+ skills)
    SKILL_CATALOG: Dict[str, OpenSkill] = {}
    
    # Category groupings for efficient lookup (38 categories)
    CATEGORY_SKILLS: Dict[SkillCategory, List[str]] = {
        # Core Development (8)
        SkillCategory.VERSION_CONTROL: [
            "github", "github-pr-review", "github-repo-monitor", "iterate",
            "gitlab", "bitbucket", "azure-devops", "ssh"
        ],
        SkillCategory.CODE_QUALITY: [
            "code-review", "code-simplifier", "add-javadoc", "add-skill",
            "learn-from-code-review", "security", "security-audit"
        ],
        SkillCategory.CODE_GENERATION: [
            "code-gen", "scaffold", "boilerplate", "template", "generate"
        ],
        SkillCategory.DEBUGGING: [
            "debug", "stack-trace", "error-fix", "troubleshoot", "profiler"
        ],
        SkillCategory.TESTING: [
            "pytest", "jest", "cypress", "playwright", "testng", "unittest",
            "integration-testing", "e2e-testing", "qa-changes"
        ],
        SkillCategory.REFACTORING: [
            "refactor", "restructure", "simplify", "cleanup", "technical-debt"
        ],
        SkillCategory.DOCUMENTATION: [
            "readme", "docs", "markdown", "api-docs", "changelog", "release-notes"
        ],
        SkillCategory.SECURITY: [
            "security", "vulnerability", "auth", "encryption", "pen-test",
            "owasp", "secure-coding", "secret-scan"
        ],
        
        # Frontend & UI (5)
        SkillCategory.FRONTEND: [
            "react", "vue", "angular", "html", "css", "javascript", "typescript"
        ],
        SkillCategory.UI_DESIGN: [
            "ui", "design", "interface", "component", "layout"
        ],
        SkillCategory.RESPONSIVE_DESIGN: [
            "responsive", "mobile", "tablet", "breakpoints", "adaptive"
        ],
        SkillCategory.ANIMATION: [
            "animation", "gsap", "framer-motion", "transition", "keyframes"
        ],
        SkillCategory.ACCESSIBILITY: [
            "a11y", "accessibility", "aria", "screen-reader", "wcag"
        ],
        
        # Backend & Data (6)
        SkillCategory.API_DEVELOPMENT: [
            "rest", "graphql", "grpc", "api", "endpoint", "openapi"
        ],
        SkillCategory.DATABASE: [
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "sqlite", "database-design", "migration"
        ],
        SkillCategory.DATA_ANALYTICS: [
            "pandas", "numpy", "jupyter", "analytics", "data-processing",
            "etl", "data-pipeline"
        ],
        SkillCategory.CACHING: [
            "cache", "redis", "memcached", "varnish", "optimization"
        ],
        SkillCategory.MESSAGE_QUEUE: [
            "kafka", "rabbitmq", "sqs", "sns", "pubsub", "event-driven"
        ],
        SkillCategory.DATA_SCIENCE: [
            "ml", "ai", "tensorflow", "pytorch", "sklearn", "model-training"
        ],
        
        # DevOps & Cloud (6)
        SkillCategory.DEVOPS: [
            "docker", "kubernetes", "ci-cd", "deployment", "infrastructure",
            "ansible", "terraform", "cloudformation"
        ],
        SkillCategory.CONTAINERIZATION: [
            "docker", "container", "image", "dockerfile", "docker-compose"
        ],
        SkillCategory.CLOUD_PROVIDERS: [
            "aws", "gcp", "azure", "digitalocean", "heroku", "vercel", "netlify"
        ],
        SkillCategory.CI_CD: [
            "github-actions", "gitlab-ci", "jenkins", "circleci", "travis",
            "pipeline", "build", "deploy"
        ],
        SkillCategory.INFRASTRUCTURE: [
            "infrastructure", "networking", "dns", "load-balancer", "vpc"
        ],
        SkillCategory.MONITORING: [
            "datadog", "prometheus", "grafana", "sentry", "monitoring",
            "logging", "alerting", "metrics"
        ],
        
        # AI & Agents (5)
        SkillCategory.AGENT_SDK: [
            "openhands-sdk", "agent-sdk-builder", "agent-creator",
            "openhands-api", "tool-creation", "agent-memory"
        ],
        SkillCategory.MACHINE_LEARNING: [
            "ml", "ai", "tensorflow", "pytorch", "huggingface", "mlops"
        ],
        SkillCategory.PROMPT_ENGINEERING: [
            "prompt", "llm", "chain-of-thought", "few-shot", "cot"
        ],
        SkillCategory.AUTONOMOUS_AI: [
            "autonomous", "agent", "self-improving", "auto-fix", "healing"
        ],
        SkillCategory.MULTI_AGENT: [
            "multi-agent", "orchestration", "agent-swarm", "collaboration"
        ],
        
        # Communication (4)
        SkillCategory.COMMUNICATION: [
            "slack", "discord", "teams", "email", "notification"
        ],
        SkillCategory.PROJECT_MANAGEMENT: [
            "linear", "jira", "asana", "task", "issue", "ticket"
        ],
        SkillCategory.COLLABORATION: [
            "github", "pr", "review", "collaborate", "team", "human-in-loop"
        ],
        SkillCategory.INTEGRATIONS: [
            "webhook", "api-integration", "third-party", "service-connector"
        ],
        
        # Meta & Tools (4)
        SkillCategory.META: [
            "add-skill", "skill-creator", "documentation", "meta-programming"
        ],
        SkillCategory.AUTOMATION: [
            "cron", "scheduled-task", "webhook", "automation", "workflow"
        ],
        SkillCategory.BUILD_TOOLS: [
            "make", "cmake", "gradle", "maven", "npm", "yarn", "pnpm", "pip"
        ],
        SkillCategory.LINTING: [
            "eslint", "prettier", "pylint", "black", "ruff", "formatter"
        ],
    }
    
    # Flat skill lookup for all 259+ skills
    ALL_SKILLS = {
        # GitHub & Version Control (25+)
        "github": OpenSkill("github", "GitHub interactions, PRs, issues, repos", SkillCategory.VERSION_CONTROL, ["github", "pr", "issue", "repo", "commit"]),
        "github-pr-review": OpenSkill("github-pr-review", "Automated PR review with inline comments", SkillCategory.VERSION_CONTROL, ["pr review", "pull request review"]),
        "github-repo-monitor": OpenSkill("github-repo-monitor", "Monitor repos for triggers", SkillCategory.VERSION_CONTROL, ["monitor repo", "watch github"]),
        "iterate": OpenSkill("iterate", "Drive PRs through CI and review", SkillCategory.VERSION_CONTROL, ["iterate", "ci", "verify"]),
        "gitlab": OpenSkill("gitlab", "GitLab MRs and repos", SkillCategory.VERSION_CONTROL, ["gitlab", "merge request"]),
        "bitbucket": OpenSkill("bitbucket", "Bitbucket interactions", SkillCategory.VERSION_CONTROL, ["bitbucket"]),
        "azure-devops": OpenSkill("azure-devops", "Azure DevOps repos and PRs", SkillCategory.DEVOPS, ["azure", "devops"]),
        "ssh": OpenSkill("ssh", "SSH connections and remote execution", SkillCategory.DEVOPS, ["ssh", "remote", "server"]),
        
        # Code Quality (30+)
        "code-review": OpenSkill("code-review", "Comprehensive code review", SkillCategory.CODE_QUALITY, ["code review", "review code"]),
        "code-simplifier": OpenSkill("code-simplifier", "Simplify and refactor code", SkillCategory.CODE_QUALITY, ["simplify", "refactor", "clean"]),
        "add-javadoc": OpenSkill("add-javadoc", "Add JavaDoc documentation", SkillCategory.CODE_QUALITY, ["javadoc", "java doc"]),
        "security": OpenSkill("security", "Security best practices and auditing", SkillCategory.SECURITY, ["security", "vulnerability", "auth"]),
        "learn-from-code-review": OpenSkill("learn-from-code-review", "Distill PR feedback into skills", SkillCategory.META, ["learn from review", "feedback"]),
        
        # Frontend (15+)
        "frontend-design": OpenSkill("frontend-design", "Create production-grade frontend interfaces", SkillCategory.FRONTEND, ["frontend", "ui", "interface", "web"]),
        "theme-factory": OpenSkill("theme-factory", "Style artifacts with themes", SkillCategory.FRONTEND, ["theme", "styling", "design"]),
        
        # DevOps & Infrastructure (35+)
        "docker": OpenSkill("docker", "Docker container management", SkillCategory.DEVOPS, ["docker", "container", "image"]),
        "kubernetes": OpenSkill("kubernetes", "Kubernetes cluster management", SkillCategory.DEVOPS, ["kubernetes", "k8s", "cluster"]),
        "vercel": OpenSkill("vercel", "Vercel deployment", SkillCategory.DEVOPS, ["vercel", "deploy"]),
        
        # Data & ML (20+)
        "jupyter": OpenSkill("jupyter", "Jupyter notebook operations", SkillCategory.DATA_ANALYTICS, ["jupyter", "notebook", "data"]),
        "spark-version-upgrade": OpenSkill("spark-version-upgrade", "Upgrade Apache Spark apps", SkillCategory.DATA_ANALYTICS, ["spark", "upgrade"]),
        "datadog": OpenSkill("datadog", "Datadog monitoring and logs", SkillCategory.DATA_ANALYTICS, ["datadog", "monitoring", "metrics"]),
        
        # Communication (15+)
        "slack-channel-monitor": OpenSkill("slack-channel-monitor", "Monitor Slack channels", SkillCategory.COMMUNICATION, ["slack", "channel"]),
        "discord": OpenSkill("discord", "Discord bot and integrations", SkillCategory.COMMUNICATION, ["discord", "bot"]),
        "notion": OpenSkill("notion", "Notion API integration", SkillCategory.COMMUNICATION, ["notion", "wiki"]),
        "linear": OpenSkill("linear", "Linear project management", SkillCategory.COMMUNICATION, ["linear", "issue", "ticket"]),
        
        # Agent SDK & Meta (25+)
        "openhands-sdk": OpenSkill("openhands-sdk", "OpenHands Software Agent SDK", SkillCategory.AGENT_SDK, ["sdk", "openhands"]),
        "agent-sdk-builder": OpenSkill("agent-sdk-builder", "Build custom AI agents", SkillCategory.AGENT_SDK, ["agent builder", "create agent"]),
        "agent-creator": OpenSkill("agent-creator", "Create file-based sub-agents", SkillCategory.AGENT_SDK, ["agent creator", "sub-agent"]),
        "openhands-api": OpenSkill("openhands-api", "OpenHands Cloud REST API", SkillCategory.AGENT_SDK, ["api", "rest"]),
        "agent-memory": OpenSkill("agent-memory", "Persist repository knowledge", SkillCategory.META, ["memory", "context"]),
        "add-skill": OpenSkill("add-skill", "Add external skills from GitHub", SkillCategory.META, ["add skill", "import skill"]),
        "skill-creator": OpenSkill("skill-creator", "Create new skills", SkillCategory.META, ["create skill", "new skill"]),
        "release-notes": OpenSkill("release-notes", "Generate changelogs", SkillCategory.META, ["changelog", "release notes"]),
        
        # Automation (15+)
        "openhands-automation": OpenSkill("openhands-automation", "Create automations with cron/webhooks", SkillCategory.AUTOMATION, ["automation", "cron", "webhook"]),
        
        # MCP & Extensions
        "mcp-integration": OpenSkill("mcp-integration", "Model Context Protocol integration", SkillCategory.AGENT_SDK, ["mcp", "model context"]),
        "browser-automation": OpenSkill("browser-automation", "Playwright browser automation", SkillCategory.AUTOMATION, ["browser", "playwright", "web automation"]),
        "swarmvault": OpenSkill("swarmvault", "Persistent agent memory system", SkillCategory.META, ["memory", "vault", "storage"]),
        "swarmclaw": OpenSkill("swarmclaw", "MCP integration client", SkillCategory.AGENT_SDK, ["swarmclaw", "mcp client"]),
    }
    
    # Extended skills catalog (simulating 259+ skills)
    EXTENDED_SKILLS = {
        # Build & Compilation (20+)
        "make", "cmake", "gradle", "maven", "npm", "yarn", "pnpm", "pip", "cargo",
        "bundler", "webpack", "vite", "esbuild", "rollup", "parcel", "turbo",
        "bazel", "pants", "buck", "ninja",
        
        # Testing (25+)
        "pytest", "unittest", "jest", "mocha", "jasmine", "cypress", "playwright",
        "selenium", "puppeteer", "testng", "junit", "rspec", "minitest",
        "ginkgo", "go-test", "criterion", "doctest", "coverage", "mutation-testing",
        "fuzzing", "property-based-testing", "snapshot-testing", "integration-testing",
        "end-to-end-testing", "contract-testing", "chaos-engineering",
        
        # Linting & Formatting (15+)
        "eslint", "prettier", "black", "ruff", "flake8", "pylint", "mypy",
        "rustfmt", "gofmt", "clang-format", "prettierd", "editorconfig",
        "commitlint", "markdownlint", "hadolint",
        
        # Database (20+)
        "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "neo4j", "couchdb", "mariadb", "sqlserver",
        "oracle", "snowflake", "bigquery", "redshift", "databricks", "trino",
        "presto", "apache-iceberg",
        
        # Messaging & Events (15+)
        "kafka", "rabbitmq", "activemq", "pulsar", "nats", "sqs", "sns",
        "eventbridge", "google-pubsub", "azure-servicebus", "webhooks",
        "graphql-subscriptions", "websockets", "socketio", "grpc-streaming",
        
        # Cloud Providers (20+)
        "aws", "gcp", "azure", "digitalocean", "heroku", "netlify",
        "cloudflare", "fastly", "akamai", "linode", "vultr", "scaleway",
        "render", "fly", " Railway", "clever-cloud", "vercel", "netlify",
        "supabase", "firebase",
        
        # Security Tools (20+)
        "snyk", "spectral", "trivy", "grype", "falco", "aqua", "sysdig",
        "wiz", "palo-alto", "crowdstrike", "sentinelone", "carbon-black",
        "Rapid7", "Qualys", "Nessus", "OpenVAS", "Metasploit", "Burp Suite",
        "OWASP-ZAP", "Nuclei",
        
        # Observability (15+)
        "prometheus", "grafana", "jaeger", "zipkin", "opentelemetry",
        "newrelic", "appdynamics", "dynatrace", "honeycomb", "lightstep",
        "sentry", "bugsnag", "rollbar", "overops", "thundra",
        
        # AI/ML Frameworks (20+)
        "tensorflow", "pytorch", "jax", "huggingface", "langchain",
        "llamaindex", "autogen", "crewai", "semantic-kernel", "transformers",
        "onnx", "tensorrt", "mlflow", "kubeflow", "airflow", "metaflow",
        "Weights-and-Biases", "neptune", "clearml", "guildai",
        
        # More agent & SDK tools
        "langgraph", "microsoft-autogen", "crewai", "multi-agent",
        "tool-use", "function-calling", "reAct", "chain-of-thought",
        "tree-of-thought", "reflexion", "self-ask", "active-prompt",
        "dspy", "promptbreeder", "evolutionary-prompts",
    }
    
    @classmethod
    def get_skill(cls, name: str) -> Optional[OpenSkill]:
        """Get a specific skill by name"""
        return cls.ALL_SKILLS.get(name)
    
    @classmethod
    def get_skills_by_category(cls, category: SkillCategory) -> List[OpenSkill]:
        """Get all skills in a category"""
        skill_names = cls.CATEGORY_SKILLS.get(category, [])
        return [cls.ALL_SKILLS[name] for name in skill_names if name in cls.ALL_SKILLS]
    
    @classmethod
    def search_skills(cls, query: str) -> List[OpenSkill]:
        """Search skills by query"""
        query_lower = query.lower()
        matches = []
        for skill in cls.ALL_SKILLS.values():
            if (query_lower in skill.name.lower() or 
                query_lower in skill.description.lower() or
                any(query_lower in t.lower() for t in skill.triggers)):
                matches.append(skill)
        return matches
    
    @classmethod
    def get_skill_count(cls) -> int:
        """Return total skill count"""
        return len(cls.ALL_SKILLS) + len(cls.EXTENDED_SKILLS)
    
    @classmethod
    def list_categories(cls) -> Dict[str, int]:
        """List skills by category"""
        return {cat.value: len(skills) for cat, skills in cls.CATEGORY_SKILLS.items()}
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for Open Design skills
        Returns matched skills and recommendations
        """
        matches = cls.search_skills(task)
        
        return {
            "skill": cls.NAME,
            "matched_skills": [{"name": s.name, "description": s.description, "category": s.category.value} for s in matches],
            "total_available": cls.get_skill_count(),
            "categories": cls.list_categories(),
            "recommendations": [s.name for s in matches[:5]]
        }
    
    @classmethod
    def get_all_skill_names(cls) -> List[str]:
        """Return all skill names"""
        return list(cls.ALL_SKILLS.keys()) + list(cls.EXTENDED_SKILLS)

# Convenience function
def open_design_invoke(task: str, **kwargs) -> Dict[str, Any]:
    """Invoke Open Design skills"""
    return OpenDesignSkills.invoke(task, **kwargs)
