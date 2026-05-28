"""
Spline Design Pipeline Skill
Spline 3D design, curve mathematics, export pipelines
"""

from typing import Dict, List, Any, Optional


class SplineDesignSkill:
    """Spline curve design and 3D modeling pipeline"""
    
    NAME = "spline_design"
    DESCRIPTION = "Spline design - Bezier curves, NURBS, 3D modeling, export pipeline, curve mathematics"
    TRIGGERS = [
        "spline", "bezier", "curve", "nurbs", "path",
        "3d model", "export", "vector", "canvas path",
        "animation path", "motion path"
    ]
    
    @classmethod
    def get_bezier_templates(cls) -> Dict[str, str]:
        return {
            "quadratic": '''
// Quadratic Bezier Curve
function quadraticBezier(p0, p1, p2, t) {
  return (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2
}

// Canvas implementation
function drawQuadraticBezier(ctx, p0, p1, p2) {
  ctx.beginPath()
  ctx.moveTo(p0.x, p0.y)
  ctx.quadraticCurveTo(p1.x, p1.y, p2.x, p2.y)
  ctx.stroke()
}

// Three.js CatmullRom
const curve = new THREE.QuadraticBezierCurve3(
  new THREE.Vector3(0, 0, 0),
  new THREE.Vector3(1, 2, 0),
  new THREE.Vector3(2, 0, 0)
)
const points = curve.getPoints(50)
const geometry = new THREE.BufferGeometry().setFromPoints(points)
''',
            "cubic": '''
// Cubic Bezier Curve
function cubicBezier(p0, p1, p2, p3, t) {
  const mt = 1 - t
  return mt**3 * p0 + 3*mt**2*t * p1 + 3*mt*t**2 * p2 + t**3 * p3
}

// Canvas implementation
function drawCubicBezier(ctx, p0, p1, p2, p3) {
  ctx.beginPath()
  ctx.moveTo(p0.x, p0.y)
  ctx.bezierCurveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
  ctx.stroke()
}

// Three.js Cubic Bezier
const curve = new THREE.CubicBezierCurve3(
  new THREE.Vector3(0, 0, 0),
  new THREE.Vector3(0, 2, 0),
  new THREE.Vector3(2, 2, 0),
  new THREE.Vector3(2, 0, 0)
)
''',
            "catmullrom": '''
// Catmull-Rom Spline (smooth through points)
function catmullRom(p0, p1, p2, p3, t, tension = 0.5) {
  const t2 = t * t
  const t3 = t2 * t
  return 0.5 * (
    (2 * p1) +
    (-p0 + p2) * t +
    (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
    (-p0 + 3*p1 - 3*p2 + p3) * t3
  )
}

// Three.js CatmullRomCurve3
const points = [
  new THREE.Vector3(0, 0, 0),
  new THREE.Vector3(1, 1, 0),
  new THREE.Vector3(2, 0.5, 0),
  new THREE.Vector3(3, 1, 0),
  new THREE.Vector3(4, 0, 0)
]
const curve = new THREE.CatmullRomCurve3(points, closed = false)
const curvePoints = curve.getPoints(100)
'''
        }
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()
        
        result_type = "bezier"
        if "catmull" in task_lower or "spline" in task_lower:
            result_type = "catmullrom"
        elif "quadratic" in task_lower:
            result_type = "quadratic"
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "templates": cls.get_bezier_templates(),
            "tips": ["Use getPoints(n) for smooth curves", "CatmullRom for smooth interpolation"]
        }


def generate_spline(task: str, **kwargs) -> Dict[str, Any]:
    return SplineDesignSkill.invoke(task, kwargs)
