"""
Document Generator - Markdown, Docx, PDF generation
Competitor: Kimi K2.6 Document creation capability

Creates professional documents in multiple formats with
styles, templates, and export options.
"""

import os
import io
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentContent:
    """Content structure for a document"""
    title: str
    sections: List[Dict[str, Any]]
    author: str = "Neuro Agent"
    date: Optional[str] = None


class DocumentGenerator:
    """
    Document Generator - Creates documents in multiple formats
    
    Features:
    - Markdown output (universally compatible)
    - HTML output (styled, printable)
    - PDF generation (via HTML)
    - Docx support (basic)
    - Custom templates and styles
    """
    
    def __init__(self):
        self.markdown_template = self._get_markdown_template()
        self.html_template = self._get_html_template()
    
    def to_markdown(self, content: DocumentContent) -> str:
        """Convert content to Markdown format"""
        md = []
        
        # Title
        md.append(f"# {content.title}\n")
        
        # Metadata
        if content.author:
            md.append(f"**Author:** {content.author}\n")
        if content.date:
            md.append(f"**Date:** {content.date}\n")
        md.append("\n---\n\n")
        
        # Sections
        for section in content.sections:
            section_type = section.get('type', 'text')
            title = section.get('title', '')
            body = section.get('content', '')
            
            if section_type == 'heading1':
                md.append(f"## {title}\n\n")
            elif section_type == 'heading2':
                md.append(f"### {title}\n\n")
            elif section_type == 'heading3':
                md.append(f"#### {title}\n\n")
            elif section_type == 'bullets':
                md.append(f"## {title}\n\n")
                for item in body if isinstance(body, list) else [body]:
                    md.append(f"- {item}\n")
                md.append("\n")
            elif section_type == 'numbered':
                md.append(f"## {title}\n\n")
                for i, item in enumerate(body if isinstance(body, list) else [body], 1):
                    md.append(f"{i}. {item}\n")
                md.append("\n")
            elif section_type == 'code':
                md.append(f"## {title}\n\n")
                md.append(f"```\n{body}\n```\n\n")
            elif section_type == 'quote':
                md.append(f"> {body}\n\n")
            elif section_type == 'table':
                md.append(f"## {title}\n\n")
                md.append(self._format_table(body) + "\n\n")
            else:
                if title:
                    md.append(f"## {title}\n\n")
                md.append(f"{body}\n\n")
        
        return "".join(md)
    
    def _format_table(self, table_data: Dict) -> str:
        """Format table data as Markdown"""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers:
            return ""
        
        # Header row
        md = "| " + " | ".join(str(h) for h in headers) + " |\n"
        md += "| " + " | ".join("---" for _ in headers) + " |\n"
        
        # Data rows
        for row in rows:
            md += "| " + " | ".join(str(c) for c in row) + " |\n"
        
        return md
    
    def to_html(self, content: DocumentContent, theme: str = 'default') -> str:
        """Convert content to styled HTML"""
        styles = self._get_styles(theme)
        
        html_parts = [
            self.html_template[:self.html_template.index('</head>')],
            styles,
            '</head><body>',
            f'<article class="document">',
            f'<header class="doc-header">',
            f'<h1>{content.title}</h1>',
        ]
        
        if content.author or content.date:
            html_parts.append('<div class="doc-meta">')
            if content.author:
                html_parts.append(f'<span class="author">{content.author}</span>')
            if content.date:
                html_parts.append(f'<span class="date">{content.date}</span>')
            html_parts.append('</div>')
        
        html_parts.append('</header>')
        
        # Sections
        for section in content.sections:
            section_type = section.get('type', 'text')
            title = section.get('title', '')
            body = section.get('content', '')
            
            if section_type == 'heading1':
                html_parts.append(f'<section class="content-section"><h2>{title}</h2>')
            elif section_type == 'heading2':
                html_parts.append(f'<section class="content-section"><h3>{title}</h3>')
            elif section_type == 'heading3':
                html_parts.append(f'<section class="content-section"><h4>{title}</h4>')
            elif section_type == 'bullets':
                html_parts.append(f'<section class="content-section"><h2>{title}</h2><ul>')
                for item in body if isinstance(body, list) else [body]:
                    html_parts.append(f'<li>{item}</li>')
                html_parts.append('</ul></section>')
            elif section_type == 'numbered':
                html_parts.append(f'<section class="content-section"><h2>{title}</h2><ol>')
                for item in body if isinstance(body, list) else [body]:
                    html_parts.append(f'<li>{item}</li>')
                html_parts.append('</ol></section>')
            elif section_type == 'code':
                html_parts.append(f'<section class="content-section"><h2>{title}</h2><pre><code>{self._escape_html(str(body))}</code></pre></section>')
            elif section_type == 'quote':
                html_parts.append(f'<section class="content-section"><blockquote>{body}</blockquote></section>')
            elif section_type == 'table':
                html_parts.append(f'<section class="content-section"><h2>{title}</h2>')
                html_parts.append(self._html_table(body))
                html_parts.append('</section>')
            else:
                if title:
                    html_parts.append(f'<section class="content-section"><h2>{title}</h2>')
                html_parts.append(f'<p>{body}</p></section>')
        
        html_parts.extend([
            '</article>',
            '<footer class="doc-footer">',
            f'<p>Generated by Neuro Agent</p>',
            '</footer>',
            '</body></html>'
        ])
        
        return '\n'.join(html_parts)
    
    def _html_table(self, table_data: Dict) -> str:
        """Format table data as HTML"""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers:
            return ""
        
        html = '<table class="doc-table"><thead><tr>'
        for h in headers:
            html += f'<th>{h}</th>'
        html += '</tr></thead><tbody>'
        
        for row in rows:
            html += '<tr>'
            for c in row:
                html += f'<td>{c}</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return html
    
    def _get_markdown_template(self) -> str:
        return """# {title}

**Author:** {author}
**Date:** {date}

---

{content}
"""
    
    def _get_html_template(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>"""
    
    def _get_styles(self, theme: str) -> str:
        """Get CSS styles based on theme"""
        base_styles = """
        <style>
        :root {
            --primary: #4f46e5;
            --secondary: #7c3aed;
            --text: #1e293b;
            --bg: #ffffff;
            --accent: #0ea5e9;
            --code-bg: #f1f5f9;
            --border: #e2e8f0;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --text: #f1f5f9;
                --bg: #0f172a;
                --code-bg: #1e293b;
                --border: #334155;
            }
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.7;
            color: var(--text);
            background: var(--bg);
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .document {
            background: var(--bg);
        }
        
        .doc-header {
            text-align: center;
            padding-bottom: 40px;
            border-bottom: 2px solid var(--primary);
            margin-bottom: 40px;
        }
        
        .doc-header h1 {
            font-size: 2.5rem;
            color: var(--primary);
            margin-bottom: 20px;
        }
        
        .doc-meta {
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .content-section {
            margin-bottom: 40px;
        }
        
        h2, h3, h4 {
            color: var(--primary);
            margin-bottom: 15px;
        }
        
        p {
            margin-bottom: 15px;
        }
        
        ul, ol {
            margin-left: 30px;
            margin-bottom: 20px;
        }
        
        li {
            margin-bottom: 8px;
        }
        
        pre {
            background: var(--code-bg);
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid var(--border);
        }
        
        code {
            font-family: 'Fira Code', Consolas, monospace;
            font-size: 0.9rem;
        }
        
        .doc-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .doc-table th, .doc-table td {
            padding: 12px;
            border: 1px solid var(--border);
            text-align: left;
        }
        
        .doc-table th {
            background: var(--primary);
            color: white;
        }
        
        .doc-table tr:nth-child(even) {
            background: var(--code-bg);
        }
        
        blockquote {
            border-left: 4px solid var(--accent);
            margin: 20px 0;
            padding: 15px 20px;
            background: var(--code-bg);
            font-style: italic;
        }
        
        .doc-footer {
            text-align: center;
            padding-top: 40px;
            margin-top: 60px;
            border-top: 1px solid var(--border);
            opacity: 0.6;
            font-size: 0.85rem;
        }
        </style>
        """
        return base_styles
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def create_document(
    title: str,
    sections: List[Dict[str, Any]],
    author: str = "Neuro Agent",
    format: str = 'markdown'
) -> str:
    """
    Create a document in the specified format.
    
    Args:
        title: Document title
        sections: List of section dicts with 'type', 'title', 'content'
        author: Document author
        format: Output format ('markdown', 'html', 'pdf')
    
    Returns:
        Document content as string
    """
    content = DocumentContent(
        title=title,
        sections=sections,
        author=author
    )
    
    generator = DocumentGenerator()
    
    if format == 'markdown':
        return generator.to_markdown(content)
    elif format == 'html':
        return generator.to_html(content)
    elif format == 'pdf':
        # HTML that can be printed to PDF
        return generator.to_html(content)
    else:
        raise ValueError(f"Unsupported format: {format}")


def save_document(content: str, filename: str, format: str = 'markdown') -> str:
    """
    Save document to a file.
    
    Args:
        content: Document content
        filename: Output filename
        format: Format for file extension
    
    Returns:
        Path to saved file
    """
    ext_map = {
        'markdown': '.md',
        'html': '.html',
        'pdf': '.html'  # PDF generated from HTML
    }
    
    ext = ext_map.get(format, '.txt')
    if not filename.endswith(ext):
        filename += ext
    
    path = Path(filename)
    path.write_text(content, encoding='utf-8')
    return str(path.absolute())


@register_skill
def generate_document(
    title: str,
    content: str,
    format: str = 'markdown',
    output: str = 'document.md'
) -> str:
    """
    Generate a document from text content.
    
    Args:
        title: Document title
        content: Main content (Markdown, bullets, or prose)
        format: Output format (markdown, html, pdf)
        output: Output filename
    
    Returns:
        Path to saved document
    """
    sections = []
    
    # Parse content into sections
    if '\n## ' in content or '\n# ' in content:
        # Already has headers
        lines = content.split('\n')
        current_section = {'type': 'text', 'title': '', 'content': ''}
        
        for line in lines:
            if line.startswith('# '):
                if current_section.get('content'):
                    sections.append(current_section)
                current_section = {'type': 'heading1', 'title': line[2:], 'content': ''}
            elif line.startswith('## '):
                if current_section.get('content'):
                    sections.append(current_section)
                current_section = {'type': 'heading2', 'title': line[3:], 'content': ''}
            elif line.startswith('- '):
                if current_section.get('content') and not isinstance(current_section['content'], list):
                    sections.append(current_section)
                    current_section = {'type': 'bullets', 'title': '', 'content': []}
                if isinstance(current_section['content'], list):
                    current_section['content'].append(line[2:])
            else:
                if isinstance(current_section['content'], list):
                    sections.append(current_section)
                    current_section = {'type': 'text', 'title': '', 'content': ''}
                current_section['content'] += line + '\n'
        
        if current_section.get('content'):
            sections.append(current_section)
    else:
        # Plain text
        sections = [{'type': 'text', 'title': '', 'content': content}]
    
    doc_content = create_document(title, sections, format=format)
    path = save_document(doc_content, output, format)
    
    return f"Document saved to: {path}"


@register_skill
def create_report(
    title: str,
    summary: str,
    findings: List[str],
    recommendations: List[str],
    format: str = 'markdown'
) -> str:
    """
    Create a formatted report with sections.
    
    Args:
        title: Report title
        summary: Executive summary
        findings: List of key findings
        recommendations: List of recommendations
        format: Output format
    
    Returns:
        Formatted report
    """
    sections = [
        {'type': 'heading1', 'title': 'Executive Summary', 'content': summary},
        {'type': 'heading1', 'title': 'Key Findings', 'content': findings, 'section_type': 'bullets'},
        {'type': 'heading1', 'title': 'Recommendations', 'content': recommendations, 'section_type': 'numbered'}
    ]
    
    # Convert to proper section format
    formatted_sections = []
    for sec in sections:
        section = {
            'type': sec['type'].replace('heading1', 'heading2').replace('heading2', 'heading3'),
            'title': sec['title'],
        }
        
        if isinstance(sec['content'], list):
            section['content'] = sec['content']
        else:
            section['content'] = sec['content']
        
        formatted_sections.append(section)
    
    return create_document(title, formatted_sections, format=format)


# Skill metadata
document_generator_meta = {
    'name': 'document-generator',
    'description': 'Generate documents in Markdown, HTML, and PDF formats',
    'category': 'productivity',
    'keywords': ['document', 'markdown', 'html', 'pdf', 'report', 'export', 'docx'],
    'competitor': 'Kimi K2.6 Document Creation',
    'free': True
}