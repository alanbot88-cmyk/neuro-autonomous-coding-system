"""
Vector & Matrix Mathematics Skill
3D math operations, transformations, physics calculations
"""

from typing import Dict, List, Any, Optional


class VectorMathSkill:
    """Vector & Matrix math for 3D graphics and physics"""
    
    NAME = "vector_math"
    DESCRIPTION = "Vector & Matrix math - 3D transformations, rotations, physics, quaternions, projections"
    TRIGGERS = [
        "vector", "matrix", "math", "quaternion", "rotation",
        "transform", "dot product", "cross product", "normalize",
        "lerp", "slerp", "euler", "physics", "collision"
    ]
    
    @classmethod
    def get_vector_templates(cls) -> Dict[str, str]:
        """Get vector operation templates"""
        return {
            "basic": '''
// Vector3 Class Implementation
class Vector3 {
  constructor(x = 0, y = 0, z = 0) {
    this.x = x
    this.y = y
    this.z = z
  }
  
  add(v) {
    return new Vector3(this.x + v.x, this.y + v.y, this.z + v.z)
  }
  
  subtract(v) {
    return new Vector3(this.x - v.x, this.y - v.y, this.z - v.z)
  }
  
  multiply(scalar) {
    return new Vector3(this.x * scalar, this.y * scalar, this.z * scalar)
  }
  
  dot(v) {
    return this.x * v.x + this.y * v.y + this.z * v.z
  }
  
  cross(v) {
    return new Vector3(
      this.y * v.z - this.z * v.y,
      this.z * v.x - this.x * v.z,
      this.x * v.y - this.y * v.x
    )
  }
  
  length() {
    return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z)
  }
  
  normalize() {
    const len = this.length()
    if (len === 0) return new Vector3()
    return new Vector3(this.x / len, this.y / len, this.z / len)
  }
  
  lerp(v, t) {
    return new Vector3(
      this.x + (v.x - this.x) * t,
      this.y + (v.y - this.y) * t,
      this.z + (v.z - this.z) * t
    )
  }
  
  distance(v) {
    return this.subtract(v).length()
  }
}
''',

            "transformations": '''
// Matrix4 Transformation Operations
// 4x4 transformation matrices for 3D graphics

// Identity matrix
const identity = [
  [1, 0, 0, 0],
  [0, 1, 0, 0],
  [0, 0, 1, 0],
  [0, 0, 0, 1]
]

// Translation matrix
function translationMatrix(x, y, z) {
  return [
    [1, 0, 0, x],
    [0, 1, 0, y],
    [0, 0, 1, z],
    [0, 0, 0, 1]
  ]
}

// Scale matrix
function scaleMatrix(sx, sy, sz) {
  return [
    [sx, 0, 0, 0],
    [0, sy, 0, 0],
    [0, 0, sz, 0],
    [0, 0, 0, 1]
  ]
}

// Rotation around X axis
function rotationXMatrix(angle) {
  const c = Math.cos(angle)
  const s = Math.sin(angle)
  return [
    [1, 0, 0, 0],
    [0, c, -s, 0],
    [0, s, c, 0],
    [0, 0, 0, 1]
  ]
}

// Rotation around Y axis
function rotationYMatrix(angle) {
  const c = Math.cos(angle)
  const s = Math.sin(angle)
  return [
    [c, 0, s, 0],
    [0, 1, 0, 0],
    [-s, 0, c, 0],
    [0, 0, 0, 1]
  ]
}

// Rotation around Z axis
function rotationZMatrix(angle) {
  const c = Math.cos(angle)
  const s = Math.sin(angle)
  return [
    [c, -s, 0, 0],
    [s, c, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
  ]
}

// Matrix multiplication
function multiplyMatrices(a, b) {
  const result = []
  for (let i = 0; i < 4; i++) {
    result[i] = []
    for (let j = 0; j < 4; j++) {
      result[i][j] = 
        a[i][0] * b[0][j] +
        a[i][1] * b[1][j] +
        a[i][2] * b[2][j] +
        a[i][3] * b[3][j]
    }
  }
  return result
}
''',

            "quaternions": '''
// Quaternion for Rotation
// Avoids gimbal lock, better interpolation than Euler

class Quaternion {
  constructor(x = 0, y = 0, z = 0, w = 1) {
    this.x = x
    this.y = y
    this.z = z
    this.w = w
  }
  
  // Create from Euler angles
  static fromEuler(x, y, z) {
    const cx = Math.cos(x / 2)
    const sx = Math.sin(x / 2)
    const cy = Math.cos(y / 2)
    const sy = Math.sin(y / 2)
    const cz = Math.cos(z / 2)
    const sz = Math.sin(z / 2)
    
    return new Quaternion(
      sx * cy * cz - cx * sy * sz,
      cx * sy * cz + sx * cy * sz,
      cx * cy * sz - sx * sy * cz,
      cx * cy * cz + sx * sy * sz
    )
  }
  
  // Convert to rotation matrix
  toMatrix() {
    const xx = this.x * this.x
    const yy = this.y * this.y
    const zz = this.z * this.z
    const xy = this.x * this.y
    const xz = this.x * this.z
    const yz = this.y * this.z
    const wx = this.w * this.x
    const wy = this.w * this.y
    const wz = this.w * this.z
    
    return [
      [1 - 2*(yy + zz), 2*(xy - wz), 2*(xz + wy), 0],
      [2*(xy + wz), 1 - 2*(xx + zz), 2*(yz - wx), 0],
      [2*(xz - wy), 2*(yz + wx), 1 - 2*(xx + yy), 0],
      [0, 0, 0, 1]
    ]
  }
  
  // Spherical linear interpolation
  slerp(q, t) {
    let cosHalfTheta = this.w * q.w + this.x * q.x + this.y * q.y + this.z * q.z
    
    if (Math.abs(cosHalfTheta) >= 1) {
      return new Quaternion(this.x, this.y, this.z, this.w)
    }
    
    const halfTheta = Math.acos(cosHalfTheta)
    const sinHalfTheta = Math.sqrt(1 - cosHalfTheta * cosHalfTheta)
    
    const ratioA = Math.sin((1 - t) * halfTheta) / sinHalfTheta
    const ratioB = Math.sin(t * halfTheta) / sinHalfTheta
    
    return new Quaternion(
      this.x * ratioA + q.x * ratioB,
      this.y * ratioA + q.y * ratioB,
      this.z * ratioA + q.z * ratioB,
      this.w * ratioA + q.w * ratioB
    )
  }
  
  multiply(q) {
    return new Quaternion(
      this.w * q.x + this.x * q.w + this.y * q.z - this.z * q.y,
      this.w * q.y - this.x * q.z + this.y * q.w + this.z * q.x,
      this.w * q.z + this.x * q.y - this.y * q.x + this.z * q.w,
      this.w * q.w - this.x * q.x - this.y * q.y - this.z * q.z
    )
  }
}
''',

            "collision": '''
// Collision Detection Math
// Bounding volumes and intersection tests

// Sphere-Sphere collision
function sphereSphereCollision(s1, s2) {
  const distance = Math.sqrt(
    Math.pow(s2.x - s1.x, 2) +
    Math.pow(s2.y - s1.y, 2) +
    Math.pow(s2.z - s1.z, 2)
  )
  return distance < (s1.radius + s2.radius)
}

// AABB (Axis-Aligned Bounding Box) collision
function aabbCollision(a, b) {
  return (
    a.min.x <= b.max.x && a.max.x >= b.min.x &&
    a.min.y <= b.max.y && a.max.y >= b.min.y &&
    a.min.z <= b.max.z && a.max.z >= b.min.z
  )
}

// Ray-Sphere intersection
function raySphereIntersect(rayOrigin, rayDir, sphereCenter, sphereRadius) {
  const oc = rayOrigin.subtract(sphereCenter)
  const a = rayDir.dot(rayDir)
  const b = 2 * oc.dot(rayDir)
  const c = oc.dot(oc) - sphereRadius * sphereRadius
  const discriminant = b * b - 4 * a * c
  
  if (discriminant < 0) return null
  
  const t = (-b - Math.sqrt(discriminant)) / (2 * a)
  return t >= 0 ? t : null
}

// Ray-Plane intersection
function rayPlaneIntersect(rayOrigin, rayDir, planePoint, planeNormal) {
  const denominator = rayDir.dot(planeNormal)
  if (Math.abs(denominator) < 0.0001) return null
  
  const t = planePoint.subtract(rayOrigin).dot(planeNormal) / denominator
  return t >= 0 ? t : null
}
''',
        }
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()
        
        result_type = "basic"
        if "matrix" in task_lower or "transform" in task_lower:
            result_type = "transformations"
        elif "quaternion" in task_lower or "rotation" in task_lower:
            result_type = "quaternions"
        elif "collision" in task_lower or "detect" in task_lower or "intersect" in task_lower:
            result_type = "collision"
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "templates": cls.get_vector_templates(),
            "key_operations": {
                "dot_product": "a·b = ax*bx + ay*by + az*bz (projection)",
                "cross_product": "a×b = perpendicular vector (surface normal)",
                "normalize": "v/|v| = unit vector",
                "lerp": "Linear interpolation between vectors",
                "slerp": "Spherical interpolation for rotations"
            }
        }


def generate_math(task: str, **kwargs) -> Dict[str, Any]:
    return VectorMathSkill.invoke(task, kwargs)
