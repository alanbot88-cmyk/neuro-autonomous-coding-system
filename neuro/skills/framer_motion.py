"""
Framer Motion Layout Skill - Layout Animations
AnimatePresence, layout animations, shared layout transitions, gestures
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class FramerMotionSkill:
    """
    Framer Motion skill for layout animations and transitions.
    Handles AnimatePresence, shared layout transitions, gestures.
    """
    
    NAME = "framer_motion"
    DESCRIPTION = "Framer Motion animations - Layout transitions, AnimatePresence, shared layouts, gestures, page transitions"
    TRIGGERS = [
        "framer-motion", "framer", "layout animation", "shared layout",
        "page transition", "animate presence", "gesture",
        "motion div", "layout group", "drag"
    ]
    
    @classmethod
    def get_layout_templates(cls) -> str:
        """Get layout animation templates"""
        return '''
// Framer Motion Layout Animations
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion'

// Shared Layout Transition (key for list reordering)
const items = [
  { id: 1, name: 'Item 1' },
  { id: 2, name: 'Item 2' },
  { id: 3, name: 'Item 3' }
]

function SharedLayoutExample() {
  const [list, setList] = useState(items)
  
  return (
    <LayoutGroup>
      <AnimatePresence mode="popLayout">
        {list.map((item) => (
          <motion.div
            key={item.id}
            layout
            layoutId={`item-${item.id}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {item.name}
          </motion.div>
        ))}
      </AnimatePresence>
    </LayoutGroup>
  )
}

// Layout animation on container
function ContainerLayout() {
  const [isBig, setIsBig] = useState(false)
  
  return (
    <motion.div
      layout
      onClick={() => setIsBig(!isBig)}
      style={{
        width: isBig ? 400 : 200,
        height: isBig ? 400 : 200,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: 20
      }}
    >
      Click to animate!
    </motion.div>
  )
}
'''

    @classmethod
    def get_page_transition_templates(cls) -> str:
        """Get page transition templates"""
        return '''
// Framer Motion Page Transitions
import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'

// Wrap your app with this
function App() {
  const location = useLocation()
  
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, x: 100 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -100 }}
        transition={{ 
          type: 'tween',
          ease: 'anticipate',
          duration: 0.3 
        }}
      >
        {/* Your page content */}
      </motion.div>
    </AnimatePresence>
  )
}

// Staggered page entrance
function StaggeredPage() {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  }
  
  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { 
      opacity: 1, 
      y: 0,
      transition: { type: 'spring', stiffness: 300, damping: 24 }
    }
  }
  
  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
    >
      {[1, 2, 3, 4, 5].map((i) => (
        <motion.div key={i} variants={item}>
          Content {i}
        </motion.div>
      ))}
    </motion.div>
  )
}

// Slide up modal
function Modal() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      >
        Modal Content
      </motion.div>
    </motion.div>
  )
}
'''

    @classmethod
    def get_gesture_templates(cls) -> str:
        """Get gesture animation templates"""
        return '''
// Framer Motion Gestures
import { motion, useMotionValue, useTransform } from 'framer-motion'

// Drag gesture
function DraggableCard() {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: -100, right: 100 }}
      dragElastic={0.1}
      whileDrag={{ scale: 1.05, cursor: 'grabbing' }}
      whileTap={{ cursor: 'grabbing' }}
      onDragEnd={(e, { offset, velocity }) => {
        console.log('Drag ended:', { offset, velocity })
      }}
    >
      Drag me!
    </motion.div>
  )
}

// Multi-drag with constraints
function MultiDrag() {
  return (
    <motion.div
      drag
      dragMomentum={false}
      dragConstraints={{
        left: -150,
        right: 150,
        top: -150,
        bottom: 150
      }}
      whileDrag={{ cursor: 'grabbing' }}
    >
      Drag anywhere
    </motion.div>
  )
}

// Hover and tap gestures
function InteractiveButton() {
  return (
    <motion.button
      whileHover={{ 
        scale: 1.05,
        backgroundColor: '#764ba2'
      }}
      whileTap={{ 
        scale: 0.95,
        backgroundColor: '#667eea'
      }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      Click or hover
    </motion.button>
  )
}

// Scroll-linked animation with useScroll
function ScrollAnimation() {
  const { scrollYProgress } = useScroll()
  const scale = useTransform(scrollYProgress, [0, 1], [1, 2])
  const rotate = useTransform(scrollYProgress, [0, 1], [0, 360])
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 1, 0])
  
  return (
    <motion.div
      style={{ scale, rotate, opacity }}
    >
      Scroll to animate me!
    </motion.div>
  )
}

// Pan gesture for images
function PanGallery() {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: -500, right: 0 }}
      dragElastic={0.2}
    >
      <img src="/panorama.jpg" alt="Panorama" />
    </motion.div>
  )
}

// Inertia physics on drag release
function PhysicsDrag() {
  return (
    <motion.div
      drag
      dragTransition={{ 
        bounceStiffness: 300, 
        bounceDamping: 30 
      }}
      whileDrag={{ cursor: 'grabbing' }}
    >
      Physics-based drag
    </motion.div>
  )
}
'''

    @classmethod
    def get_variants_templates(cls) -> str:
        """Get animation variants templates"""
        return '''
// Framer Motion Animation Variants
import { motion } from 'framer-motion'

// Define states as variants
const variants = {
  hidden: { 
    opacity: 0, 
    y: 50 
  },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.5,
      ease: 'easeOut'
    }
  },
  hover: {
    scale: 1.1,
    transition: { duration: 0.2 }
  },
  tap: {
    scale: 0.95,
    transition: { duration: 0.1 }
  }
}

// Using variants
function VariantBox() {
  return (
    <motion.div
      variants={variants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      whileTap="tap"
    >
      Variant Box
    </motion.div>
  )
}

// Orchestrated variants (parent controls children)
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const childVariants = {
  hidden: { x: -50, opacity: 0 },
  visible: { 
    x: 0, 
    opacity: 1,
    transition: { type: 'spring', stiffness: 300, damping: 20 }
  }
}

function OrchestratedList() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {[1, 2, 3].map(i => (
        <motion.div key={i} variants={childVariants}>
          Item {i}
        </motion.div>
      ))}
    </motion.div>
  )
}

// Dynamic variants
function DynamicVariants({{ isActive }}) {
  const variants = {
    inactive: { 
      scale: 1, 
      backgroundColor: '#gray' 
    },
    active: { 
      scale: 1.1, 
      backgroundColor: '#667eea' 
    }
  }
  
  return (
    <motion.div
      variants={variants}
      animate={isActive ? 'active' : 'inactive'}
      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
    >
      Dynamic
    </motion.div>
  )
}
'''

    @classmethod
    def get_motion_values_templates(cls) -> str:
        """Get motion values templates"""
        return '''
// Framer Motion MotionValues
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion'

// Basic motion value
function MotionValueExample() {
  const x = useMotionValue(0)
  
  return (
    <motion.div
      style={{ x }}
      drag="x"
      dragConstraints={{ left: 0, right: 1000 }}
    >
      Drag me (x: {x.get()})
    </motion.div>
  )
}

// Transform motion values
function TransformExample() {
  const { scrollYProgress } = useScroll()
  
  const scale = useTransform(scrollYProgress, [0, 1], [1, 2])
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 0])
  const color = useTransform(
    scrollYProgress,
    [0, 0.5, 1],
    ['#ff008c', '#3333ff', '#00ff88']
  )
  
  return (
    <motion.div style={{ scale, opacity, backgroundColor: color }}>
      Transformed on scroll!
    </motion.div>
  )
}

// Spring physics
function SpringExample() {
  const x = useSpring(0, {
    stiffness: 100,
    damping: 10,
    mass: 1
  })
  
  return (
    <motion.div
      style={{ x }}
      drag="x"
      dragConstraints={{ left: -500, right: 500 }}
    >
      Smooth spring physics!
    </motion.div>
  )
}

// Combine motion values
function CombinedExample() {
  const a = useMotionValue(0)
  const b = useMotionValue(0)
  
  // Combine motion values
  const combined = useTransform([a, b], ([latestA, latestB]) => latestA + latestB)
  
  return (
    <>
      <motion.div
        style={{ x: a }}
        drag="x"
      >
        A
      </motion.div>
      <motion.div
        style={{ x: combined }}
      >
        Combined: {combined.get()}
      </motion.div>
    </>
  )
}

// Mouse tracking
function MouseTrack() {
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  function handleMouseMove(event) {
    x.set(event.clientX)
    y.set(event.clientY)
  }
  
  return (
    <div onMouseMove={handleMouseMove}>
      <motion.div
        style={{ x, y }}
        transition={{ type: 'spring', stiffness: 500, damping: 50 }}
      >
        Following mouse!
      </motion.div>
    </div>
  )
}
'''

    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main skill invocation"""
        context = context or {}
        task_lower = task.lower()
        
        result_type = "layout"
        if "transition" in task_lower or "page" in task_lower:
            result_type = "page_transition"
        elif "gesture" in task_lower or "drag" in task_lower or "pan" in task_lower:
            result_type = "gesture"
        elif "variant" in task_lower or "stagger" in task_lower:
            result_type = "variant"
        elif "scroll" in task_lower:
            result_type = "scroll"
        elif "motion" in task_lower or "value" in task_lower:
            result_type = "motion_value"
        
        templates = {
            "layout": cls.get_layout_templates(),
            "page_transition": cls.get_page_transition_templates(),
            "gesture": cls.get_gesture_templates(),
            "variant": cls.get_variants_templates(),
            "scroll": cls.get_gesture_templates(),  # Reuse scroll from gestures
            "motion_value": cls.get_motion_values_templates(),
        }
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "template": templates[result_type],
            "dependencies": ["framer-motion"],
            "key_concepts": {
                "AnimatePresence": "Enables exit animations when components unmount",
                "layoutId": "Key for shared layout transitions",
                "LayoutGroup": "Groups layout animations",
                "motion.div": "Animated div component",
                "useSpring": "Physics-based animation",
                "useScroll": "Scroll position tracking"
            },
            "tips": [
                "Use layoutId to link elements across screens",
                "Use AnimatePresence for exit animations",
                "Use useSpring for smooth physics",
                "Use variants for reusable animation states",
                "Combine with useTransform for derived animations"
            ]
        }


# Convenience function
def generate_framer(task: str, **kwargs) -> Dict[str, Any]:
    return FramerMotionSkill.invoke(task, kwargs)
