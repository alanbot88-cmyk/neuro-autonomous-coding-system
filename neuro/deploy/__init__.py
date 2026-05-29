"""
Deployment Module - Auto-select and deploy apps to cloud platforms
"""

import subprocess
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class DeploymentConfig:
    """Configuration for deployment."""
    platform: str
    project_dir: str
    env_vars: Dict[str, str]
    build_command: str
    start_command: str
    region: str = "us-east-1"


@dataclass
class DeploymentResult:
    """Result from a deployment."""
    success: bool
    url: Optional[str] = None
    platform: str = ""
    message: str = ""
    instructions: List[str] = None
    error: Optional[str] = None


class DeploymentSelector:
    """Select best deployment platform based on app characteristics."""
    
    def select(self, project_dir: str = ".", env_vars: Dict[str, str] = None) -> str:
        """Auto-select best platform for the project."""
        has_files = self._detect_file_types(project_dir)
        
        # Priority order based on stack detection
        if has_files.get("nextjs") or has_files.get("react"):
            return "vercel"
        elif has_files.get("python") and has_files.get("postgres_schema"):
            return "railway"
        elif has_files.get("python"):
            return "render"
        elif has_files.get("static"):
            return "netlify"
        elif has_files.get("dockerfile"):
            return "docker"
        elif has_files.get("node"):
            return "render"
        else:
            return "vercel"  # Default
    
    def _detect_file_types(self, project_dir: str) -> Dict[str, bool]:
        """Detect file types to determine stack."""
        files = {}
        path = Path(project_dir)
        
        files["package_json"] = (path / "package.json").exists()
        files["nextjs"] = files["package_json"] and (path / "next.config.js").exists()
        files["react"] = files["package_json"] and not files["nextjs"]
        files["python"] = (path / "requirements.txt").exists() or (path / "pyproject.toml").exists()
        files["fastapi"] = files["python"] and (path / "app.py").exists() or (path / "main.py").exists()
        files["django"] = files["python"] and (path / "manage.py").exists()
        files["flask"] = files["python"] and not files["django"] and not files["fastapi"]
        files["postgres_schema"] = files["python"] and (path / "alembic.ini").exists()
        files["static"] = (path / "index.html").exists() and not files["package_json"]
        files["dockerfile"] = (path / "Dockerfile").exists() or (path / "docker-compose.yml").exists()
        files["node"] = files["package_json"] and (path / "server.js").exists() or (path / "index.js").exists()
        
        return files


