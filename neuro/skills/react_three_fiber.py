"""
React Three Fiber Skill - 3D Web Development
R3F component generation, scene setup, and 3D interactions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class R3FConfig:
    """React Three Fiber configuration"""
    canvas_props: Dict[str, Any] = None
    camera_type: str = "perspective"
    shadows: bool = True
    dpr: int = 2
    gl_props: Dict[str, Any] = None


class ReactThreeFiberSkill:
    """
    React Three Fiber (R3F) skill for 3D web development.
    Generates R3F components, manages 3D scenes, handles interactions.
    """
    
    NAME = "react_three_fiber"
    DESCRIPTION = "React Three Fiber 3D development - Canvas, geometries, materials, lights, interactions"
    TRIGGERS = [
        "react-three-fiber", "r3f", "three.js react", "3d react",
        "canvas 3d", "webgl react", "react 3d component", "@react-three"
    ]
    
    # Common R3F patterns
    R3F_COMPONENTS = {
        "mesh": "Primitive mesh (Box, Sphere, Plane, etc.)",
        "light": "Light sources (Ambient, Directional, Point, Spot)",
        "camera": "Camera controls (Orbit, Perspective, Orthographic)",
        "effects": "Post-processing (Bloom, SSAO, Vignette)",
        "helpers": "Debug helpers (Grid, Axes, Stats)",
        "physics": "Physics simulation (@react-three/rapier, cannon)",
        "drei": "Drei helpers (Environment, Loader, Text, etc.)",
    }
    
    @classmethod
    def get_templates(cls, component_type: str) -> str:
        """Get code template for R3F component type"""
        templates = {
            "basic_scene": '''
// React Three Fiber Basic Scene
import {{ Canvas }} from '@react-three/fiber'
import {{ OrbitControls, Environment }} from '@react-three/drei'

export function BasicScene() {{
  return (
    <Canvas
      camera={{ position: [5, 5, 5], fov: 50 }}
      shadows
      dpr={{[1, 2]}}
    >
      <ambientLight intensity={{0.5}} />
      <directionalLight
        position={{[10, 10, 10]}}
        intensity={{1}}
        castShadow
        shadow-mapSize={{[1024, 1024]}}
      />
      
      {/* Your 3D content here */}
      
      <OrbitControls makeDefault />
      <Environment preset="city" />
    </Canvas>
  )
}}
''',

            "animated_mesh": '''
// Animated R3F Component with useFrame
import {{ useRef }} from 'react'
import {{ useFrame }} from '@react-three/fiber'
import * as THREE from 'three'

export function AnimatedMesh() {{
  const meshRef = useRef()
  
  useFrame((state, delta) => {{
    meshRef.current.rotation.x += delta * 0.5
    meshRef.current.rotation.y += delta * 0.3
  }})
  
  return (
    <mesh ref={{meshRef}} castShadow receiveShadow>
      <boxGeometry args={{[1, 1, 1]}} />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}}
''',

            "interactivity": '''
// Interactive R3F Component with events
import {{ useState }} from 'react'

export function InteractiveObject() {{
  const [hovered, setHover] = useState(false)
  const [clicked, setClick] = useState(false)
  
  return (
    <mesh
      onPointerOver={{() => setHover(true)}}
      onPointerOut={{() => setHover(false)}}
      onClick={{() => setClick(!clicked)}}
      scale={{clicked ? 1.2 : 1}}
    >
      <sphereGeometry args={{[1, 32, 32]}} />
      <meshStandardMaterial 
        color={{hovered ? 'hotpink' : 'gray'}} 
      />
    </mesh>
  )
}}
''',

            "loader": '''
// GLTF/GLB Model Loader
import {{ useGLTF }} from '@react-three/drei'

export function Model({{ url }}) {{
  const {{ scene }} = useGLTF(url)
  
  return (
    <primitive 
      object={{scene}} 
      scale={{1}}
      position={{[0, 0, 0]}}
    />
  )
}}

// Preload model
useGLTF.preload('/models/asset.glb')
''',

            "physics_box": '''
// Physics-enabled object with @react-three/rapier
import {{ RigidBody }} from '@react-three/rapier'

export function PhysicsBox({{ position = [0, 2, 0] }}) {{
  return (
    <RigidBody position={{position}} colliders="cuboid">
      <mesh castShadow receiveShadow>
        <boxGeometry args={{[1, 1, 1]}} />
        <meshStandardMaterial color="royalblue" />
      </mesh>
    </RigidBody>
  )
}}
''',
        }
        return templates.get(component_type, templates["basic_scene"])
    
    @classmethod
    def generate_scene_setup(cls, scene_type: str) -> str:
        """Generate complete scene setup"""
        setups = {
            "product_viewer": '''
// 3D Product Viewer with Turntable
import {{ useRef }} from 'react'
import {{ Canvas }} from '@react-three/fiber'
import {{ 
  OrbitControls, 
  Environment, 
  ContactShadows,
  Float,
  PresentationControls
} from '@react-three/drei'

export function ProductViewer({{ model }}) {{
  return (
    <Canvas shadows dpr={{[1, 2]}} camera={{0, 0, 4}}>
      <PresentationControls
        globalRotation={{0.1, 0.2}}
        globalTranslation={{0, 0, 0}}
        speed={1.5}
      >
        <Float rotationIntensity={{0.5}} floatIntensity={{0.5}}>
          {{model}}
        </Float>
      </PresentationControls>
      <ContactShadows position={{[0, -1, 0]}} opacity={{0.4}} />
      <Environment preset="studio" />
    </Canvas>
  )
}}
''',

            "scroll_animation": '''
// Scroll-driven 3D Animation
import {{ useScroll }} from '@react-three/drei'
import {{ useFrame }} from '@react-three/fiber'
import * as THREE from 'three'

export function ScrollScene() {{
  const scroll = useScroll()
  const groupRef = useRef()
  
  useFrame(() => {{
    const r1 = scroll.range(0, 1/3)
    const r2 = scroll.range(1/3, 1/3)
    const r3 = scroll.range(2/3, 1/3)
    
    // Scroll-driven animations
    groupRef.current.rotation.y = r1 * Math.PI * 2
  }})
  
  return (
    <group ref={{groupRef}}>
      {{/* 3D content driven by scroll */}}
    </group>
  )
}}
''',

            "particles": '''
// Particle System
import {{ useRef, useMemo }} from 'react'
import {{ useFrame }} from '@react-three/fiber'
import * as THREE from 'three'

export function Particles({{ count = 1000 }}) {{
  const mesh = useRef()
  
  const dummy = useMemo(() => new THREE.Object3D(), [])
  const particles = useMemo(() => {{
    const temp = []
    for (let i = 0; i < count; i++) {{
      const t = Math.random() * 100
      const factor = 20 + Math.random() * 100
      const speed = 0.01 + Math.random() / 200
      const xFactor = -50 + Math.random() * 100
      const yFactor = -50 + Math.random() * 100
      const zFactor = -50 + Math.random() * 100
      temp.push={{ t, factor, speed, xFactor, yFactor, zFactor, mx: 0, my: 0 }}
    }}
    return temp
  }}, [count])
  
  useFrame((state) => {{
    particles.forEach((particle, i) => {{
      let {{ t, factor, speed, xFactor, yFactor, zFactor }} = particle
      t = particle.t += speed / 2
      const a = Math.cos(t) + Math.sin(t * 1) / 10
      const b = Math.sin(t) + Math.cos(t * 2) / 10
      const s = Math.cos(t)
      dummy.position.set(
        particle.mx / 10 + a + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
        particle.my / 10 + b + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
        particle.my / 10 + a + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
      )
      dummy.scale.set(s, s, s)
      dummy.rotation.set(s * 5, s * 5, s * 5)
      dummy.updateMatrix()
      mesh.current.setMatrixAt(i, dummy.matrix)
    }})
    mesh.current.instanceMatrix.needsUpdate = true
  }})
  
  return (
    <instancedMesh ref={{mesh}} args={[null, null, count]}>
      <dodecahedronGeometry args={{[0.2, 0]}} />
      <meshPhongMaterial color="white" />
    </instancedMesh>
  )
}}
''',
        }
        return setups.get(scene_type, setups["product_viewer"])
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main skill invocation"""
        context = context or {}
        task_lower = task.lower()
        
        # Determine what to generate
        component_type = "basic_scene"
        if "animation" in task_lower or "animated" in task_lower:
            component_type = "animated_mesh"
        elif "interactive" in task_lower or "click" in task_lower or "hover" in task_lower:
            component_type = "interactivity"
        elif "model" in task_lower or "gltf" in task_lower or "glb" in task_lower:
            component_type = "loader"
        elif "physics" in task_lower or "rigid" in task_lower:
            component_type = "physics_box"
        elif "product" in task_lower or "viewer" in task_lower:
            component_type = "product_viewer"
        elif "scroll" in task_lower:
            component_type = "scroll_animation"
        elif "particle" in task_lower:
            component_type = "particles"
        
        return {
            "skill": cls.NAME,
            "component_type": component_type,
            "template": cls.get_templates(component_type),
            "available_components": cls.R3F_COMPONENTS,
            "dependencies": [
                "@react-three/fiber",
                "@react-three/drei",
                "three",
                "@react-three/rapier (for physics)"
            ],
            "tips": [
                "Use useFrame for animations",
                "Use useRef for mesh references",
                "Enable shadows on Canvas for realistic lighting",
                "Use Environment for HDR lighting",
                "Use ContactShadows for ground shadows"
            ]
        }


# Convenience function
def generate_r3f(task: str, **kwargs) -> Dict[str, Any]:
    return ReactThreeFiberSkill.invoke(task, kwargs)
