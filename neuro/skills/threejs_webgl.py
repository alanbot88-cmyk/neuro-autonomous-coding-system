"""
Three.js Core & WebGL Skill - 3D Graphics Engine
Pure Three.js, WebGL shaders, geometries, materials, rendering
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ThreeJSConfig:
    """Three.js configuration"""
    renderer: str = "WebGLRenderer"
    antialias: bool = True
    alpha: bool = True
    shadows: bool = True


class ThreeJSCoreSkill:
    """
    Three.js Core skill for raw WebGL/Three.js development.
    Handles scenes, cameras, renderers, geometries, materials, shaders.
    """
    
    NAME = "threejs_core"
    DESCRIPTION = "Three.js core WebGL development - Scene, camera, renderer, geometries, materials, GLSL shaders"
    TRIGGERS = [
        "three.js", "threejs", "webgl", "webgpu",
        "canvas", "renderer", "geometry", "material",
        "shader", "vertex", "fragment", "texture"
    ]
    
    @classmethod
    def get_basic_scene_template(cls) -> str:
        """Get basic Three.js scene setup"""
        return '''
// Three.js Basic Scene Setup
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

// Scene setup
const scene = new THREE.Scene()
scene.background = new THREE.Color(0x1a1a2e)

// Camera
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
)
camera.position.set(5, 5, 5)

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true })
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.setPixelRatio(window.devicePixelRatio)
renderer.shadowMap.enabled = true
document.body.appendChild(renderer.domElement)

// Controls
const controls = new OrbitControls(camera, renderer.domElement)
controls.enableDamping = true
controls.dampingFactor = 0.05

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
scene.add(ambientLight)

const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
directionalLight.position.set(10, 10, 10)
directionalLight.castShadow = true
scene.add(directionalLight)

// Create mesh
const geometry = new THREE.BoxGeometry(1, 1, 1)
const material = new THREE.MeshStandardMaterial({ 
  color: 0x00ff88,
  metalness: 0.5,
  roughness: 0.5
})
const cube = new THREE.Mesh(geometry, material)
cube.castShadow = true
cube.receiveShadow = true
scene.add(cube)

// Animation loop
function animate() {
  requestAnimationFrame(animate)
  
  cube.rotation.x += 0.01
  cube.rotation.y += 0.01
  
  controls.update()
  renderer.render(scene, camera)
}

animate()

// Handle resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})
'''

    @classmethod
    def get_geometry_templates(cls) -> Dict[str, str]:
        """Get geometry creation templates"""
        return {
            "box": '''
// BoxGeometry
const geometry = new THREE.BoxGeometry(width, height, depth, widthSegments, heightSegments, depthSegments)
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)
''',

            "sphere": '''
// SphereGeometry
const geometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments, phiStart, phiLength, thetaStart, thetaLength)
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)
''',

            "cylinder": '''
// CylinderGeometry
const geometry = new THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments)
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)
''',

            "torus": '''
// TorusGeometry (Donut shape)
const geometry = new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments, arc)
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)
''',

            "plane": '''
// PlaneGeometry (flat surface)
const geometry = new THREE.PlaneGeometry(width, height, widthSegments, heightSegments)
const mesh = new THREE.Mesh(geometry, material)
mesh.rotation.x = -Math.PI / 2 // Lay flat
scene.add(mesh)
''',

            "icosahedron": '''
// IcosahedronGeometry (geometric shape)
const geometry = new THREE.IcosahedronGeometry(radius, detail)
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)
''',

            "custom": '''
// Custom BufferGeometry for complex shapes
const geometry = new THREE.BufferGeometry()
const vertices = new Float32Array([
  // Define vertices here: x, y, z
  0, 0, 0,
  1, 0, 0,
  0.5, 1, 0
])
geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3))
geometry.computeVertexNormals()
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)
''',
        }

    @classmethod
    def get_material_templates(cls) -> Dict[str, str]:
        """Get material creation templates"""
        return {
            "basic": '''
// MeshBasicMaterial - Unlit, flat colors
const material = new THREE.MeshBasicMaterial({
  color: 0x00ff00,
  wireframe: false
})
''',

            "standard": '''
// MeshStandardMaterial - PBR lit material
const material = new THREE.MeshStandardMaterial({
  color: 0x3498db,
  metalness: 0.5,
  roughness: 0.5,
  emissive: 0x000000,
  emissiveIntensity: 1,
  transparent: false,
  opacity: 1
})
''',

            "physical": '''
// MeshPhysicalMaterial - Advanced PBR with clearcoat
const material = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  metalness: 0,
  roughness: 0,
  clearcoat: 1,
  clearcoatRoughness: 0,
  transmission: 0.5, // Glass-like
  thickness: 1
})
''',

            "lambert": '''
// MeshLambertMaterial - Simple diffuse lighting
const material = new THREE.MeshLambertMaterial({
  color: 0xff5500,
  emissive: 0x000000,
  emissiveIntensity: 1
})
''',

            "phong": '''
// MeshPhongMaterial - Specular highlights
const material = new THREE.MeshPhongMaterial({
  color: 0xffff00,
  emissive: 0x000000,
  specular: 0xffffff,
  shininess: 30,
  flatShading: false
})
''',

            "toon": '''
// MeshToonMaterial - Cel-shaded look
const material = new THREE.MeshToonMaterial({
  color: 0x00ffff,
  gradientMap: gradientTexture
})
// Toon gradient texture
const gradientMap = new THREE.DataTexture(
  new Uint8Array([255, 200, 100, 50]),
  4, 1
)
gradientMap.needsUpdate = true
material.gradientMap = gradientMap
''',

            "shader": '''
// Raw ShaderMaterial with custom GLSL
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color(0xff0000) }
  },
  vertexShader: \`
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  \`,
  fragmentShader: \`
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(uColor * sin(uTime), 1.0);
    }
  \`
})
''',
        }

    @classmethod
    def get_texture_templates(cls) -> str:
        """Get texture loading templates"""
        return '''
// Texture Loading
import { TextureLoader } from 'three'

const textureLoader = new TextureLoader()

// Load texture
textureLoader.load(
  '/textures diffuse.jpg',
  (texture) => {
    material.map = texture
    texture.wrapS = THREE.RepeatWrapping
    texture.wrapT = THREE.RepeatWrapping
    texture.repeat.set(2, 2)
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy()
    texture.needsUpdate = true
  },
  undefined,
  (error) => console.error('Error loading texture:', error)
)

// Load normal map
textureLoader.load('/textures/normal.jpg', (texture) => {
  material.normalMap = texture
  material.normalScale.set(1, 1)
  material.needsUpdate = true
})

// Load HDR environment
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js'
const pmremGenerator = new THREE.PMREMGenerator(renderer)
pmremGenerator.compileEquirectangularShader()

new RGBELoader()
  .setDataType(THREE.UnsignedByteType)
  .load('/textures/environment.hdr', (texture) => {
    const envMap = pmremGenerator.fromEquirectangular(texture).texture
    scene.environment = envMap
    texture.dispose()
    pmremGenerator.dispose()
  })
'''

    @classmethod
    def get_animation_templates(cls) -> str:
        """Get animation/morph targets templates"""
        return '''
// Animation System using GSAP or built-in
// Option 1: Using Three.js Clock
const clock = new THREE.Clock()

function animate() {
  const elapsedTime = clock.getElapsedTime()
  
  // Sine wave animation
  cube.position.y = Math.sin(elapsedTime) * 2
  cube.rotation.z = Math.cos(elapsedTime) * 0.5
  
  // Scale pulsing
  const scale = 1 + Math.sin(elapsedTime * 2) * 0.2
  cube.scale.set(scale, scale, scale)
  
  renderer.render(scene, camera)
  requestAnimationFrame(animate)
}

// Option 2: Morph Targets for character animation
const geometry = new THREE.BufferGeometry()
const positions = geometry.attributes.position
const morphAttributes = geometry.morphAttributes Relative

// Add morph target (target shape 1)
const target1 = positions.array.slice()
for (let i = 0; i < positions.count; i++) {
  target1[i * 3 + 1] += 0.5 // Move up
}
geometry.morphAttributes.relative = true
geometry.morphAttributes.push(new THREE.BufferAttribute(target1, 3))

// Control morph target influence
mesh.morphTargetInfluences[0] = Math.sin(elapsedTime) // 0 to 1
'''

    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main skill invocation"""
        context = context or {}
        task_lower = task.lower()
        
        result_type = "scene"
        if "geometry" in task_lower or "shape" in task_lower:
            result_type = "geometry"
        elif "material" in task_lower or "texture" in task_lower or "surface" in task_lower:
            result_type = "material"
        elif "shader" in task_lower or "glsl" in task_lower or "fragment" in task_lower:
            result_type = "shader"
        elif "animation" in task_lower or "animate" in task_lower:
            result_type = "animation"
        elif "texture" in task_lower or "load" in task_lower:
            result_type = "texture"
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "scene_template": cls.get_basic_scene_template(),
            "geometry_templates": cls.get_geometry_templates(),
            "material_templates": cls.get_material_templates(),
            "texture_template": cls.get_texture_templates(),
            "animation_template": cls.get_animation_templates(),
            "dependencies": ["three"],
            "tips": [
                "Use BufferGeometry for custom shapes",
                "MeshStandardMaterial for PBR rendering",
                "Use dispose() to prevent memory leaks",
                "Use requestAnimationFrame for smooth animation",
                "Enable shadow mapping for realistic shadows"
            ]
        }


# Convenience function
def generate_threejs(task: str, **kwargs) -> Dict[str, Any]:
    return ThreeJSCoreSkill.invoke(task, kwargs)