class VercelDeployer:
    """Deploy to Vercel."""
    
    name = "vercel"
    
    def is_configured(self) -> bool:
        """Check if Vercel CLI or API token is available."""
        has_token = bool(os.getenv("VERCEL_TOKEN"))
        has_cli = False
        try:
            result = subprocess.run(
                ["vercel", "--version"],
                capture_output=True,
                timeout=5,
            )
            has_cli = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return has_token or has_cli
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> DeploymentResult:
        """Deploy to Vercel."""
        token = os.getenv("VERCEL_TOKEN")
        
        has_cli = False
        try:
            result = subprocess.run(
                ["vercel", "--version"],
                capture_output=True,
                timeout=5,
            )
            has_cli = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        if token:
            # API-based deployment
            return self._deploy_via_api(project_dir, token, env_vars or {})
        elif has_cli:
            # CLI-based deployment
            return self._deploy_via_cli(project_dir, env_vars or {})
        else:
            # No credentials - generate instructions
            return DeploymentResult(
                success=False,
                platform="vercel",
                message="No Vercel credentials found",
                instructions=[
                    "1. Install Vercel CLI: npm install -g vercel",
                    "2. Login: vercel login",
                    "3. Deploy: vercel --prod",
                    "4. Set environment variables in Vercel dashboard",
                ]
            )
    
    def _deploy_via_api(self, project_dir: str, token: str, env_vars: Dict[str, str]) -> DeploymentResult:
        """Deploy using Vercel API."""
        try:
            import requests
            
            # Create deployment
            response = requests.post(
                "https://api.vercel.com/v13/deployments",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "name": Path(project_dir).name,
                    "gitSource": {
                        "type": "github",
                        "repo": f"username/{Path(project_dir).name}",
                    }
                }
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return DeploymentResult(
                    success=True,
                    url=f"https://{data.get('url', 'app.vercel.app')}",
                    platform="vercel",
                    message="Deployed via Vercel API"
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="vercel",
                    error=f"API error: {response.status_code}"
                )
        except Exception as e:
            return DeploymentResult(success=False, platform="vercel", error=str(e))
    
    def _deploy_via_cli(self, project_dir: str, env_vars: Dict[str, str]) -> DeploymentResult:
        """Deploy using Vercel CLI."""
        try:
            cmd = ["vercel", "--prod", "--yes"]
            
            proc = subprocess.Popen(
                cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = proc.communicate(timeout=120)
            
            if proc.returncode == 0:
                url = stdout.strip().split("\n")[-1]
                return DeploymentResult(
                    success=True,
                    url=url,
                    platform="vercel",
                    message="Deployed via Vercel CLI"
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="vercel",
                    error=stderr or "Deployment failed"
                )
        except subprocess.TimeoutExpired:
            return DeploymentResult(success=False, platform="vercel", error="Deployment timed out")
        except Exception as e:
            return DeploymentResult(success=False, platform="vercel", error=str(e))
    
    def generate_env_example(self) -> str:
        return """# Vercel Environment Variables
# Add these in Vercel Dashboard > Settings > Environment Variables
DATABASE_URL=
NEXTAUTH_SECRET=
NEXTAUTH_URL=https://your-app.vercel.app
"""


class RailwayDeployer:
    """Deploy to Railway (via API)."""
    
    name = "railway"
    
    def is_configured(self) -> bool:
        return bool(os.getenv("RAILWAY_TOKEN"))
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> DeploymentResult:
        """Deploy to Railway."""
        token = os.getenv("RAILWAY_TOKEN")
        
        if not token:
            return DeploymentResult(
                success=False,
                platform="railway",
                message="No Railway token found",
                instructions=[
                    "1. Get Railway token: railway.me > Settings > Tokens",
                    "2. Export: export RAILWAY_TOKEN=your_token",
                    "3. Install CLI: npm install -g @railway/cli",
                    "4. Deploy: railway up",
                    "5. Link project: railway link",
                ]
            )
        
        # API-based deployment
        try:
            import requests
            
            response = requests.post(
                "https://backboard.railway.dev/v2/deployments",
                headers={"Authorization": f"Bearer {token}"},
                json={"service": "web"},
            )
            
            if response.status_code in [200, 201]:
                return DeploymentResult(
                    success=True,
                    platform="railway",
                    message="Deployment initiated via Railway API"
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="railway",
                    error=f"API error: {response.status_code}"
                )
        except Exception as e:
            return DeploymentResult(success=False, platform="railway", error=str(e))
    
    def generate_env_example(self) -> str:
        return """# Railway Environment Variables
# Set via: railway variables add KEY=value
DATABASE_URL=postgres://...
SECRET_KEY=generate-a-random-key
DEBUG=false
PORT=8000
"""


class RenderDeployer:
    """Deploy to Render (via API)."""
    
    name = "render"
    
    def is_configured(self) -> bool:
        return bool(os.getenv("RENDER_API_KEY"))
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> DeploymentResult:
        """Deploy to Render."""
        api_key = os.getenv("RENDER_API_KEY")
        
        if not api_key:
            return DeploymentResult(
                success=False,
                platform="render",
                message="No Render API key found",
                instructions=[
                    "1. Get API key: dashboard.render.com > API Keys",
                    "2. Export: export RENDER_API_KEY=your_key",
                    "3. Create blueprint: render.yaml in project",
                    "4. Auto-deploy from GitHub",
                    "5. Set environment variables in dashboard",
                ]
            )
        
        try:
            import requests
            
            # Create web service
            response = requests.post(
                "https://api.render.com/v1/services",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "serviceType": "web",
                    "name": Path(project_dir).name,
                    "env": "python",
                }
            )
            
            if response.status_code in [200, 201]:
                return DeploymentResult(
                    success=True,
                    platform="render",
                    message="Service created via Render API"
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="render",
                    error=f"API error: {response.status_code}"
                )
        except Exception as e:
            return DeploymentResult(success=False, platform="render", error=str(e))
    
    def generate_env_example(self) -> str:
        return """# Render Environment Variables
DATABASE_URL=postgres://...
SECRET_KEY=generate-random-key
FLASK_ENV=production
"""


