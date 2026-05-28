"""
Lenis Smooth Scroll Skill - Smooth Scrolling
Lenis integration with GSAP, Locomotive Scroll alternative
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class LenisSmoothScrollSkill:
    """
    Lenis smooth scroll skill for buttery smooth scrolling.
    Integrates with GSAP ScrollTrigger, RAF updates, parallax.
    """
    
    NAME = "lenis_scroll"
    DESCRIPTION = "Lenis smooth scroll - Smooth scrolling, GSAP integration, parallax, momentum"
    TRIGGERS = [
        "lenis", "smooth scroll", "locomotive scroll",
        "momentum scroll", "lerp scroll", "smooth scrolling",
        "parallax scroll", "gsap lenis"
    ]
    
    @classmethod
    def get_basic_setup_template(cls) -> str:
        """Get basic Lenis setup"""
        return '''
// Lenis Smooth Scroll - Basic Setup
import Lenis from 'lenis'

// Initialize Lenis
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  orientation: 'vertical',
  gestureOrientation: 'vertical',
  smoothWheel: true,
  wheelMultiplier: 1,
  touchMultiplier: 2,
  infinite: false,
})

// RAF loop for smooth updates
function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)

// Scroll event (debounced)
lenis.on('scroll', ({ scroll, limit, velocity }) => {
  console.log('Scroll:', scroll, 'Velocity:', velocity)
})
'''

    @classmethod
    def get_gsap_integration_template(cls) -> str:
        """Get GSAP ScrollTrigger integration template"""
        return '''
// Lenis + GSAP ScrollTrigger Integration
import Lenis from 'lenis'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// Initialize Lenis
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
})

// RAF loop with GSAP
function raf(time) {
  lenis.raf(time)
  gsap.updateRoot(time * 0.001) // Update GSAP's time
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)

// Connect ScrollTrigger to Lenis
lenis.on('scroll', ScrollTrigger.update)

// GSAP animations work with Lenis now!
// Just use ScrollTrigger normally

gsap.to('.element', {
  scrollTrigger: {
    trigger: '.element',
    start: 'top bottom',
    end: 'bottom top',
    scrub: 1
  },
  x: 500,
  rotation: 360
})

// Clean up on unmount
function destroy() {
  lenis.destroy()
}
'''

    @classmethod
    def get_parallax_template(cls) -> str:
        """Get parallax with Lenis template"""
        return '''
// Lenis Parallax Effect
import Lenis from 'lenis'

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
})

// Track scroll for parallax
let scrollY = 0

lenis.on('scroll', ({ scroll }) => {
  scrollY = scroll
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)

// Parallax effect (CSS-based)
const parallaxElements = document.querySelectorAll('.parallax')

parallaxElements.forEach((el) => {
  const speed = parseFloat(el.dataset.speed) || 0.5
  
  function updateParallax() {
    const y = window.scrollY * speed
    el.style.transform = `translateY(${y}px)`
    requestAnimationFrame(updateParallax)
  }
  
  updateParallax()
})

// JS-based parallax (smoother)
const jsParallax = document.querySelectorAll('.js-parallax')

jsParallax.forEach((el) => {
  const speed = parseFloat(el.dataset.speed) || 0.5
  const rect = el.getBoundingClientRect()
  const initialTop = rect.top + window.scrollY
  
  function updateJSParallax() {
    const currentScroll = window.scrollY
    const relativeScroll = currentScroll - initialTop
    const y = relativeScroll * speed
    el.style.transform = `translateY(${y}px)`
  }
  
  // Use Lenis scroll event
  lenis.on('scroll', updateJSParallax)
})
'''

    @classmethod
    def get_horizontal_scroll_template(cls) -> str:
        """Get horizontal scroll with Lenis template"""
        return '''
// Lenis Horizontal Scroll
import Lenis from 'lenis'

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  gestureOrientation: 'horizontal',
  smoothWheel: false, // Disable for horizontal
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)

// Horizontal scroll with wheel
const horizontalSection = document.querySelector('.horizontal-container')
const horizontalItems = document.querySelectorAll('.horizontal-item')
const totalWidth = Array.from(horizontalItems).reduce(
  (acc, item) => acc + item.offsetWidth,
  0
)

// Convert vertical scroll to horizontal movement
lenis.on('scroll', ({ scroll, limit, velocity }) => {
  const scrollPercent = scroll / limit
  const translateX = scrollPercent * (totalWidth - window.innerWidth)
  horizontalSection.style.transform = `translateX(-${translateX}px)`
})
'''

    @classmethod
    def get_vertical_loop_template(cls) -> str:
        """Get infinite vertical loop scroll template"""
        return '''
// Lenis Infinite Vertical Loop
import Lenis from 'lenis'

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  infinite: true, // Enable infinite scroll
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)

// Items to loop
const items = document.querySelectorAll('.loop-item')
let currentIndex = 0

lenis.on('scroll', ({ scroll, limit, velocity }) => {
  // Calculate which item should be centered
  const itemHeight = items[0].offsetHeight
  const visibleItems = Math.ceil(window.innerHeight / itemHeight)
  const newIndex = Math.floor(scroll / itemHeight) % items.length
  
  if (newIndex !== currentIndex) {
    currentIndex = newIndex
    
    // Update active state or trigger animations
    items.forEach((item, i) => {
      item.classList.toggle('active', i === currentIndex)
    })
  }
})
'''

    @classmethod
    def get_sticky_sections_template(cls) -> str:
        """Get sticky sections with Lenis template"""
        return '''
// Lenis with Sticky Sections
import Lenis from 'lenis'

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)

// Sticky sections
const stickySections = document.querySelectorAll('.sticky-section')

stickySections.forEach((section) => {
  const inner = section.querySelector('.sticky-inner')
  const start = section.offsetTop
  const end = start + section.offsetHeight - window.innerHeight
  
  function updateSticky() {
    const scrollY = window.scrollY
    
    if (scrollY >= start && scrollY <= end) {
      const progress = (scrollY - start) / (end - start)
      // Animate based on progress
      inner.style.transform = `translateY(${-progress * 100}px)`
    }
  }
  
  lenis.on('scroll', updateSticky)
})
'''

    @classmethod
    def get_reveal_on_scroll_template(cls) -> str:
        """Get reveal animations on scroll with Lenis"""
        return '''
// Lenis Reveal on Scroll
import Lenis from 'lenis'

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)

// Reveal elements on scroll
const revealElements = document.querySelectorAll('.reveal')

function checkReveal() {
  revealElements.forEach((el) => {
    const rect = el.getBoundingClientRect()
    const isVisible = rect.top < window.innerHeight * 0.8
    
    if (isVisible && !el.classList.contains('revealed')) {
      el.classList.add('revealed')
      el.classList.add('animate')
    }
  })
}

// Use Lenis scroll event for reveal
lenis.on('scroll', checkReveal)

// Initial check
checkReveal()

// CSS for reveal
/*
.reveal {
  opacity: 0;
  transform: translateY(50px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.reveal.animate {
  opacity: 1;
  transform: translateY(0);
}
*/
'''

    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main skill invocation"""
        context = context or {}
        task_lower = task.lower()
        
        result_type = "basic"
        if "gsap" in task_lower or "scrolltrigger" in task_lower:
            result_type = "gsap"
        elif "parallax" in task_lower:
            result_type = "parallax"
        elif "horizontal" in task_lower:
            result_type = "horizontal"
        elif "loop" in task_lower or "infinite" in task_lower:
            result_type = "loop"
        elif "sticky" in task_lower or "pin" in task_lower:
            result_type = "sticky"
        elif "reveal" in task_lower or "animation" in task_lower:
            result_type = "reveal"
        
        templates = {
            "basic": cls.get_basic_setup_template(),
            "gsap": cls.get_gsap_integration_template(),
            "parallax": cls.get_parallax_template(),
            "horizontal": cls.get_horizontal_scroll_template(),
            "loop": cls.get_vertical_loop_template(),
            "sticky": cls.get_sticky_sections_template(),
            "reveal": cls.get_reveal_on_scroll_template(),
        }
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "template": templates[result_type],
            "dependencies": ["lenis"],
            "tips": [
                "Always use RAF loop for smooth updates",
                "Connect Lenis to GSAP ScrollTrigger with lenis.on('scroll', ScrollTrigger.update)",
                "Use duration and easing options for control",
                "Combine with GSAP for powerful scroll animations",
                "Use data attributes for parallax speeds"
            ]
        }


# Convenience function
def generate_lenis(task: str, **kwargs) -> Dict[str, Any]:
    return LenisSmoothScrollSkill.invoke(task, kwargs)
