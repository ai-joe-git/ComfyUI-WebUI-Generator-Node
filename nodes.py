import json
import os
import re
import time
import webbrowser
import subprocess
import sys
from typing import Any, Dict, Tuple

from .workflow_to_html_generator import generate_html_from_api_workflow


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(THIS_DIR, "web")
GENERATED_DIR = os.path.join(WEB_DIR, "generated")


def _ensure_dirs() -> None:
    os.makedirs(GENERATED_DIR, exist_ok=True)


def _slugify(name: str) -> str:
    name = name.strip() or "workflow"
    name = re.sub(r"[^\w\-. ]+", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "-", name).strip("-")
    return name[:80] if len(name) > 80 else name


def _read_json_input(api_json_or_path: str) -> Dict[str, Any]:
    s = (api_json_or_path or "").strip()
    if not s:
        raise ValueError("Empty input. Provide API workflow JSON (string) or a path to a .json file.")

    # If it looks like a file path and exists, read it.
    if (len(s) < 4096) and (os.path.exists(s)) and os.path.isfile(s):
        with open(s, "r", encoding="utf-8") as f:
            s = f.read().strip()

    try:
        data = json.loads(s)
    except Exception as e:
        raise ValueError(f"Invalid JSON. Make sure you exported the *API workflow* JSON. JSON error: {e}")

    # Basic sanity check: API workflow usually has a dict of nodes by id.
    if not isinstance(data, dict):
        raise ValueError("API workflow JSON must be an object/dict at the top level.")
    return data


def _open_in_default_browser(url: str) -> None:
    try:
        webbrowser.open(url, new=2)
        return
    except Exception:
        pass

    # Fallbacks
    try:
        if sys.platform.startswith("win"):
            os.startfile(url)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", url])
        else:
            subprocess.Popen(["xdg-open", url])
    except Exception:
        # Non-fatal
        return


class WorkflowToHTMLNode:
    """
    ComfyUI node:
    - Takes API workflow JSON (pasted or file path)
    - Generates HTML into: custom_nodes/<this_repo>/web/generated/<name>__<timestamp>.html
    - Returns a URL that is served by ComfyUI under /extensions/<folder>/generated/...
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_workflow_json_or_path": ("STRING", {"multiline": True, "default": ""}),
                "output_name": ("STRING", {"default": "workflow-ui"}),
            },
            "optional": {
                # If ComfyUI is not on localhost or non-default port, user can override:
                "comfy_base_url": ("STRING", {"default": ""}),
                "open_in_browser": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("html_url", "html_file_path")
    FUNCTION = "run"
    CATEGORY = "web"

    def run(
        self,
        api_workflow_json_or_path: str,
        output_name: str,
        comfy_base_url: str = "",
        open_in_browser: bool = True,
    ) -> Tuple[str, str]:
        _ensure_dirs()

        api_wf = _read_json_input(api_workflow_json_or_path)

        ts = time.strftime("%Y%m%d-%H%M%S")
        base = _slugify(output_name)
        filename = f"{base}__{ts}.html"
        out_path = os.path.join(GENERATED_DIR, filename)

        # Generate HTML
        html = generate_html_from_api_workflow(api_wf)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)

        # Build same-origin URL served by ComfyUI:
        # /extensions/<folder_name>/generated/<file>
        folder_name = os.path.basename(THIS_DIR)
        rel_url = f"/extensions/{folder_name}/generated/{filename}"

        # If user provided base URL, use it, else keep relative.
        comfy_base_url = (comfy_base_url or "").strip()
        if comfy_base_url:
            comfy_base_url = comfy_base_url.rstrip("/")
            html_url = f"{comfy_base_url}{rel_url}"
        else:
            html_url = rel_url

        if open_in_browser:
            # Best-effort: if base url missing, try localhost default
            if html_url.startswith("/"):
                _open_in_default_browser(f"http://127.0.0.1:8188{html_url}")
            else:
                _open_in_default_browser(html_url)

        return (html_url, out_path)


NODE_CLASS_MAPPINGS = {
    "WorkflowToHTMLNode": WorkflowToHTMLNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkflowToHTMLNode": "Workflow → HTML (Generator)",
}