class DockerDeployer:
    """Deploy using Docker (local or cloud)."""
    
    name = "docker"
    
    def is_configured(self) -> bool:
        installed = False
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5,
            )
            installed = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return installed
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> DeploymentResult:
        """Generate Dockerfile and docker-compose."""
        if not self.is_configured():
            return DeploymentResult(
                success=False,
                platform="docker",
                message="Docker not installed",
                instructions=[
                    "1. Install Docker: docker.com/get-started",
                    "2. Build: docker build -t myapp .",
                    "3. Run: docker run -p 3000:3000 myapp",
                    "4. Push to registry: docker push myapp:latest",
                    "5. Deploy to cloud: Use Cloud-specific commands",
                ]
            )
        
        dockerfile = self._generate_dockerfile(project_dir)
        compose = self._generate_compose()
        
        return DeploymentResult(
            success=True,
            platform="docker",
            message="Docker configuration generated",
            instructions=[
                f"1. Create Dockerfile:\n{dockerfile}",
                "2. Build image: docker build -t myapp .",
                "3. Run locally: docker-compose up",
                "4. Push to registry: docker push myregistry/myapp",
            ]
        )
    
    def _generate_dockerfile(self, project_dir: str) -> str:
        has_package = Path(project_dir).joinpath("package.json").exists()
        has_req = Path(project_dir).joinpath("requirements.txt").exists()
        
        if has_package:
            return '''FROM node:18-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
ENV NODE_ENV=production
CMD ["npm", "start"]'''
        elif has_req:
            return '''FROM python:3.11-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]'''
        else:
            return '''FROM alpine:latest
WORKDIR /app
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]'''
    
    def _generate_compose(self) -> str:
        return '''version: "3.8"
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/db
    depends_on:
      db:
        image: postgres:15
        environment:
          POSTGRES_DB: app
          POSTGRES_PASSWORD: secret
        volumes:
          - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:'''


