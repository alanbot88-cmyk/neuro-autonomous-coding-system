"""
GSAP ScrollTrigger Skill - Scroll-Driven Animations
Scroll-based animations, parallax effects, timeline scrubbing
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class GSAPScrollSkill:
    """
    GSAP ScrollTrigger skill for scroll-driven animations.
    Creates scroll-based animations, parallax, timeline scrubbing.
    """
    
    NAME = "gsap_scroll"
    DESCRIPTION = "GSAP ScrollTrigger animations - Scroll-driven, parallax, timeline scrubbing, pin effects"
    TRIGGERS = [
        "gsap", "scrolltrigger", "scroll", "parallax",
        "scroll animation", "pinning", "scrubbing",
        "scroll-driven", "tween", "timeline"
    ]
    
    @classmethod
    def get_basic_scroll_template(cls) -> str:
        """Get basic scroll animation template"""
        return '''
// GSAP ScrollTrigger - Basic Scroll Animation
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

// Basic scroll animation
gsap.to(".element", {
  scrollTrigger: {
    trigger: ".element",
    start: "top bottom",
    end: "bottom top",
    scrub: 1, // Smooth scrubbing
    markers: true // Debug markers
  },
  x: 400,
  rotation: 360,
  ease: "power2.inOut"
})

// Fade in on scroll
gsap.from(".fade-element", {
  scrollTrigger: {
    trigger: ".fade-element",
    start: "top 80%",
    toggleActions: "play none none reverse"
  },
  opacity: 0,
  y: 50,
  duration: 1
})
'''

    @classmethod
    def get_parallax_template(cls) -> str:
        """Get parallax effect template"""
        return '''
// GSAP Parallax Effect
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

// Parallax layers (different speeds)
const parallaxSections = document.querySelectorAll('.parallax-section')

parallaxSections.forEach((section, index) => {
  const layer = section.querySelector('.parallax-layer')
  const speed = 0.5 + (index * 0.2) // Faster for background
  
  gsap.to(layer, {
    yPercent: -30 * speed,
    ease: "none",
    scrollTrigger: {
      trigger: section,
      start: "top bottom",
      end: "bottom top",
      scrub: true
    }
  })
})

// Image parallax
gsap.to(".parallax-image", {
  yPercent: -20,
  ease: "none",
  scrollTrigger: {
    trigger: ".parallax-container",
    start: "top bottom",
    end: "bottom top",
    scrub: 0.5
  }
})

// Text parallax (slower)
gsap.to(".hero-text", {
  yPercent: -50,
  opacity: 0,
  ease: "none",
  scrollTrigger: {
    trigger: ".hero-section",
    start: "top top",
    end: "bottom top",
    scrub: 1
  }
})
'''

    @classmethod
    def get_pinned_section_template(cls) -> str:
        """Get pinned section template"""
        return '''
// GSAP Pinned Scroll Section
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

// Pinned section with timeline
const pinnedTimeline = gsap.timeline({
  scrollTrigger: {
    trigger: ".pinned-section",
    start: "top top",
    end: "+=3000", // Pin for 3000px of scroll
    pin: true,
    scrub: 1,
    anticipatePin: 1
  }
})

// Timeline animations
pinnedTimeline
  .from(".step-1", { opacity: 0, y: 50 })
  .to(".step-1", { opacity: 0, y: -50, duration: 0.5 })
  .from(".step-2", { opacity: 0, y: 50 })
  .to(".step-2", { opacity: 0, y: -50, duration: 0.5 })
  .from(".step-3", { opacity: 0, y: 50 })
  .to(".step-3", { opacity: 0, y: -50, duration: 0.5 })

// Horizontal scroll pin
gsap.to(".horizontal-content", {
  xPercent: -100 * (document.querySelectorAll('.horizontal-item').length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-container",
    start: "top top",
    end: () => "+=" + document.querySelector(".horizontal-content").offsetWidth,
    pin: true,
    scrub: 1,
    snap: {
      snapTo: 1 / (document.querySelectorAll('.horizontal-item').length - 1),
      duration: { min: 0.2, max: 0.6 },
      delay: 0.1
    }
  }
})
'''

    @classmethod
    def get_horizontal_scroll_template(cls) -> str:
        """Get horizontal scroll template"""
        return '''
// Horizontal Scroll Section
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

// Horizontal scroll with sections
const sections = gsap.utils.toArray('.horizontal-section')

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-wrapper",
    start: "top top",
    end: () => "+=" + (sections.length - 1) * window.innerWidth,
    scrub: 1,
    pin: true,
    anticipatePin: 1,
    snap: {
      snapTo: 1 / (sections.length - 1),
      duration: { min: 0.2, max: 0.5 }
    }
  }
})

// Section-specific animations
sections.forEach((section, index) => {
  const elements = section.querySelectorAll('.animate-in')
  
  gsap.from(elements, {
    y: 100,
    opacity: 0,
    stagger: 0.1,
    duration: 1,
    scrollTrigger: {
      trigger: section,
      containerAnimation: ScrollTrigger.getAll()[0].animation,
      start: "left center",
      toggleActions: "play none none reverse"
    }
  })
})
'''

    @classmethod
    def get_reveal_effects_template(cls) -> str:
        """Get reveal effects template"""
        return '''
// Scroll Reveal Effects
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

// Staggered reveal
gsap.utils.toArray('.reveal-stagger').forEach((element) => {
  const children = element.querySelectorAll('.reveal-item')
  
  gsap.from(children, {
    y: 100,
    opacity: 0,
    stagger: 0.1,
    duration: 0.8,
    ease: "power3.out",
    scrollTrigger: {
      trigger: element,
      start: "top 80%",
      toggleActions: "play none none reverse"
    }
  })
})

// Character-by-character reveal (SplitText-like)
const splitText = (element) => {
  const text = element.textContent
  element.innerHTML = text.split('').map(char => 
    char === ' ' ? ' ' : `<span class="char">${char}</span>`
  ).join('')
  return element.querySelectorAll('.char')
}

document.querySelectorAll('.split-text').forEach(el => {
  const chars = splitText(el)
  
  gsap.from(chars, {
    opacity: 0,
    y: 50,
    rotateX: -90,
    stagger: 0.02,
    duration: 0.5,
    ease: "power2.out",
    scrollTrigger: {
      trigger: el,
      start: "top 80%",
      toggleActions: "play none none reverse"
    }
  })
})

// Clip-path reveal
gsap.to('.clip-reveal', {
  clipPath: "inset(0% 0% 0% 0%)",
  duration: 1.5,
  ease: "power2.inOut",
  scrollTrigger: {
    trigger: '.clip-reveal',
    start: "top 70%"
  }
})

// Scale reveal
gsap.from('.scale-reveal', {
  scale: 0.8,
  opacity: 0,
  duration: 1,
  ease: "power2.out",
  scrollTrigger: {
    trigger: '.scale-reveal',
    start: "top 80%"
  }
})
'''

    @classmethod
    def get_scroll_progress_template(cls) -> str:
        """Get scroll progress tracking template"""
        return '''
// Scroll Progress Tracking
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

// Progress bar
gsap.to('.progress-bar', {
  scaleX: 1,
  ease: "none",
  scrollTrigger: {
    trigger: document.body,
    start: "top top",
    end: "bottom bottom",
    scrub: 0.5
  }
})

// Section indicator
const sections = document.querySelectorAll('.section')

sections.forEach((section, index) => {
  ScrollTrigger.create({
    trigger: section,
    start: "top center",
    end: "bottom center",
    onEnter: () => updateIndicator(index),
    onEnterBack: () => updateIndicator(index)
  })
})

function updateIndicator(activeIndex) {
  document.querySelectorAll('.indicator-dot').forEach((dot, i) => {
    dot.classList.toggle('active', i === activeIndex)
  })
}

// ScrollTrigger for progress-based effects
gsap.to('.rotating-element', {
  rotation: 360,
  ease: "none",
  scrollTrigger: {
    trigger: '.rotation-section',
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
})

// Percentage counter
gsap.to('.counter', {
  innerText: 100,
  snap: { innerText: 1 },
  scrollTrigger: {
    trigger: '.counter-section',
    start: "top 80%",
    end: "bottom 20%",
    scrub: 1
  },
  onUpdate: function() {
    document.querySelector('.counter').textContent = Math.round(this.targets()[0].innerText) + '%'
  }
})
'''

    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main skill invocation"""
        context = context or {}
        task_lower = task.lower()
        
        result_type = "basic"
        if "parallax" in task_lower:
            result_type = "parallax"
        elif "pin" in task_lower or "pinned" in task_lower:
            result_type = "pinned"
        elif "horizontal" in task_lower:
            result_type = "horizontal"
        elif "reveal" in task_lower or "fade" in task_lower:
            result_type = "reveal"
        elif "progress" in task_lower or "track" in task_lower:
            result_type = "progress"
        
        templates = {
            "basic": cls.get_basic_scroll_template(),
            "parallax": cls.get_parallax_template(),
            "pinned": cls.get_pinned_section_template(),
            "horizontal": cls.get_horizontal_scroll_template(),
            "reveal": cls.get_reveal_effects_template(),
            "progress": cls.get_scroll_progress_template(),
        }
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "template": templates[result_type],
            "dependencies": ["gsap", "gsap/ScrollTrigger"],
            "tips": [
                "Use 'scrub: true' for smooth scroll-linked animation",
                "Use 'pin: true' to pin elements during scroll",
                "Use markers for debugging",
                "Use snap for carousel-like snapping",
                "Combine with Lenis for smooth scrolling"
            ]
        }


# Convenience function
def generate_gsap(task: str, **kwargs) -> Dict[str, Any]:
    return GSAPScrollSkill.invoke(task, kwargs)
