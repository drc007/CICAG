import os
import yaml

# --- SETTINGS ---
BOOK_TITLE = "CICAG python course"
AUTHOR = "CICAG"

GITHUB_REPO = "https://github.com/drc007/CICAG" 
IGNORE_DIRS = {'.ipynb_checkpoints', '_build', 'images', '.git', 'venv', 'jupyter-book','CICAG_course_slides'}
IGNORE_FILES = {'generate_myst.py', 'myst.yml', 'requirements.txt', 'README.md'}

def generate_myst():
    nav = []
    
    # Force index.md to be first if it exists
    if os.path.exists("index.md"):
        nav.append({"file": "index.md", "title": "Home"})

    # Scan for folders
    dirs = [d for d in os.listdir(".") if os.path.isdir(d) and d not in IGNORE_DIRS]
    dirs.sort()

    for folder in dirs:
        # Find notebooks/markdowns in subfolder
        files = [f for f in os.listdir(folder) if f.endswith(('.ipynb', '.md'))]
        if not files: continue
        
        files.sort()
        children = []
        for f in files:
            # FORCE forward slashes for MyST compatibility
            path = f"{folder}/{f}".replace("\\", "/")
            title = f.replace(".ipynb", "").replace(".md", "").replace("_", " ").title()
            children.append({"file": path, "title": title})
            
        nav.append({
            "title": folder.replace("_", " ").title(),
            "children": children
        })
    
    myst_config = {
        "version": 1,
        "project": {
            "title": BOOK_TITLE,
            "author": AUTHOR,
            "github": GITHUB_REPO,  
            "toc": nav
        },
        "site": {
            "template": "book-theme",
            "options": {
                "repository": GITHUB_REPO,
                "branch": "main"
            }
        }
    }

    with open("myst.yml", "w", encoding="utf-8") as f:
        yaml.dump(myst_config, f, sort_keys=False, default_flow_style=False)
    

if __name__ == "__main__":
    generate_myst()