from django import template
from django.utils.safestring import mark_safe
import markdown
import re

register = template.Library() 

@register.filter(name='markdown_with_latex')
def markdown_with_latex(value):
    """
    Convert markdown text to HTML with LaTeX support.
    
    This filter processes markdown content while preserving LaTeX expressions
    enclosed in $...$ (inline) or $$...$$ (block) delimiters.
    """
    if not value:
        return ""
    
    # Store LaTeX expressions temporarily
    latex_blocks = {}
    block_count = 0
    
    # Function to replace LaTeX with placeholders
    def save_latex(match):
        nonlocal block_count
        placeholder = f"LATEX_PLACEHOLDER_{block_count}"
        latex_blocks[placeholder] = match.group(0)
        block_count += 1
        return placeholder
    
    # Save display math: \[ ... \] and $$ ... $$
    pattern_display = r'(\\\[.*?\\\]|\$\$.*?\$\$)'
    value = re.sub(pattern_display, save_latex, value, flags=re.DOTALL)
    
    # Save inline math: \( ... \) and $ ... $
    # Be careful with single $ to avoid false positives
    pattern_inline = r'(\\\(.*?\\\)|\$[^\$\s][^\$]*?[^\$\s]?\$)'
    value = re.sub(pattern_inline, save_latex, value, flags=re.DOTALL)
    
    # Process markdown content
    html_content = markdown.markdown(
        value,
        extensions=[
            'tables',                # Support for tables
            'fenced_code',           # Support for ```code blocks
            'codehilite',            # Syntax highlighting
            'nl2br',                 # Convert newlines to <br>
            'sane_lists',            # Better list handling
            'def_list',              # Definition lists
            'attr_list',             # HTML attributes
            'smarty'                 # Smart quotes, dashes, etc.
        ]
    )
    
    # Restore LaTeX expressions
    for placeholder, latex in latex_blocks.items():
        html_content = html_content.replace(placeholder, latex)
    
    return mark_safe(html_content)