class NetlifyDeployer:
    """Deploy to Netlify."""
    
    name = "netlify"
    
    def is_configured(self) -> bool:
        return bool(os.getenv("NETLIFY_AUTH_TOKEN"))
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> DeploymentResult:
        token = os.getenv("NETLIFY_AUTH_TOKEN")
        site_id = os.getenv("NETLIFY_SITE_ID")
        
        if not token:
            return DeploymentResult(
                success=False,
                platform="netlify",
                message="No Netlify auth token found",
                instructions=[
                    "1. Get auth token: app.netlify.com > User settings > OAuth",
                    "2. Export: export NETLIFY_AUTH_TOKEN=your_token",
                    "3. Install CLI: npm install -g netlify-cli",
                    "4. Deploy: netlify deploy --prod --dir=build",
                ]
            )
        
        # Build first
        build_result = subprocess.run(
            ["npm", "run", "build"] if Path(project_dir).joinpath("package.json").exists() else ["echo", "No build needed"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        
        if build_result.returncode != 0:
            return DeploymentResult(
                success=False,
                platform="netlify",
                error="Build failed"
            )
        
        try:
            import requests
            
            response = requests.post(
                "https://api.netlify.com/api/v1/sites",
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code == 201:
                data = response.json()
                return DeploymentResult(
                    success=True,
                    url=data.get("ssl_url", data.get("url")),
                    platform="netlify",
                    message="Site created via Netlify API"
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="netlify",
                    error=f"API error: {response.status_code}"
                )
        except Exception as e:
            return DeploymentResult(success=False, platform="netlify", error=str(e))
    
    def generate_env_example(self) -> str:
        return """# Netlify Environment Variables
HUGO_VERSION=0.80.0
"""


class ReplitDeployer:
    """Deploy to Replit."""
    
    name = "replit"
    
    def is_configured(self) -> bool:
        return bool(os.getenv("REPLIT_CLI_TOKEN"))
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> DeploymentResult:
        return DeploymentResult(
            success=False,
            platform="replit",
            message="Replit deployment requires manual import",
            instructions=[
                "1. Go to replit.com and create new project",
                "2. Import from GitHub: Import from repo > Select repository",
                "3. Set language and run command in .replit file",
                "4. Click Run button",
                "5. For production: Upgrade to paid plan",
            ]
        )
    
    def generate_env_example(self) -> str:
        return """# Replit Secrets
# Add via: Secrets tab in Replit project
DATABASE_URL=
SECRET_KEY=
"""


# Registry of deployers
DEPLOYERS = {
    "vercel": VercelDeployer,
    "railway": RailwayDeployer,
    "render": RenderDeployer,
    "docker": DockerDeployer,
    "netlify": NetlifyDeployer,
    "replit": ReplitDeployer,
}

# Platform priorities by stack
PLATFORM_PRIORITY = {
    "nextjs": ["vercel", "netlify", "docker"],
    "react": ["vercel", "render", "netlify"],
    "fastapi": ["railway", "render", "docker"],
    "django": ["railway", "render", "docker"],
    "flask": ["render", "railway", "docker"],
    "static": ["netlify", "vercel", "github-pages"],
    "node": ["vercel", "render", "railway"],
}


def select_best_platform(project_dir: str = ".") -> str:
    """Auto-select best platform for the project."""
    selector = DeploymentSelector()
    return selector.select(project_dir)


def deploy_app(
    platform: Optional[str] = None,
    project_dir: str = ".",
    env_vars: Dict[str, str] = None,
    auto_select: bool = True,
) -> DeploymentResult:
    """
    Deploy application - auto-selects best platform by default.
    
    Usage:
        from neuro.deploy import deploy_app
        
        # Auto-select best platform
        result = deploy_app(project_dir="./my-app")
        
        # Specific platform
        result = deploy_app(platform="vercel", project_dir="./my-app")
    """
    # Auto-select if no platform specified
    if not platform or auto_select:
        platform = select_best_platform(project_dir)
    
    deployer_class = DEPLOYERS.get(platform.lower())
    if not deployer_class:
        return DeploymentResult(
            success=False,
            platform=platform or "unknown",
            error=f"Unknown platform: {platform}",
            instructions=[f"Available platforms: {list(DEPLOYERS.keys())}"]
        )
    
    deployer = deployer_class()
    return deployer.deploy(project_dir, env_vars)


def auto_deploy(project_dir: str = ".") -> DeploymentResult:
    """
    Fully automatic deployment with platform auto-selection.
    Tries each configured platform until one succeeds.
    
    Usage:
        from neuro.deploy import auto_deploy
        
        result = auto_deploy("./my-app")
        if result.success:
            print(f"Deployed to: {result.url}")
        else:
            print(f"Instructions: {result.instructions}")
    """
    # First, auto-select best platform
    best_platform = select_best_platform(project_dir)
    
    # Try the best platform first
    result = deploy_app(platform=best_platform, project_dir=project_dir)
    if result.success:
        return result
    
    # Fallback: try other platforms with available credentials
    for platform_name, deployer_class in DEPLOYERS.items():
        if platform_name == best_platform:
            continue
        
        deployer = deployer_class()
        if deployer.is_configured():
            result = deployer.deploy(project_dir)
            if result.success:
                return result
    
    # No platform configured - return instructions for best platform
    deployer = DEPLOYERS[best_platform]()
    return DeploymentResult(
        success=False,
        platform=best_platform,
        message=f"Auto-deploy unable to complete. Set credentials and try again.",
        instructions=deployer.generate_env_example().strip().split("\n")
    )


def generate_deployment_files(
    platform: str,
    project_dir: str,
) -> Dict[str, str]:
    """Generate deployment configuration files."""
    deployer_class = DEPLOYERS.get(platform.lower())
    if not deployer_class:
        return {"error": f"Unknown platform: {platform}"}
    
    deployer = deployer_class()
    
    files = {
        ".env.example": deployer.generate_env_example(),
    }
    
    # Add platform-specific config
    if platform == "render":
        files["render.yaml"] = '''python:
  version: "latest"
  buildCommand: "pip install -r requirements.txt"
  startCommand: "gunicorn app:app --bind :$PORT"
  healthCheckPath: "/health"'''
    
    return files


def list_platforms() -> List[str]:
    """List available deployment platforms."""
    return list(DEPLOYERS.keys())


def get_configured_platforms() -> List[str]:
    """Get list of platforms with credentials configured."""
    configured = []
    for platform_name, deployer_class in DEPLOYERS.items():
        deployer = deployer_class()
        if deployer.is_configured():
            configured.append(platform_name)
    return configured
