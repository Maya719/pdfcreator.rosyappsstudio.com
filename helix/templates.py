import os
import json
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

templates = Jinja2Templates(directory="resources/views")

def vite(entrypoint: str) -> str:
    hot_file = os.path.join("public", "hot")
    if os.path.exists(hot_file):
        with open(hot_file, "r") as f:
            dev_url = f.read().strip()
        client_tag = f'<script type="module" src="{dev_url}/@vite/client"></script>'
        if entrypoint == "resources/js/app.js":
            return Markup(f'{client_tag}\n<script type="module" src="{dev_url}/{entrypoint}"></script>')
        elif entrypoint.endswith(".css"):
            return Markup(f'<link rel="stylesheet" href="{dev_url}/{entrypoint}" />')
        else:
            return Markup(f'<script type="module" src="{dev_url}/{entrypoint}"></script>')
    else:
        # Check standard Vite v5+ manifest path first
        manifest_path = os.path.join("public", "build", ".vite", "manifest.json")
        if not os.path.exists(manifest_path):
            manifest_path = os.path.join("public", "build", "manifest.json")
            
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            
            asset_info = manifest.get(entrypoint)
            if asset_info:
                file_path = asset_info.get("file")
                url = f"/build/{file_path}"
                if entrypoint.endswith(".css") or file_path.endswith(".css"):
                    return Markup(f'<link rel="stylesheet" href="{url}" />')
                
                tags = []
                css_imports = asset_info.get("css", [])
                for css_file in css_imports:
                    tags.append(f'<link rel="stylesheet" href="/build/{css_file}" />')
                tags.append(f'<script type="module" src="{url}"></script>')
                return Markup("\n".join(tags))
        
        # Fallback to local files if build doesn't exist
        fallback_name = entrypoint.split("/")[-1]
        return Markup(f'<link rel="stylesheet" href="/assets/{fallback_name}" />')

# Register global helper
templates.env.globals["vite"] = vite
