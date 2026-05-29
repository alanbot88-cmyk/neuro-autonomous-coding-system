"""
Slide/Presentation Builder - HTML/CSS/JS based presentation generator
Competitor: Kimi K2.6 Slides generation capability

Creates professional presentations with animations, transitions,
and interactive elements using web technologies.
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SlideContent:
    """Content for a single slide"""
    title: str
    bullets: List[str] = field(default_factory=list)
    image_url: Optional[str] = None
    code_block: Optional[str] = None
    notes: str = ""
    transition: str = "fade"


@dataclass
class Presentation:
    """A complete presentation"""
    title: str
    subtitle: str = ""
    author: str = "Neuro Agent"
    slides: List[SlideContent] = field(default_factory=list)
    theme: str = "default"
    animations: bool = True


class SlideBuilder:
    """
    Slide/Presentation Builder - Creates web-based presentations
    
    Features:
    - HTML/CSS/JS output for universal compatibility
    - Multiple themes (dark, light, gradient)
    - Animations and transitions
    - Code syntax highlighting
    - Speaker notes support
    - Export to PDF (via browser print)
    """
    
    THEMES = {
        'default': {
            'primary': '#6366f1',
            'secondary': '#8b5cf6',
            'background': '#0f172a',
            'text': '#f1f5f9',
            'accent': '#22d3ee'
        },
        'light': {
            'primary': '#2563eb',
            'secondary': '#7c3aed',
            'background': '#ffffff',
            'text': '#1e293b',
            'accent': '#059669'
        },
        'gradient': {
            'primary': '#f97316',
            'secondary': '#ec4899',
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'text': '#ffffff',
            'accent': '#fbbf24'
        },
        'minimal': {
            'primary': '#374151',
            'secondary': '#6b7280',
            'background': '#f9fafb',
            'text': '#111827',
            'accent': '#3b82f6'
        },
        'cyber': {
            'primary': '#00ff88',
            'secondary': '#00d4ff',
            'background': '#0a0a0a',
            'text': '#e0e0e0',
            'accent': '#ff0055'
        }
    }
    
    def __init__(self, theme: str = 'default'):
        self.theme = theme
        self.colors = self.THEMES.get(theme, self.THEMES['default'])
    
    def create_presentation(
        self,
        title: str,
        subtitle: str = "",
        author: str = "Neuro Agent",
        slides: Optional[List[Dict]] = None
    ) -> str:
        """Generate a complete HTML presentation"""
        
        if slides is None:
            slides = []
        
        slides_html = self._generate_slides(slides)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{self._get_css()}
    </style>
</head>
<body>
    <div class="presentation">
        <div class="slides-container">
{slides_html}
        </div>
        
        <div class="controls">
            <button onclick="prevSlide()" class="btn">&#10094; Prev</button>
            <span class="slide-counter"><span id="current">1</span> / <span id="total">{len(slides) or 1}</span></span>
            <button onclick="nextSlide()" class="btn">Next &#10095;</button>
        </div>
        
        <div class="progress-bar">
            <div class="progress" id="progress"></div>
        </div>
    </div>
    
    <script>
{self._get_js()}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_slides(self, slides: List[Dict]) -> str:
        """Generate HTML for all slides"""
        html_parts = []
        
        for i, slide in enumerate(slides):
            title = slide.get('title', f'Slide {i + 1}')
            bullets = slide.get('bullets', [])
            image_url = slide.get('image')
            code = slide.get('code')
            notes = slide.get('notes', '')
            transition = slide.get('transition', 'fade')
            
            slide_html = f'''            <div class="slide {transition}" data-notes="{notes}">
                <div class="slide-content">
                    <h1 class="slide-title">{title}</h1>
'''
            if bullets:
                slide_html += '                    <ul class="slide-bullets">\n'
                for bullet in bullets:
                    slide_html += f'                        <li>{bullet}</li>\n'
                slide_html += '                    </ul>\n'
            
            if image_url:
                slide_html += f'                    <img src="{image_url}" alt="{title}" class="slide-image">\n'
            
            if code:
                slide_html += f'''                    <pre class="slide-code"><code>{self._escape_html(code)}</code></pre>
'''
            
            slide_html += '''                </div>
            </div>
'''
            html_parts.append(slide_html)
        
        return '\n'.join(html_parts)
    
    def _get_css(self) -> str:
        """Get CSS styles for the presentation"""
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: {self.colors['primary']};
            --secondary: {self.colors['secondary']};
            --bg: {self.colors['background']};
            --text: {self.colors['text']};
            --accent: {self.colors['accent']};
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            overflow: hidden;
            height: 100vh;
        }}
        
        .presentation {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        
        .slides-container {{
            width: 100%;
            height: calc(100% - 60px);
            overflow: hidden;
            position: relative;
        }}
        
        .slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: none;
            padding: 60px 80px;
            flex-direction: column;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.5s ease;
        }}
        
        .slide.active {{
            display: flex;
            opacity: 1;
        }}
        
        .slide.fade {{
            animation: fadeIn 0.5s ease;
        }}
        
        .slide.slideUp {{
            animation: slideUp 0.5s ease;
        }}
        
        .slide.slideRight {{
            animation: slideRight 0.5s ease;
        }}
        
        .slide.zoom {{
            animation: zoomIn 0.5s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideUp {{
            from {{ transform: translateY(50px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        
        @keyframes slideRight {{
            from {{ transform: translateX(-50px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        @keyframes zoomIn {{
            from {{ transform: scale(0.9); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
        
        .slide-content {{
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }}
        
        .slide-title {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 40px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titleFade 0.8s ease;
        }}
        
        @keyframes titleFade {{
            from {{ transform: translateY(-20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        
        .slide-bullets {{
            list-style: none;
            padding-left: 0;
        }}
        
        .slide-bullets li {{
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-left: 40px;
            position: relative;
            opacity: 0;
            animation: bulletFade 0.5s ease forwards;
        }}
        
        .slide-bullets li:nth-child(1) {{ animation-delay: 0.2s; }}
        .slide-bullets li:nth-child(2) {{ animation-delay: 0.4s; }}
        .slide-bullets li:nth-child(3) {{ animation-delay: 0.6s; }}
        .slide-bullets li:nth-child(4) {{ animation-delay: 0.8s; }}
        .slide-bullets li:nth-child(5) {{ animation-delay: 1.0s; }}
        
        @keyframes bulletFade {{
            from {{ transform: translateX(-20px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        .slide-bullets li::before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: var(--accent);
            font-weight: bold;
        }}
        
        .slide-image {{
            max-width: 80%;
            max-height: 50vh;
            margin: 30px auto;
            display: block;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .slide-code {{
            background: rgba(0,0,0,0.4);
            border-radius: 12px;
            padding: 30px;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 1.2rem;
            overflow-x: auto;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .controls {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
        }}
        
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(99, 102, 241, 0.4);
        }}
        
        .slide-counter {{
            font-size: 1.2rem;
            color: var(--text);
            opacity: 0.8;
        }}
        
        .progress-bar {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: rgba(255,255,255,0.1);
        }}
        
        .progress {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            transition: width 0.3s ease;
        }}
        
        /* Keyboard navigation hint */
        .presentation::after {{
            content: "← → Arrow keys to navigate";
            position: absolute;
            bottom: 70px;
            right: 20px;
            font-size: 0.8rem;
            opacity: 0.5;
        }}
"""
    
    def _get_js(self) -> str:
        """Get JavaScript for slide navigation"""
        return """
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const total = slides.length;
        
        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.remove('active');
                if (i === index) {
                    slide.classList.add('active');
                }
            });
            
            document.getElementById('current').textContent = index + 1;
            document.getElementById('progress').style.width = ((index + 1) / total * 100) + '%';
            
            // Announce for screen readers
            const activeSlide = slides[index];
            if (activeSlide) {
                const title = activeSlide.querySelector('.slide-title');
                if (title) {
                    document.title = title.textContent + ' - Presentation';
                }
            }
        }
        
        function nextSlide() {
            currentSlide = (currentSlide + 1) % total;
            showSlide(currentSlide);
        }
        
        function prevSlide() {
            currentSlide = (currentSlide - 1 + total) % total;
            showSlide(currentSlide);
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                nextSlide();
            } else if (e.key === 'ArrowLeft') {
                prevSlide();
            } else if (e.key === 'Home') {
                currentSlide = 0;
                showSlide(0);
            } else if (e.key === 'End') {
                currentSlide = total - 1;
                showSlide(currentSlide);
            }
        });
        
        // Touch support
        let touchStartX = 0;
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        });
        
        document.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) nextSlide();
                else prevSlide();
            }
        });
        
        // Show first slide
        showSlide(0);
        """
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def create_presentation_from_outline(
    title: str,
    outline: Dict[str, List[str]],
    theme: str = 'default'
) -> str:
    """
    Create a presentation from an outline structure.
    
    Args:
        title: Presentation title
        outline: Dict mapping slide titles to bullet points
        theme: Visual theme to use
    
    Returns:
        HTML presentation string
    """
    builder = SlideBuilder(theme)
    
    slides = []
    for slide_title, bullets in outline.items():
        slides.append({
            'title': slide_title,
            'bullets': bullets,
            'transition': 'fade'
        })
    
    return builder.create_presentation(
        title=title,
        slides=slides
    )


