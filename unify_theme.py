import os
import re

TEMPLATES_DIR = r"c:\Users\rushi\OneDrive\Desktop\traincare_connect\templates"
UNIFIED_CSS = "css/unified_theme.css"

def unify_templates():
    print(f"Scanning templates in: {TEMPLATES_DIR}")
    
    count = 0
    for filename in os.listdir(TEMPLATES_DIR):
        if not filename.endswith(".html"):
            continue
            
        file_path = os.path.join(TEMPLATES_DIR, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex to find CSS links
        # Looking for: <link rel="stylesheet" href="{{ url_for('static', filename='css/ANYTHING.css') }}">
        # But we want to preserve animations.css and external CDNs
        
        # First, let's find all local CSS links
        local_css_pattern = re.compile(r"""<link\s+rel=["']stylesheet["']\s+href=["']\{\{\s*url_for\s*\(\s*['"]static['"]\s*,\s*filename\s*=\s*['"]css/([^'"]+)['"]\s*\)\s*\}\}["']\s*>""")
        
        new_content = content
        
        def replace_css(match):
            css_file = match.group(1)
            # Skip animations.css, leafleat, etc.
            if css_file in ["animations.css", "leaflet.css", "unified_theme.css"]:
                return match.group(0)
            
            print(f"  [{filename}] Replacing {css_file} -> {UNIFIED_CSS}")
            return f'<link rel="stylesheet" href="{{{{ url_for(\'static\', filename=\'{UNIFIED_CSS}\') }}}}">'

        new_content = local_css_pattern.sub(replace_css, content)
        
        # Also remove inline styles in <body> or <html> that set background colors (common in the dark themes)
        # Identify dark theme backgrounds
        if 'background: var(--dark)' in new_content or 'background-color: #263238' in new_content:
             new_content = new_content.replace('background: var(--dark)', '')
             new_content = new_content.replace('background-color: #263238', '')
             print(f"  [{filename}] Removed inline dark background styles")

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1
            
    print(f"\nUpdated {count} templates.")

if __name__ == "__main__":
    unify_templates()
