# ComfyUI WebUI Generator Node

A ComfyUI custom node that generates a shareable HTML UI from a **ComfyUI API workflow JSON**.

## Install
Clone into:
`ComfyUI/custom_nodes/ComfyUI-WebUI-Generator-Node`

Restart ComfyUI.

## Node
**Workflow → HTML (Generator)**

Input:
- `api_workflow_json_or_path`: paste API workflow JSON OR give a path to a `.json`
- `output_name`: used to name the generated file
- `open_in_browser`: auto-open the generated URL (best effort)
- `comfy_base_url` (optional): if your ComfyUI isn't on localhost

Output:
- `html_url`: served by ComfyUI under `/extensions/.../generated/...`
- `html_file_path`: local path

## IMPORTANT: Use API workflow JSON
In ComfyUI: export the workflow as **API** workflow JSON (not the normal workflow JSON).