def save_presentation(html: str, filename: str = "presentation.html") -> str:
    """Save presentation to a file"""
    path = Path(filename)
    path.write_text(html, encoding='utf-8')
    return str(path.absolute())


# Skill functions
@register_skill
def create_slides(
    title: str,
    slides: List[Dict[str, Any]],
    theme: str = 'default',
    output_file: str = 'presentation.html'
) -> str:
    """
    Create a slide presentation.
    
    Args:
        title: Presentation title
        slides: List of slide dicts with 'title', 'bullets', 'code', 'image', 'notes'
        theme: Visual theme (default, light, gradient, minimal, cyber)
        output_file: Where to save the HTML file
    
    Returns:
        Path to saved presentation
    """
    builder = SlideBuilder(theme)
    html = builder.create_presentation(title, slides=slides)
    path = save_presentation(html, output_file)
    
    return f"Presentation saved to: {path}"


@register_skill
def create_from_outline(
    title: str,
    outline: str,
    theme: str = 'default'
) -> str:
    """
    Create presentation from text outline.
    
    Args:
        title: Presentation title
        outline: Text outline with # for titles and - for bullets
        theme: Visual theme
    
    Returns:
        HTML presentation string
    """
    builder = SlideBuilder(theme)
    
    # Parse outline
    slides = []
    current_title = "Introduction"
    current_bullets = []
    
    for line in outline.strip().split('\n'):
        line = line.strip()
        if line.startswith('# '):
            if current_bullets:
                slides.append({'title': current_title, 'bullets': current_bullets})
                current_bullets = []
            current_title = line[2:]
        elif line.startswith('- '):
            current_bullets.append(line[2:])
        elif line.startswith('  - '):
            current_bullets.append(line[4:])
    
    if current_bullets:
        slides.append({'title': current_title, 'bullets': current_bullets})
    
    html = builder.create_presentation(title, slides=slides)
    return html


@register_skill
def presentation_themes() -> Dict[str, Dict[str, str]]:
    """List available presentation themes"""
    return SlideBuilder.THEMES


# Skill metadata
slide_builder_meta = {
    'name': 'slide-builder',
    'description': 'Create HTML/CSS presentations with animations and themes',
    'category': 'productivity',
    'keywords': ['slides', 'presentation', 'powerpoint', 'html', 'export'],
    'competitor': 'Kimi K2.6 Slides Generation',
    'free': True
}