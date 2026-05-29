"""
Neuro 3D Graphics & Motion Skills - Top 20 for UI/Frontend Design
==================================================================
Complete 3D graphics, animation, and motion design capabilities
for enterprise-grade UI/frontend development.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class GraphicsSkill:
    """A 3D graphics or motion design skill."""
    name: str
    category: str
    priority: int
    description: str
    triggers: List[str]
    dependencies: List[str]
    example_use_cases: List[str]
    code_templates: Dict[str, str]


class Neuro3DGraphicsSkills:
    """
    Comprehensive 3D graphics and motion design skills for Neuro.
    Covers everything from Three.js to Blender automation.
    """
    
    # Category: 3D Rendering & WebGL
    THREE_JS_CORE = {
        "name": "threejs_core",
        "category": "3d_rendering",
        "priority": 1,
        "description": "Core Three.js WebGL rendering for 3D web experiences",
        "triggers": ["3d", "threejs", "webgl", "3d model", "render"],
        "code_template": '''import * as THREE from 'three';

export class Scene3D {
  constructor(container) {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(this.renderer.domElement);
  }
  
  addMesh(geometry, material, position = [0, 0, 0]) {
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(...position);
    this.scene.add(mesh);
    return mesh;
  }
  
  animate() {
    requestAnimationFrame(() => this.animate());
    this.renderer.render(this.scene, this.camera);
  }
}
'''
    }
    
    REACT_THREE_FIBER = {
        "name": "react_three_fiber",
        "category": "3d_rendering",
        "priority": 1,
        "description": "React renderer for Three.js - Declarative 3D in React",
        "triggers": ["r3f", "react-three", "react fiber", "react 3d"],
        "code_template": '''import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF } from '@react-three/drei';

function Model({ url }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

export function Scene3D() {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight intensity={0.5} />
      <Model url="/model.glb" />
      <OrbitControls enableDamping />
      <Environment preset="city" />
    </Canvas>
  );
}
'''
    }
    
    WEBGL_SHADERS = {
        "name": "webgl_shaders",
        "category": "3d_rendering",
        "priority": 2,
        "description": "Custom GLSL shaders and post-processing effects",
        "triggers": ["shader", "glsl", "fragment", "vertex", "custom shader", "post-processing"],
        "code_template": '''// Custom ShaderMaterial for advanced effects
import * as THREE from 'three';

const customShaderMaterial = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    colorA: { value: new THREE.Color('#ff6b6b') },
    colorB: { value: new THREE.Color('#4ecdc4') }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float time;
    uniform vec3 colorA;
    uniform vec3 colorB;
    varying vec2 vUv;
    
    void main() {
      float mixed = sin(vUv.x * 10.0 + time) * 0.5 + 0.5;
      gl_FragColor = vec4(mix(colorA, colorB, mixed), 1.0);
    }
  `
});
'''
    }
    
    # Category: Animation & Motion
    GSAP_ANIMATION = {
        "name": "gsap_animation",
        "category": "animation",
        "priority": 1,
        "description": "Professional-grade animations with GSAP and ScrollTrigger",
        "triggers": ["gsap", "animation", "scroll", "timeline", "tween", "motion"],
        "code_template": '''import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Main timeline animation
const tl = gsap.timeline();

tl.to('.hero-title', {
  y: 0,
  opacity: 1,
  duration: 1,
  ease: 'power3.out'
})
.to('.hero-subtitle', {
  y: 0,
  opacity: 1,
  duration: 0.8
}, '-=0.5')
.to('.hero-cta', {
  scale: 1,
  opacity: 1,
  duration: 0.6
}, '-=0.3');

// Scroll-triggered section animation
ScrollTrigger.create({
  trigger: '.features-section',
  start: 'top 80%',
  onEnter: () => {
    gsap.from('.feature-card', {
      y: 100,
      opacity: 0,
      stagger: 0.2,
      duration: 0.8,
      ease: 'power3.out'
    });
  }
});
'''
    }
    
    FRAMER_MOTION = {
        "name": "framer_motion",
        "category": "animation",
        "priority": 1,
        "description": "React animation library with gestures and layout animations",
        "triggers": ["framer", "react animation", "transition", "gesture", "layout"],
        "code_template": '''import { motion, AnimatePresence } from 'framer-motion';

// Page transitions
const pageVariants = {
  initial: { opacity: 0, x: '-100%' },
  enter: { opacity: 1, x: 0, transition: { duration: 0.5 } },
  exit: { opacity: 0, x: '100%' }
};

// Staggered children animation
const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

export function AnimatedSection() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {[1, 2, 3].map(i => (
        <motion.div key={i} variants={itemVariants}>
          Content {i}
        </motion.div>
      ))}
    </motion.div>
  );
}
'''
    }
    
    LOTTIE_ANIMATION = {
        "name": "lottie_animation",
        "category": "animation",
        "priority": 2,
        "description": "Scalable vector animations from After Effects",
        "triggers": ["lottie", "after effects", "animation export", "json animation"],
        "code_template": '''import Lottie from 'lottie-react';

const animationOptions = {
  loop: true,
  autoplay: true,
  animationData: require('./animation.json'),
  rendererSettings: {
    preserveAspectRatio: 'xMidYMid slice'
  }
};

export function LottieAnimation({ scrollProgress }) {
  return (
    <div className="lottie-container">
      <Lottie
        {...animationOptions}
        style={{ transform: `scale(${1 + scrollProgress * 0.2})` }}
      />
    </div>
  );
}

// For scroll-linked animations
export function ScrollLottie() {
  const ref = useRef(null);
  
  useLayoutEffect(() => {
    const animation = Lottie.loadAnimation({
      container: ref.current,
      ...animationOptions
    });
    
    const handleScroll = () => {
      const progress = window.scrollY / document.body.scrollHeight;
      animation.goToAndStop(progress * animation.totalFrames, true);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  return <div ref={ref} />;
}
'''
    }
    
    SVG_ANIMATIONS = {
        "name": "svg_animations",
        "category": "animation",
        "priority": 1,
        "description": "Advanced SVG path animations and morphing",
        "triggers": ["svg", "vector", "icon animation", "path animation", "morph"],
        "code_template": '''// SVG path animation with stroke-dasharray/dashoffset
const svgAnimation = `
@keyframes drawPath {
  to { stroke-dashoffset: 0; }
}

.path-animated {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawPath 2s ease forwards;
}

// CSS for path animation
.icon-path {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
`;

// React SVG component with morphing
export function AnimatedIcon({ isHovered }) {
  return (
    <svg viewBox="0 0 24 24" className="animated-icon">
      <motion.path
        d={isHovered ? "M12 2L2 7l10 5 10-5-10-5z" : "M12 2L2 7l10 5 10-5-10-5z"}
        initial={false}
        animate={{ d: isHovered ? "M22 12h-4l-3 9L9 3l-3 9H2" : "M12 2L2 7l10 5 10-5-10-5z" }}
        transition={{ duration: 0.5 }}
      />
    </svg>
  );
}
'''
    }
    
    # Category: 3D Modeling & Tools
    BLENDER_AUTOMATION = {
        "name": "blender_automation",
        "category": "3d_modeling",
        "priority": 1,
        "description": "Blender Python API automation for 3D workflows",
        "triggers": ["blender", "3d model", "animation", "render", "bpy", "blender python"],
        "code_template": '''import bpy
import math

# Create a new material
def create_emissive_material(name, color, strength=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (*color, 1)
    emission.inputs['Strength'].default_value = strength
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.inputs['Surface'].default_value = emission.outputs['Emission']
    
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    return mat

# Create a procedural mesh
def create_procedural_cube(location=(0,0,0), size=2):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    return obj

# Setup render settings for Eevee
def setup_eevee_render():
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.use_shadows = True
    bpy.context.scene.eevee.taa_render_samples = 16
'''
    }
    
    PARTICLE_SYSTEMS = {
        "name": "particle_systems",
        "category": "effects",
        "priority": 2,
        "description": "Particle systems and visual effects",
        "triggers": ["particles", "sparkles", "effects", "simulation", "points"],
        "code_template": '''import * as THREE from 'three';
import gsap from 'gsap';

// Custom particle system with physics
export class ParticleSystem {
  constructor(count = 1000) {
    this.count = count;
    this.particles = null;
    this.velocities = [];
    this.init();
  }
  
  init() {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.count * 3);
    const colors = new Float32Array(this.count * 3);
    
    for (let i = 0; i < this.count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = Math.random() * 10;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
      
      colors[i * 3] = Math.random();
      colors[i * 3 + 1] = Math.random();
      colors[i * 3 + 2] = Math.random();
      
      this.velocities.push({
        x: (Math.random() - 0.5) * 0.02,
        y: Math.random() * 0.02,
        z: (Math.random() - 0.5) * 0.02
      });
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const material = new THREE.PointsMaterial({
      size: 0.05,
      vertexColors: true,
      transparent: true,
      opacity: 0.8
    });
    
    this.particles = new THREE.Points(geometry, material);
  }
  
  update() {
    const positions = this.particles.geometry.attributes.position.array;
    
    for (let i = 0; i < this.count; i++) {
      positions[i * 3] += this.velocities[i].x;
      positions[i * 3 + 1] += this.velocities[i].y;
      positions[i * 3 + 2] += this.velocities[i].z;
    }
    
    this.particles.geometry.attributes.position.needsUpdate = true;
  }
}
'''
    }
    
    # Category: UI/UX Motion
    SCROLL_ANIMATIONS = {
        "name": "scroll_animations",
        "category": "ui_motion",
        "priority": 1,
        "description": "Scroll-linked animations and parallax effects",
        "triggers": ["scroll", "parallax", "sticky", "horizontal scroll", "scrolltrigger"],
        "code_template": '''import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Parallax effect
export function initParallax() {
  gsap.to('.parallax-bg', {
    yPercent: 50,
    ease: 'none',
    scrollTrigger: {
      trigger: '.parallax-section',
      start: 'top bottom',
      end: 'bottom top',
      scrub: true
    }
  });
}

// Horizontal scroll section
export function initHorizontalScroll() {
  const sections = gsap.utils.toArray('.horizontal-panel');
  
  gsap.to(sections, {
    xPercent: -100 * (sections.length - 1),
    ease: 'none',
    scrollTrigger: {
      trigger: '.horizontal-container',
      pin: true,
      scrub: 1,
      snap: 1 / (sections.length - 1),
      end: () => '+=' + document.querySelector('.horizontal-container').offsetWidth
    }
  });
}

// Text reveal on scroll
export function initTextReveal() {
  gsap.utils.toArray('.reveal-text').forEach(text => {
    gsap.from(text, {
      y: 100,
      opacity: 0,
      duration: 1,
      scrollTrigger: {
        trigger: text,
        start: 'top 80%',
        toggleActions: 'play none none reverse'
      }
    });
  });
}
'''
    }
    
    MICRO_INTERACTIONS = {
        "name": "micro_interactions",
        "category": "ui_motion",
        "priority": 1,
        "description": "Button, hover, and focus micro-interactions",
        "triggers": ["hover", "click", "interaction", "button", "focus", "state"],
        "code_template": '''// CSS for micro-interactions
.micro-interactions {
  /* Button hover effect */
  .btn-primary {
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      transition: width 0.6s, height 0.6s;
    }
    
    &:hover::before {
      width: 300px;
      height: 300px;
    }
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    }
    
    &:active {
      transform: translateY(0) scale(0.98);
    }
  }
  
  /* Card hover effect */
  .card-interactive {
    transition: transform 0.3s, box-shadow 0.3s;
    
    &:hover {
      transform: translateY(-8px) scale(1.02);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    }
  }
  
  /* Magnetic button effect */
  .magnetic-btn {
    transition: transform 0.2s ease-out;
  }
}
'''
    }
    
    # Category: Advanced Effects
    POST_PROCESSING = {
        "name": "post_processing",
        "category": "effects",
        "priority": 2,
        "description": "Three.js post-processing effects (bloom, DOF, etc.)",
        "triggers": ["post-processing", "bloom", "dof", "depth of field", "effects", "vignette"],
        "code_template": '''import { EffectComposer, BloomEffect, DepthOfFieldEffect, VignetteEffect } from 'postprocessing';
import { EffectPass, RenderPass } from 'postprocessing';

export function setupPostProcessing(scene, camera, renderer) {
  const composer = new EffectComposer(renderer);
  
  // Render pass
  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);
  
  // Bloom effect
  const bloomEffect = new BloomEffect({
    luminanceThreshold: 0.2,
    luminanceSmoothing: 0.9,
    intensity: 1.5
  });
  const bloomPass = new EffectPass(camera, bloomEffect);
  composer.addPass(bloomPass);
  
  // Depth of Field
  const dofEffect = new DepthOfFieldEffect({
    focusDistance: 0.02,
    focalLength: 0.05,
    bokehScale: 3
  });
  const dofPass = new EffectPass(camera, dofEffect);
  composer.addPass(dofPass);
  
  // Vignette
  const vignetteEffect = new VignetteEffect({
    offset: 0.3,
    darkness: 0.6
  });
  const vignettePass = new EffectPass(camera, vignetteEffect);
  composer.addPass(vignettePass);
  
  return composer;
}
'''
    }
    
    PHYSICS_SIMULATION = {
        "name": "physics_simulation",
        "category": "simulation",
        "priority": 2,
        "description": "Physics simulations (rigid body, soft body, fluids)",
        "triggers": ["physics", "simulation", "rigid body", "fluids", "collision"],
        "code_template": '''// Using Cannon.js for physics simulation
import * as CANNON from 'cannon-es';
import * as THREE from 'three';

export class PhysicsWorld {
  constructor() {
    this.world = new CANNON.World();
    this.world.gravity.set(0, -9.82, 0);
    this.bodies = [];
    this.meshes = [];
  }
  
  createBox(size, position, mass = 1) {
    const shape = new CANNON.Box(new CANNON.Vec3(size/2, size/2, size/2));
    const body = new CANNON.Body({ mass, shape });
    body.position.set(...position);
    
    this.world.addBody(body);
    this.bodies.push(body);
    
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(size, size, size),
      new THREE.MeshStandardMaterial()
    );
    this.meshes.push(mesh);
    
    return { body, mesh };
  }
  
  update(delta) {
    this.world.step(1/60, delta, 3);
    
    for (let i = 0; i < this.bodies.length; i++) {
      this.meshes[i].position.copy(this.bodies[i].position);
      this.meshes[i].quaternion.copy(this.bodies[i].quaternion);
    }
  }
}
'''
    }
    
    PROCEDURAL_GENERATION = {
        "name": "procedural_generation",
        "category": "generation",
        "priority": 2,
        "description": "Procedural 3D content generation with noise",
        "triggers": ["procedural", "noise", "voronoi", "generation", "algorithm"],
        "code_template": '''// Procedural terrain generation with Perlin noise
import * as THREE from 'three';
import SimplexNoise from 'simplex-noise';

export class ProceduralTerrain {
  constructor(size = 100, segments = 128) {
    this.size = size;
    this.segments = segments;
    this.simplex = new SimplexNoise();
  }
  
  generateHeight(x, z) {
    const scale = 0.05;
    const amplitude = 10;
    
    let height = 0;
    height += this.simplex.noise2D(x * scale, z * scale) * amplitude;
    height += this.simplex.noise2D(x * scale * 2, z * scale * 2) * (amplitude / 2);
    height += this.simplex.noise2D(x * scale * 4, z * scale * 4) * (amplitude / 4);
    
    return height;
  }
  
  createMesh() {
    const geometry = new THREE.PlaneGeometry(
      this.size, this.size, this.segments, this.segments
    );
    geometry.rotateX(-Math.PI / 2);
    
    const positions = geometry.attributes.position.array;
    for (let i = 0; i < positions.length; i += 3) {
      const x = positions[i];
      const z = positions[i + 2];
      positions[i + 1] = this.generateHeight(x, z);
    }
    
    geometry.computeVertexNormals();
    
    return new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({ flatShading: true })
    );
  }
}
'''
    }
    
    CHARACTER_ANIMATION = {
        "name": "character_animation",
        "category": "animation",
        "priority": 2,
        "description": "Character rigging and skeletal animation",
        "triggers": ["character", "rigging", "skeleton", "bones", "skeletal", "animation"],
        "code_template": '''// Character animation with skeletal rigging
import * as THREE from 'three';

export class SkeletalAnimation {
  constructor() {
    this.bones = {};
    this.skeleton = null;
    this.mixer = null;
  }
  
  createSkeleton(rootBone) {
    this.skeleton = new THREE.Skeleton([
      rootBone,
      this.bones.spine,
      this.bones.head,
      this.bones.leftArm,
      this.bones.rightArm,
      this.bones.leftLeg,
      this.bones.rightLeg
    ]);
    
    return this.skeleton;
  }
  
  createBone(name, length, position) {
    const bone = new THREE.Bone();
    bone.name = name;
    bone.position.set(...position);
    
    if (length) {
      const child = new THREE.Bone();
      child.position.y = length;
      bone.add(child);
    }
    
    this.bones[name] = bone;
    return bone;
  }
  
  createIKChain(startBone, endBone, targets) {
    // IK solver for procedural animation
    // Using FABRIK algorithm
  }
}
'''
    }
    
    REAL_TIME_GRAPHICS = {
        "name": "real_time_graphics",
        "category": "rendering",
        "priority": 2,
        "description": "Real-time rendering and game engine integration",
        "triggers": ["real-time", "game engine", "unreal", "unity", "rtx", "ray tracing"],
        "code_template": '''// Real-time rendering optimizations
export class RealTimeRenderer {
  constructor(renderer) {
    this.renderer = renderer;
    this.shadowMapSize = 2048;
    this.setupOptimizations();
  }
  
  setupOptimizations() {
    // Enable HDR rendering
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    
    // Optimize shadow maps
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    // Enable frustum culling
    this.renderer.frustumCulled = true;
    
    // Use LOD for complex meshes
    this.lodSystem = new THREE.LOD();
  }
  
  enableRayTracing() {
    // WebGPU ray tracing support check
    if ('getPreferredCanvasFormat' in this.renderer) {
      // Enable ray tracing features
    }
  }
}
'''
    }
    
    VFX_COMPOSITING = {
        "name": "vfx_compositing",
        "category": "effects",
        "priority": 2,
        "description": "Visual effects compositing and color grading",
        "triggers": ["vfx", "compositing", "color grading", "comp", "visual effects"],
        "code_template": '''// VFX compositing pipeline
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

// Color grading shader
const ColorGradeShader = {
  uniforms: {
    tDiffuse: { value: null },
    exposure: { value: 1.0 },
    contrast: { value: 1.0 },
    saturation: { value: 1.0 },
    temperature: { value: 0 },
    tint: { value: 0 }
  },
  vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float exposure;
    uniform float contrast;
    uniform float saturation;
    varying vec2 vUv;
    
    vec3 adjustExposure(vec3 color, float exp) {
      return color * pow(2.0, exp);
    }
    
    void main() {
      vec4 color = texture2D(tDiffuse, vUv);
      color.rgb = adjustExposure(color.rgb, exposure);
      gl_FragColor = color;
    }
  `
};

export function setupVFXCompositor(scene, camera, renderer) {
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  
  const colorGradePass = new ShaderPass(ColorGradeShader);
  composer.addPass(colorGradePass);
  
  return composer;
}
'''
    }
    
    IMMERSIVE_WEB = {
        "name": "immersive_web",
        "category": "webxr",
        "priority": 2,
        "description": "WebXR, VR, and immersive web experiences",
        "triggers": ["vr", "xr", "immersive", "virtual reality", "webxr", "metaverse"],
        "code_template": '''// WebXR VR support
import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { XRControllerModelFactory } from 'three/examples/jsm/webxr/XRControllerModelFactory.js';

export class ImmersiveRenderer {
  constructor(scene, renderer) {
    this.scene = scene;
    this.renderer = renderer;
    this.controllers = [];
    this.setupXR();
  }
  
  setupXR() {
    this.renderer.xr.enabled = true;
    document.body.appendChild(VRButton.createButton(this.renderer));
    
    // Setup controllers
    const controllerModelFactory = new XRControllerModelFactory();
    
    for (let i = 0; i < 2; i++) {
      const controller = this.renderer.xr.getController(i);
      controller.addEventListener('connected', (event) => {
        controller.userData.inputSource = event.data;
      });
      
      const grip = this.renderer.xr.getControllerGrip(i);
      grip.add(controllerModelFactory.createControllerModel(grip));
      this.scene.add(grip);
      
      this.controllers.push({ controller, grip });
    }
  }
  
  createVRScene() {
    // Create VR-optimized scene
    const vrScene = new THREE.Scene();
    vrScene.fog = new THREE.FogExp2(0x000000, 0.02);
    return vrScene;
  }
}
'''
    }
    
    # Export all skills
    @classmethod
    def get_all_skills(cls) -> List[Dict]:
        """Get all 3D graphics and motion skills."""
        skills = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_'):
                attr = getattr(cls, attr_name)
                if isinstance(attr, dict) and 'name' in attr:
                    skills.append(attr)
        return skills
    
    @classmethod
    def get_skills_by_category(cls, category: str) -> List[Dict]:
        """Get skills filtered by category."""
        all_skills = cls.get_all_skills()
        return [s for s in all_skills if s.get('category') == category]
    
    @classmethod
    def match_skills_for_task(cls, task: str) -> List[Dict]:
        """Match skills based on task description."""
        task_lower = task.lower()
        matched = []
        
        for skill in cls.get_all_skills():
            for trigger in skill.get('triggers', []):
                if trigger.lower() in task_lower:
                    matched.append(skill)
                    break
                    
        return matched


# Categories for organization
SKILL_CATEGORIES = {
    "3d_rendering": ["threejs_core", "react_three_fiber", "webgl_shaders", "post_processing"],
    "animation": ["gsap_animation", "framer_motion", "lottie_animation", "svg_animations", "character_animation"],
    "3d_modeling": ["blender_automation", "procedural_generation"],
    "effects": ["particle_systems", "vfx_compositing", "real_time_graphics"],
    "ui_motion": ["scroll_animations", "micro_interactions"],
    "webxr": ["immersive_web"],
    "simulation": ["physics_simulation"]
}