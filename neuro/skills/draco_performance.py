"""
Draco Compression & Performance Tuning Skill
3D model optimization, Draco compression, performance best practices
"""

from typing import Dict, List, Any, Optional


class DracoPerformanceSkill:
    """Draco compression and performance optimization for 3D web"""
    
    NAME = "draco_performance"
    DESCRIPTION = "Draco compression - 3D model optimization, GLTF compression, performance tuning, lazy loading"
    TRIGGERS = [
        "draco", "compression", "gltf", "glb", "optimize",
        "performance", "lazy load", "instancing", " LOD", 
        "bundle size", "model optimization"
    ]
    
    @classmethod
    def get_draco_loader_template(cls) -> str:
        return '''
// Draco GLTF Loader Setup
import { useGLTF } from '@react-three/drei'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader'
import { useLoader } from '@react-three/fiber'

// Configure Draco decoder
const dracoLoader = new DRACOLoader()
dracoLoader.setDecoderPath('/draco/') // Self-hosted for production
dracoLoader.setDecoderType('js') // or 'wasm' for WebAssembly

// Load with Draco compression
function Model({{ url }}) {
  const {{ scene }} = useGLTF(url, dracoLoader)
  return <primitive object={{scene}} />
}

// Preload
useGLTF.preload('/models/optimized.glb', dracoLoader)
'''

    @classmethod
    def get_optimization_templates(cls) -> Dict[str, str]:
        return {
            "instancing": '''
// GPU Instancing for multiple meshes
const count = 1000
const geometry = new THREE.InstancedMesh(
  new THREE.BoxGeometry(0.1, 0.1, 0.1),
  new THREE.MeshStandardMaterial(),
  count
)

const dummy = new THREE.Object3D()
for (let i = 0; i < count; i++) {
  dummy.position.set(
    Math.random() * 10 - 5,
    Math.random() * 10,
    Math.random() * 10 - 5
  )
  dummy.updateMatrix()
  geometry.setMatrixAt(i, dummy.matrix)
}
geometry.instanceMatrix.needsUpdate = true
scene.add(geometry)
''',
            "lod": '''
// Level of Detail (LOD)
import { LOD } from 'three'

const lod = new LOD()

// High detail (close)
const highDetail = new THREE.Mesh(highGeometry, material)
lod.addLevel(highDetail, 0)

// Medium detail (10-50 units)
const mediumDetail = new THREE.Mesh(mediumGeometry, material)
lod.addLevel(mediumDetail, 10)

// Low detail (50+ units)
const lowDetail = new THREE.Mesh(lowGeometry, material)
lod.addLevel(lowDetail, 50)

scene.add(lod)
''',
            "lazy": '''
// Lazy loading 3D content
const LazyModel = lazy(() => import('./HeavyModel'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Canvas>
        <LazyModel />
      </Canvas>
    </Suspense>
  )
}
'''
        }
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()
        
        result_type = "draco"
        if "instance" in task_lower:
            result_type = "instancing"
        elif "lod" in task_lower or "level" in task_lower:
            result_type = "lod"
        elif "lazy" in task_lower or "code splitting" in task_lower:
            result_type = "lazy"
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "draco_template": cls.get_draco_loader_template(),
            "optimization_templates": cls.get_optimization_templates(),
            "compression_tips": [
                "Use Draco compression for geometry (10-100x smaller)",
                "Use Basis Universal for textures",
                "Enable meshopt compression",
                "Use instancing for repeated geometry",
                "Implement LOD for distant objects"
            ]
        }


def generate_optimized(task: str, **kwargs) -> Dict[str, Any]:
    return DracoPerformanceSkill.invoke(task, kwargs)
