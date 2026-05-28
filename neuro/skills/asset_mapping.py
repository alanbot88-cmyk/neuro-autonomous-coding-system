"""
Asset Mapping & Mocking Skill
Asset pipeline, mock data, asset loading, CDN strategies
"""

from typing import Dict, List, Any, Optional


class AssetMappingSkill:
    """Asset mapping and mocking for development"""
    
    NAME = "asset_mapping"
    DESCRIPTION = "Asset mapping - Mock data, asset loading, CDN strategies, fixtures, test data"
    TRIGGERS = [
        "asset", "mock", "fixture", "test data", "mocking",
        "asset pipeline", "cdn", "image optimization",
        "lazy load", "preload", "sprite"
    ]
    
    @classmethod
    def get_asset_templates(cls) -> Dict[str, str]:
        return {
            "mock": '''
// Mock Data for Development
const mockUsers = [
  { id: 1, name: "John Doe", email: "john@example.com" },
  { id: 2, name: "Jane Smith", email: "jane@example.com" },
  { id: 3, name: "Bob Wilson", email: "bob@example.com" }
]

// Mock API function
async function fetchUsers() {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockUsers), 500)
  })
}

// Use in component
const users = await fetchUsers()
''',

            "asset_loader": '''
// Asset Preloader
class AssetLoader {
  constructor() {
    this.queue = []
    this.loaded = new Map()
  }
  
  add(key, url, type = "image") {
    this.queue.push({ key, url, type })
    return this
  }
  
  async load() {
    const promises = this.queue.map(item => this.loadAsset(item))
    await Promise.all(promises)
    return this.loaded
  }
  
  async loadAsset({ key, url, type }) {
    if (type === "image") {
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          this.loaded.set(key, img)
          resolve(img)
        }
        img.onerror = reject
        img.src = url
      })
    }
  }
  
  get(key) {
    return this.loaded.get(key)
  }
}

// Usage
const assets = await new AssetLoader()
  .add("hero", "/images/hero.jpg")
  .add("logo", "/images/logo.svg")
  .add("bg", "/images/bg.png")
  .load()

const hero = assets.get("hero")
'''
        }
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()
        
        result_type = "mock"
        if "loader" in task_lower or "preload" in task_lower:
            result_type = "asset_loader"
        elif "cdn" in task_lower or "image" in task_lower:
            result_type = "cdn"
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "templates": cls.get_asset_templates(),
            "tips": [
                "Use mock data for development",
                "Preload critical assets",
                "Implement lazy loading",
                "Use CDN for production assets"
            ]
        }


def generate_asset(task: str, **kwargs) -> Dict[str, Any]:
    return AssetMappingSkill.invoke(task, kwargs)
