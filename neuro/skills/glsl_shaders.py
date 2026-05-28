"""
Custom GLSL Shader Skill - GPU Programming
Shader writing, vertex/fragment shaders, uniforms, post-processing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class GLSLShaderSkill:
    """
    GLSL Shader skill for custom GPU programming.
    Creates vertex shaders, fragment shaders, uniforms, post-processing.
    """
    
    NAME = "glsl_shaders"
    DESCRIPTION = "Custom GLSL shaders - Vertex/fragment shaders, uniforms, post-processing, WebGL, GPU programming"
    TRIGGERS = [
        "glsl", "shader", "vertex shader", "fragment shader",
        "gpu", "webgl", "uniform", "varying", "texture",
        "post-processing", "bloom", "blur", "custom shader"
    ]
    
    @classmethod
    def get_vertex_shader_template(cls) -> str:
        """Get vertex shader template"""
        return '''
// Vertex Shader Template
// attribute: per-vertex data (position, normal, uv)
// uniform: global data (model matrix, view matrix, projection matrix)
// varying: data passed to fragment shader

attribute vec3 position;
attribute vec3 normal;
attribute vec2 uv;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

// Varyings (output to fragment shader)
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;
varying vec3 vWorldPosition;

void main() {
  // Transform normal to world space
  vNormal = normalize((modelMatrix * vec4(normal, 0.0)).xyz);
  
  // Transform position to world space
  vec4 worldPosition = modelMatrix * vec4(position, 1.0);
  vWorldPosition = worldPosition.xyz;
  
  // Pass UV coordinates
  vUv = uv;
  
  // Pass position for custom calculations
  vPosition = position;
  
  // Final position
  gl_Position = projectionMatrix * viewMatrix * worldPosition;
}
'''

    @classmethod
    def get_fragment_shader_templates(cls) -> Dict[str, str]:
        """Get fragment shader templates"""
        return {
            "basic": '''
// Basic Fragment Shader
precision highp float;

varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vWorldPosition;

uniform vec3 uColor;
uniform float uTime;

void main() {
  // Simple solid color
  gl_FragColor = vec4(uColor, 1.0);
}
''',

            "gradient": '''
// Gradient Shader
precision highp float;

varying vec2 vUv;
varying vec3 vNormal;

uniform vec3 uColorA;
uniform vec3 uColorB;
uniform float uTime;

void main() {
  // Mix colors based on UV
  vec3 color = mix(uColorA, uColorB, vUv.y + sin(uTime) * 0.1);
  gl_FragColor = vec4(color, 1.0);
}
''',

            "noise": '''
// Noise-based Shader
precision highp float;

varying vec2 vUv;
varying vec3 vPosition;
varying vec3 vNormal;

uniform float uTime;
uniform vec3 uColor;

// Simplex noise function
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

float snoise(vec3 v) {
  const vec2 C = vec2(1.0/6.0, 1.0/3.0);
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
  
  vec3 i  = floor(v + dot(v, C.yyy));
  vec3 x0 = v - i + dot(i, C.xxx);
  
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min(g.xyz, l.zxy);
  vec3 i2 = max(g.xyz, l.zxy);
  
  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;
  
  i = mod289(i);
  vec4 p = permute(permute(permute(
    i.z + vec4(0.0, i1.z, i2.z, 1.0))
    + i.y + vec4(0.0, i1.y, i2.y, 1.0))
    + i.x + vec4(0.0, i1.x, i2.x, 1.0));
  
  float n_ = 0.142857142857;
  vec3 ns = n_ * D.wyz - D.xzx;
  
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_);
  
  vec4 x = x_ *ns.x + ns.yyyy;
  vec4 y = y_ *ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  
  vec4 b0 = vec4(x.xy, y.xy);
  vec4 b1 = vec4(x.zw, y.zw);
  
  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  
  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
  
  vec3 p0 = vec3(a0.xy, h.x);
  vec3 p1 = vec3(a0.zw, h.y);
  vec3 p2 = vec3(a1.xy, h.z);
  vec3 p3 = vec3(a1.zw, h.w);
  
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;
  
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
}

void main() {
  // Use noise for displacement or coloring
  float n = snoise(vPosition * 2.0 + uTime * 0.5);
  vec3 color = uColor * (0.5 + 0.5 * n);
  gl_FragColor = vec4(color, 1.0);
}
''',

            "fresnel": '''
// Fresnel Effect Shader
precision highp float;

varying vec3 vNormal;
varying vec3 vWorldPosition;

uniform vec3 uColor;
uniform vec3 uFresnelColor;
uniform float uPower;
uniform float uTime;

void main() {
  // Calculate fresnel
  vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
  float fresnel = pow(1.0 - dot(viewDirection, vNormal), uPower);
  
  // Mix base color with fresnel
  vec3 color = mix(uColor, uFresnelColor, fresnel);
  
  // Add animation
  color += fresnel * sin(uTime) * 0.1;
  
  gl_FragColor = vec4(color, 1.0);
}
''',

            "displacement": '''
// Displacement Mapping Shader
precision highp float;

varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vWorldPosition;

uniform sampler2D uDisplacementMap;
uniform float uDisplacementScale;
uniform float uTime;

void main() {
  // Sample displacement
  float displacement = texture2D(uDisplacementMap, vUv).r;
  
  // Displace along normal
  vec3 displacedPosition = position + normal * displacement * uDisplacementScale;
  
  // Calculate displaced normal (simplified)
  vec3 displacedNormal = normalize(normal + vec3(displacement * 0.5));
  
  gl_Position = projectionMatrix * modelViewMatrix * vec4(displacedPosition, 1.0);
}
''',

            "pbr": '''
// PBR (Physically Based Rendering) Shader
precision highp float;

varying vec3 vNormal;
varying vec3 vWorldPosition;
varying vec2 vUv;

uniform vec3 uAlbedo;
uniform float uMetallic;
uniform float uRoughness;
uniform vec3 uLightPosition;
uniform vec3 uLightColor;
uniform vec3 uCameraPosition;

// PBR functions
float DistributionGGX(vec3 N, vec3 H, float roughness) {
  float a = roughness * roughness;
  float a2 = a * a;
  float NdotH = max(dot(N, H), 0.0);
  float NdotH2 = NdotH * NdotH;
  
  float nom = a2;
  float denom = (NdotH2 * (a2 - 1.0) + 1.0);
  denom = 3.14159 * denom * denom;
  
  return nom / denom;
}

float GeometrySchlickGGX(float NdotV, float roughness) {
  float r = (roughness + 1.0);
  float k = (r * r) / 8.0;
  
  float nom = NdotV;
  float denom = NdotV * (1.0 - k) + k;
  
  return nom / denom;
}

float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
  float NdotV = max(dot(N, V), 0.0);
  float NdotL = max(dot(N, L), 0.0);
  float ggx2 = GeometrySchlickGGX(NdotV, roughness);
  float ggx1 = GeometrySchlickGGX(NdotL, roughness);
  
  return ggx1 * ggx2;
}

vec3 fresnelSchlick(float cosTheta, vec3 F0) {
  return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

void main() {
  vec3 N = normalize(vNormal);
  vec3 V = normalize(uCameraPosition - vWorldPosition);
  vec3 L = normalize(uLightPosition - vWorldPosition);
  vec3 H = normalize(V + L);
  
  // Cook-Torrance BRDF
  float NDF = DistributionGGX(N, H, uRoughness);
  float G = GeometrySmith(N, V, L, uRoughness);
  vec3 F = fresnelSchlick(max(dot(H, V), 0.0), vec3(0.04));
  
  vec3 numerator = NDF * G * F;
  float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
  vec3 specular = numerator / denominator;
  
  vec3 kS = F;
  vec3 kD = vec3(1.0) - kS;
  kD *= 1.0 - uMetallic;
  
  float NdotL = max(dot(N, L), 0.0);
  vec3 Lo = (kD * uAlbedo / 3.14159 + specular) * uLightColor * NdotL;
  
  vec3 color = Lo;
  
  // Tone mapping
  color = color / (color + vec3(1.0));
  color = pow(color, vec3(1.0/2.2));
  
  gl_FragColor = vec4(color, 1.0);
}
''',
        }

    @classmethod
    def get_post_processing_templates(cls) -> Dict[str, str]:
        """Get post-processing shader templates"""
        return {
            "bloom": '''
// Bloom Post-Processing Effect
// Requires render targets for multi-pass rendering

// Extract bright areas
uniform sampler2D tDiffuse;
uniform float uThreshold;
uniform float uStrength;

varying vec2 vUv;

void main() {
  vec4 color = texture2D(tDiffuse, vUv);
  
  // Extract luminance
  float brightness = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
  
  // Extract bright areas
  if (brightness > uThreshold) {
    gl_FragColor = color * uStrength;
  } else {
    gl_FragColor = vec4(0.0);
  }
}
''',

            "blur": '''
// Gaussian Blur Post-Processing
uniform sampler2D tDiffuse;
uniform vec2 uResolution;
uniform float uBlurSize;
uniform bool uHorizontal;

varying vec2 vUv;

// Gaussian weights
const float weights[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

void main() {
  vec2 texelSize = 1.0 / uResolution;
  vec3 result = texture2D(tDiffuse, vUv).rgb * weights[0];
  
  if (uHorizontal) {
    for (int i = 1; i < 5; i++) {
      result += texture2D(tDiffuse, vUv + vec2(texelSize.x * float(i) * uBlurSize, 0.0)).rgb * weights[i];
      result += texture2D(tDiffuse, vUv - vec2(texelSize.x * float(i) * uBlurSize, 0.0)).rgb * weights[i];
    }
  } else {
    for (int i = 1; i < 5; i++) {
      result += texture2D(tDiffuse, vUv + vec2(0.0, texelSize.y * float(i) * uBlurSize)).rgb * weights[i];
      result += texture2D(tDiffuse, vUv - vec2(0.0, texelSize.y * float(i) * uBlurSize)).rgb * weights[i];
    }
  }
  
  gl_FragColor = vec4(result, 1.0);
}
''',

            "vignette": '''
// Vignette Post-Processing
uniform sampler2D tDiffuse;
uniform float uIntensity;
uniform float uSmoothness;

varying vec2 vUv;

void main() {
  vec4 color = texture2D(tDiffuse, vUv);
  
  // Calculate distance from center
  vec2 center = vec2(0.5);
  float dist = distance(vUv, center);
  
  // Apply vignette
  float vignette = smoothstep(0.8, uSmoothness, dist * (uIntensity + uSmoothness));
  color.rgb = mix(color.rgb, color.rgb * vignette, uIntensity);
  
  gl_FragColor = color;
}
''',

            "chromatic": '''
// Chromatic Aberration
uniform sampler2D tDiffuse;
uniform float uStrength;
uniform vec2 uResolution;

varying vec2 vUv;

void main() {
  vec2 dir = vUv - vec2(0.5);
  float dist = length(dir);
  
  vec2 offset = dir * dist * uStrength;
  
  // Sample RGB at different offsets
  float r = texture2D(tDiffuse, vUv + offset).r;
  float g = texture2D(tDiffuse, vUv).g;
  float b = texture2D(tDiffuse, vUv - offset).b;
  
  gl_FragColor = vec4(r, g, b, 1.0);
}
''',
        }

    @classmethod
    def get_threejs_shader_material_template(cls) -> str:
        """Get Three.js ShaderMaterial template"""
        return '''
// Three.js ShaderMaterial Integration
import * as THREE from 'three'

const vertexShader = \`
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vPosition;
  uniform float uTime;
  
  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);
    vPosition = position;
    
    // Animate vertices
    vec3 pos = position;
    pos.y += sin(position.x * 2.0 + uTime) * 0.1;
    
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
\`

const fragmentShader = \`
  precision highp float;
  
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vPosition;
  
  uniform float uTime;
  uniform vec3 uColor;
  
  void main() {
    // Create wave effect
    float wave = sin(vUv.y * 10.0 + uTime) * 0.5 + 0.5;
    
    // Mix colors
    vec3 color = mix(uColor, uColor * 1.5, wave);
    
    // Add lighting
    float lighting = dot(vNormal, normalize(vec3(1.0, 1.0, 1.0))) * 0.5 + 0.5;
    
    gl_FragColor = vec4(color * lighting, 1.0);
  }
\`

// Create shader material
const material = new THREE.ShaderMaterial({
  vertexShader,
  fragmentShader,
  uniforms: {
    uTime: { value: 0 },
    uColor: { value: new THREE.Color(0x00ff88) }
  },
  wireframe: false,
  side: THREE.DoubleSide
})

// Update uniforms in animation loop
function animate() {
  material.uniforms.uTime.value = performance.now() / 1000
  requestAnimationFrame(animate)
}
animate()

// Use with mesh
const geometry = new THREE.PlaneGeometry(2, 2, 32, 32)
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)
'''

    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main skill invocation"""
        context = context or {}
        task_lower = task.lower()
        
        result_type = "vertex"
        if "fragment" in task_lower or "pixel" in task_lower:
            result_type = "fragment"
        elif "noise" in task_lower:
            result_type = "noise"
        elif "fresnel" in task_lower or "rim" in task_lower:
            result_type = "fresnel"
        elif "pbr" in task_lower or "physical" in task_lower:
            result_type = "pbr"
        elif "post" in task_lower or "bloom" in task_lower or "blur" in task_lower:
            result_type = "post"
        elif "displacement" in task_lower or "bump" in task_lower:
            result_type = "displacement"
        elif "three" in task_lower or "threejs" in task_lower:
            result_type = "threejs"
        
        templates = {
            "vertex": cls.get_vertex_shader_template(),
            "fragment": cls.get_fragment_shader_templates()["basic"],
            "noise": cls.get_fragment_shader_templates()["noise"],
            "fresnel": cls.get_fragment_shader_templates()["fresnel"],
            "pbr": cls.get_fragment_shader_templates()["pbr"],
            "displacement": cls.get_fragment_shader_templates()["displacement"],
            "post": list(cls.get_post_processing_templates().values())[0],
            "threejs": cls.get_threejs_shader_material_template(),
        }
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "vertex_template": cls.get_vertex_shader_template(),
            "fragment_templates": cls.get_fragment_shader_templates(),
            "post_processing_templates": cls.get_post_processing_templates(),
            "threejs_template": cls.get_threejs_shader_material_template(),
            "key_concepts": {
                "attribute": "Per-vertex data (position, normal, UV)",
                "uniform": "Global data (matrices, time, colors)",
                "varying": "Data passed from vertex to fragment shader",
                "gl_Position": "Final vertex position (required)",
                "gl_FragColor": "Final fragment color (required)",
            },
            "tips": [
                "Always declare precision in fragment shaders",
                "Use normalMatrix for correct normal transformation",
                "Combine multiple effects in single pass when possible",
                "Use render targets for multi-pass post-processing",
                "Use time uniform for animated shaders"
            ]
        }


# Convenience function
def generate_glsl(task: str, **kwargs) -> Dict[str, Any]:
    return GLSLShaderSkill.invoke(task, kwargs)
