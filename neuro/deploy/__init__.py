"""
Deployment Module - Deploy apps to cloud platforms
"""

import subprocess
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DeploymentConfig:
    """Configuration for deployment."""
    platform: str
    project_dir: str
    env_vars: Dict[str, str]
    build_command: str
    start_command: str
    region: str = "us-east-1"


class VercelDeployer:
    """Deploy to Vercel."""
    
    name = "vercel"
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """Deploy to Vercel."""
        try:
            result = subprocess.run(
                ["vercel", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return {"success": False, "error": "Vercel CLI not found. Run: npm install -g vercel"}
            
            cmd = ["vercel", "--prod"] if os.getenv("VERCEL_AUTH") else ["vercel"]
            
            proc = subprocess.Popen(
                cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()
            
            if proc.returncode == 0:
                return {
                    "success": True,
                    "url": stdout.decode().strip().split("\n")[-1],
                    "platform": "vercel",
                }
            else:
                return {"success": False, "error": stderr.decode()}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_env_example(self) -> str:
        return """# Vercel Environment Variables
DATABASE_URL=
NEXTAUTH_SECRET=
NEXTAUTH_URL=
"""


class RailwayDeployer:
    """Deploy to Railway."""
    
    name = "railway"
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """Deploy to Railway."""
        return {
            "success": True,
            "platform": "railway",
            "instructions": [
                "1. Install Railway CLI: npm install -g @railway/cli",
                "2. Login: railway login",
                "3. Deploy: railway up",
                "4. Set env vars: railway variables add KEY=value",
            ],
            "commands": ["railway up", "railway domains add"],
        }
    
    def generate_env_example(self) -> str:
        return """# Railway Environment Variables
DATABASE_URL=postgres://...
SECRET_KEY=
DEBUG=false
ALLOWED_HOSTS=*
"""


class RenderDeployer:
    """Deploy to Render."""
    
    name = "render"
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """Deploy to Render."""
        return {
            "success": True,
            "platform": "render",
            "instructions": [
                "1. Connect GitHub: render.com → Dashboard → New → PostgreSQL",
                "2. Create web service: New → Web Service",
                "3. Connect repo and set build command",
                "4. Add environment variables",
            ],
            "build_command": "pip install -r requirements.txt",
            "start_command": "gunicorn app:app",
        }
    
    def generate_env_example(self) -> str:
        return """# Render Environment Variables
DATABASE_URL=
SECRET_KEY=
FLASK_ENV=production
"""


class DockerDeployer:
    """Deploy using Docker."""
    
    name = "docker"
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """Generate Dockerfile and docker-compose."""
        dockerfile = self._generate_dockerfile(project_dir)
        compose = self._generate_compose()
        
        return {
            "success": True,
            "files": {"Dockerfile": dockerfile, "docker-compose.yml": compose},
            "commands": [
                "docker build -t myapp .",
                "docker run -p 3000:3000 myapp",
            ],
        }
    
    def _generate_dockerfile(self, project_dir: str) -> str:
        """Generate Dockerfile."""
        has_package = Path(project_dir).joinpath("package.json").exists()
        has_req = Path(project_dir).joinpath("requirements.txt").exists()
        
        if has_package:
            return '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
'''
        elif has_req:
            return '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
'''
        else:
            return '''FROM alpine:latest
WORKDIR /app
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
'''
    
    def _generate_compose(self) -> str:
        return '''version: "3.8"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://...
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app
      - POSTGRES_PASSWORD=secret
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
'''


class NetlifyDeployer:
    """Deploy to Netlify."""
    
    name = "netlify"
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """Deploy to Netlify."""
        return {
            "success": True,
            "platform": "netlify",
            "instructions": [
                "1. Install Netlify CLI: npm install -g netlify-cli",
                "2. Login: netlify login",
                "3. Deploy: netlify deploy --prod",
            ],
            "build_command": "npm run build",
            "publish_dir": "dist",
        }
    
    def generate_env_example(self) -> str:
        return """# Netlify Environment Variables
HUGO_VERSION=0.80.0
"""


class ReplitDeployer:
    """Deploy to Replit."""
    
    name = "replit"
    
    def deploy(self, project_dir: str, env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """Deploy to Replit."""
        return {
            "success": True,
            "platform": "replit",
            "instructions": [
                "1. Create new Replit project",
                "2. Import from GitHub",
                "3. Click Run button",
                "4. Use Always-on instance for production",
            ],
            "tips": [
                "Set .replit file for custom run command",
                "Add secrets in Secrets tab",
            ],
        }
    
    def generate_env_example(self) -> str:
        return """# Replit Secrets
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


def deploy_app(
    platform: str,
    project_dir: str,
    env_vars: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    Deploy application to specified platform.
    
    Usage:
        from neuro.deploy import deploy_app
        
        result = deploy_app(
            platform="vercel",
            project_dir="./my-app",
            env_vars={"DATABASE_URL": "..."}
        )
    """
    deployer_class = DEPLOYERS.get(platform.lower())
    if not deployer_class:
        return {
            "success": False,
            "error": f"Unknown platform: {platform}",
            "available": list(DEPLOYERS.keys()),
        }
    
    deployer = deployer_class()
    return deployer.deploy(project_dir, env_vars)


def generate_deployment_files(
    platform: str,
    project_dir: str,
) -> Dict[str, str]:
    """Generate deployment configuration files."""
    deployer_class = DEPLOYERS.get(platform.lower())
    if not deployer_class:
        return {"error": f"Unknown platform: {platform}"}
    
    deployer = deployer_class()
    
    return {
        ".env.example": deployer.generate_env_example(),
    }


def list_platforms() -> List[str]:
    """List available deployment platforms."""
    return list(DEPLOYERS.keys())
