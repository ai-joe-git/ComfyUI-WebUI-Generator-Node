import os
import sys
import threading
import socket
import time
import subprocess
from typing import Optional

# ComfyUI server (aiohttp) hooks
from server import PromptServer


_LOCK = threading.Lock()
_THREAD: Optional[threading.Thread] = None

# You can change this if you want
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7860


def _is_port_open(host: str, port: int, timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def _pick_port(host: str, preferred: int) -> int:
    # If preferred is free, use it. Otherwise scan a small range.
    if not _is_port_open(host, preferred):
        return preferred
    for p in range(preferred + 1, preferred + 50):
        if not _is_port_open(host, p):
            return p
    return preferred


def _run_gradio_server(host: str, port: int):
    """
    Runs your existing workflow_to_html_generator.py Gradio app
    inside this ComfyUI process (thread).
    """
    try:
        # Import your file that you copied into this custom node folder
        import workflow_to_html_generator as gen

        iface = gen.create_interface()

        # queue() is fine; it's what you do in __main__
        try:
            iface.queue()
        except Exception:
            pass

        iface.launch(
            server_name=host,
            server_port=port,
            share=False,
            inbrowser=False,
            prevent_thread_lock=True,
        )
    except Exception as e:
        print(f"[WebUI-Generator-Node] Failed to start generator: {e}", file=sys.stderr)


def ensure_generator_running():
    """
    Starts the generator once (idempotent).
    """
    global _THREAD

    with _LOCK:
        if _THREAD and _THREAD.is_alive():
            return

        host = os.environ.get("COMFY_WEBUI_GEN_HOST", DEFAULT_HOST)
        preferred_port = int(os.environ.get("COMFY_WEBUI_GEN_PORT", str(DEFAULT_PORT)))
        port = _pick_port(host, preferred_port)

        os.environ["COMFY_WEBUI_GEN_EFFECTIVE_PORT"] = str(port)

        t = threading.Thread(
            target=_run_gradio_server,
            args=(host, port),
            daemon=True,
            name="ComfyUI-WebUI-Generator-Gradio",
        )
        t.start()
        _THREAD = t


def _open_path_in_explorer(path: str):
    """
    Cross-platform folder open.
    """
    path = os.path.abspath(path)

    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# -------------------------
# ComfyUI HTTP routes
# -------------------------

@PromptServer.instance.routes.get("/webui-generator/info")
async def webui_generator_info(request):
    ensure_generator_running()
    host = os.environ.get("COMFY_WEBUI_GEN_HOST", DEFAULT_HOST)
    port = os.environ.get("COMFY_WEBUI_GEN_EFFECTIVE_PORT", str(DEFAULT_PORT))
    return PromptServer.instance.json_response({
        "host": host,
        "port": int(port),
        "url": f"http://{host}:{port}"
    })


@PromptServer.instance.routes.post("/webui-generator/open-output")
async def webui_generator_open_output(request):
    """
    Opens ComfyUI's output dir (or a custom one if you want later).
    """
    try:
        comfy_root = os.path.dirname(os.path.abspath(sys.argv[0]))
        output_dir = os.path.join(comfy_root, "output")
        os.makedirs(output_dir, exist_ok=True)
        _open_path_in_explorer(output_dir)
        return PromptServer.instance.json_response({"ok": True, "path": output_dir})
    except Exception as e:
        return PromptServer.instance.json_response({"ok": False, "error": str(e)}, status=500)


# Start generator automatically when the custom node is imported (ComfyUI startup)
ensure_generator_running()
