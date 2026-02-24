"""
🚀 SMART ComfyUI Workflow to HTML Generator v2.0
Professional-grade HTML interface generator with modern UI/UX
"""

import gradio as gr
import json
import requests
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
import traceback

# Configure logging with UTF-8 encoding for Windows
import sys
import io

# Force UTF-8 output for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("generator.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class SmartWorkflowGenerator:
    """Enhanced workflow generator with professional features"""

    VERSION = "2.0.0"

    # Predefined dropdown options matching ComfyUI
    DROPDOWN_OPTIONS = {
        "megapixel": [
            "0.1",
            "0.15",
            "0.2",
            "0.25",
            "0.3",
            "0.35",
            "0.4",
            "0.45",
            "0.5",
            "0.55",
            "0.6",
            "0.65",
            "0.7",
            "0.75",
            "0.8",
            "0.85",
            "0.9",
            "0.95",
            "1.0",
            "1.1",
            "1.2",
            "1.3",
            "1.4",
            "1.5",
            "2.0",
            "2.5",
            "3.0",
            "4.0",
        ],
        "divisible_by": ["8", "16", "32", "64"],
        "aspect_ratio": [
            "1:1 (Perfect Square)",
            "2:3 (Classic Portrait)",
            "3:4 (Golden Ratio)",
            "3:5 (Elegant Vertical)",
            "4:5 (Artistic Frame)",
            "5:7 (Balanced Portrait)",
            "5:8 (Tall Portrait)",
            "7:9 (Modern Portrait)",
            "9:16 (Slim Vertical)",
            "9:19 (Tall Slim)",
            "9:21 (Ultra Tall)",
            "9:32 (Skyline)",
            "3:2 (Golden Landscape)",
            "4:3 (Classic Landscape)",
            "5:3 (Wide Horizon)",
            "5:4 (Balanced Frame)",
            "7:5 (Elegant Landscape)",
            "8:5 (Cinematic View)",
            "9:7 (Artful Horizon)",
            "16:9 (Panorama)",
            "19:9 (Cinematic Ultrawide)",
            "21:9 (Epic Ultrawide)",
            "32:9 (Super Ultrawide)",
        ],
        "sampler_name": [
            "euler",
            "euler_cfg_pp",
            "euler_ancestral",
            "euler_ancestral_cfg_pp",
            "heun",
            "heunpp2",
            "dpm_2",
            "dpm_2_ancestral",
            "lms",
            "dpm_fast",
            "dpm_adaptive",
            "dpmpp_2s_ancestral",
            "dpmpp_2s_ancestral_cfg_pp",
            "dpmpp_sde",
            "dpmpp_sde_gpu",
            "dpmpp_2m",
            "dpmpp_2m_cfg_pp",
            "dpmpp_2m_sde",
            "dpmpp_2m_sde_gpu",
            "dpmpp_3m_sde",
            "dpmpp_3m_sde_gpu",
            "ddpm",
            "lcm",
            "ipndm",
            "ipndm_v",
            "deis",
            "ddim",
            "uni_pc",
            "uni_pc_bh2",
            "res_momentumized",
            "res_multistep",
            "restart",
        ],
        "scheduler": [
            "normal",
            "karras",
            "exponential",
            "sgm_uniform",
            "simple",
            "ddim_uniform",
            "beta",
            "linear_quadratic",
            "lcm",
            "turbo",
            "align_your_steps",
            "gits",
        ],
        "type": [
            "flux",
            "flux2",
            "sd3",
            "sd15",
            "sd21",
            "sdxl",
            "stable_diffusion",
            "lumina2",
            "hunyuan_video",
            "auraflow",
            "ltxv",
        ],
        "device": ["default", "cpu", "cuda", "mps"],
        "format": [
            "video/h264-mp4",
            "video/h265-mp4",
            "video/av1-mp4",
            "video/vp9-webm",
            "image/gif",
            "image/webp",
        ],
        "upscale_method": ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],
        "keep_proportion": ["crop", "pad", "disabled"],
        "crop_position": ["center", "top", "bottom", "left", "right"],
        "pix_fmt": ["yuv420p", "yuv422p", "yuv444p"],
    }

    # Hardcoded upload fields for nodes that don't have proper API flags
    UPLOAD_FIELDS = {
        # Video Helper Suite nodes
        "VHS_LoadAudioUpload": {"audio": "audio"},
        "VHS_LoadVideo": {"video": "video"},
        "VHS_LoadVideoPath": {"video": "video"},
        "VHS_LoadImagePath": {"image": "image"},
        # Add more as needed
    }

    def __init__(self):
        self.workflow = None
        self.parameters = []
        self.nodes_by_category = {}
        self.node_defs = {}
        self.server_url = "http://127.0.0.1:8188"
        logger.info(f"🚀 Generator v{self.VERSION} initialized")

    def fetch_node_defs(self, server_url: str):
        """Fetch ALL node definitions from ComfyUI API"""
        try:
            logger.info(f"📡 Connecting to ComfyUI: {server_url}")
            response = requests.get(f"{server_url}/object_info", timeout=10)

            if response.status_code == 200:
                self.node_defs = response.json()
                logger.info(f"✅ Fetched {len(self.node_defs)} node types from API")

                # Debug: Save API response for inspection
                try:
                    with open("api_debug.json", "w", encoding="utf-8") as f:
                        json.dump(self.node_defs, f, indent=2, ensure_ascii=False)
                    logger.info("📝 Saved API response to api_debug.json")
                except Exception as e:
                    logger.warning(f"Could not save API debug: {e}")

                # Debug: Check for specific nodes
                if "TextEncodeAceStepAudio1.5" in self.node_defs:
                    node_info = self.node_defs["TextEncodeAceStepAudio1.5"]
                    logger.info(f"🔍 Found TextEncodeAceStepAudio1.5 in API")
                    logger.info(f"   Inputs: {list(node_info.get('input', {}).keys())}")
                else:
                    logger.warning(f"⚠️ TextEncodeAceStepAudio1.5 NOT found in API")

                return (
                    True,
                    f"✅ API Connected: {len(self.node_defs)} node types fetched",
                )

            logger.warning(f"⚠️ HTTP {response.status_code}")
            return False, f"⚠️ HTTP {response.status_code}"

        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Connection refused: {server_url}")
            return (
                False,
                f"❌ Could not connect to ComfyUI at {server_url}. Is ComfyUI running?",
            )
        except requests.exceptions.Timeout:
            logger.error(f"❌ Connection timeout: {server_url}")
            return False, f"❌ Connection timeout. ComfyUI is not responding."
        except Exception as e:
            logger.error(f"❌ API Error: {str(e)}")
            return False, f"❌ Error: {str(e)}"

    def get_dropdown_options_from_api(
        self, class_type: str, input_name: str
    ) -> Tuple[Optional[List], bool, Optional[str]]:
        """Extract dropdown options from ComfyUI API with enhanced parsing.
        Returns: (options_list, has_upload, upload_type)"""
        if class_type not in self.node_defs:
            logger.debug(f"🔍 Node {class_type} not found in API definitions")
            return None, False

        node_def = self.node_defs[class_type]

        # Debug: Log the node structure for specific nodes
        if "TextEncode" in class_type or "Audio" in class_type or "Ace" in class_type:
            logger.info(f"🔍 Checking {class_type}.{input_name}")
            if "input" in node_def:
                logger.info(f"   Input sections: {list(node_def['input'].keys())}")

        def extract_options(input_def, section_name):
            """Extract options from input definition with multiple format support.
            Returns: (options_list, has_upload, upload_type)"""
            if not isinstance(input_def, list):
                return None, False, None

            if len(input_def) == 0:
                return None, False, None

            _has_img_upload_tmp = False
            _has_aud_upload_tmp = False

            # Check for image_upload flag in metadata (second element)
            if len(input_def) > 1 and isinstance(input_def[1], dict):
                _has_img_upload_tmp = input_def[1].get("image_upload", False)
                _has_aud_upload_tmp = input_def[1].get("audio_upload", False)
            if _has_img_upload_tmp:
                logger.info(f"🖼️ {class_type}.{input_name} has image_upload support")
            if _has_aud_upload_tmp:
                logger.info(f"🔊 {class_type}.{input_name} has audio_upload support")

            # Format 1: COMBO widget - ["COMBO", {"options": [...]}]
            if (
                isinstance(input_def[0], str)
                and len(input_def) > 1
                and isinstance(input_def[1], dict)
                and "options" in input_def[1]
            ):
                options = input_def[1]["options"]
                if isinstance(options, list) and len(options) > 0:
                    logger.info(
                        f"📋 {class_type}.{input_name} ({section_name}): {len(options)} options [COMBO]"
                    )
                    has_upload = _has_img_upload_tmp or _has_aud_upload_tmp
                    upload_type = (
                        "audio"
                        if _has_aud_upload_tmp
                        else ("image" if _has_img_upload_tmp else None)
                    )
                    return options, has_upload, upload_type

            # Format 2: [["option1", "option2", ...], {}] - list of options in first element
            if isinstance(input_def[0], list) and len(input_def[0]) > 0:
                options = input_def[0]
                if all(isinstance(opt, str) for opt in options):
                    logger.info(
                        f"📋 {class_type}.{input_name} ({section_name}): {len(options)} options [list]"
                    )
                    has_upload = _has_img_upload_tmp or _has_aud_upload_tmp
                    upload_type = (
                        "audio"
                        if _has_aud_upload_tmp
                        else ("image" if _has_img_upload_tmp else None)
                    )
                    return options, has_upload, upload_type

            # Format 3: [{"options": [...]}, {}] - nested options dict in first element
            if isinstance(input_def[0], dict) and "options" in input_def[0]:
                options = input_def[0]["options"]
                if isinstance(options, list) and len(options) > 0:
                    logger.info(
                        f"📋 {class_type}.{input_name} ({section_name}): {len(options)} options [nested]"
                    )
                    has_upload = _has_img_upload_tmp or _has_aud_upload_tmp
                    upload_type = (
                        "audio"
                        if _has_aud_upload_tmp
                        else ("image" if _has_img_upload_tmp else None)
                    )
                    return options, has_upload, upload_type

            # Format 4: Direct list of strings ["option1", "option2"]
            if all(isinstance(opt, str) for opt in input_def):
                logger.info(
                    f"📋 {class_type}.{input_name} ({section_name}): {len(input_def)} options [direct]"
                )
                has_upload = _has_img_upload_tmp or _has_aud_upload_tmp
                upload_type = (
                    "audio"
                    if has_audio_upload
                    else ("image" if _has_img_upload_tmp else None)
                )
                return input_def, has_upload, upload_type

            has_upload = _has_img_upload_tmp or _has_aud_upload_tmp
            upload_type = (
                "audio"
                if _has_aud_upload_tmp
                else ("image" if _has_img_upload_tmp else None)
            )
            return None, has_upload, upload_type

        # Check required inputs
        if "input" in node_def:
            inputs = node_def["input"]

            if "required" in inputs and input_name in inputs["required"]:
                input_def = inputs["required"][input_name]
                options, has_upload, upload_type = extract_options(
                    input_def, "required"
                )
                if options or has_upload:
                    return options, has_upload, upload_type

            # Check optional inputs
            if "optional" in inputs and input_name in inputs["optional"]:
                input_def = inputs["optional"][input_name]
                options, has_upload, upload_type = extract_options(
                    input_def, "optional"
                )
                if options or has_upload:
                    return options, has_upload, upload_type

            # Check hidden inputs (some nodes put dropdowns here)
            if "hidden" in inputs and input_name in inputs["hidden"]:
                input_def = inputs["hidden"][input_name]
                options, has_upload, upload_type = extract_options(input_def, "hidden")
                if options or has_upload:
                    return options, has_upload, upload_type

        return None, False, None

    def get_input_description(self, class_type: str, input_name: str) -> str:
        """Get parameter description from API for tooltips"""
        if class_type not in self.node_defs:
            return ""

        node_def = self.node_defs[class_type]

        # Try to extract description if available
        if "input" in node_def:
            for section in ["required", "optional"]:
                if (
                    section in node_def["input"]
                    and input_name in node_def["input"][section]
                ):
                    input_def = node_def["input"][section][input_name]
                    if isinstance(input_def, list) and len(input_def) > 1:
                        if isinstance(input_def[1], dict) and "tooltip" in input_def[1]:
                            return input_def[1]["tooltip"]

        return ""

    def load_workflow(self, file, server_url="http://127.0.0.1:8188") -> Tuple:
        """Load and analyze workflow with full API integration"""
        try:
            logger.info("=" * 60)
            logger.info(
                f"📂 Loading workflow: {file.name if hasattr(file, 'name') else 'uploaded file'}"
            )
            logger.info(f"🌐 ComfyUI Server: {server_url}")
            logger.info("=" * 60)

            self.server_url = server_url

            # STEP 1: Fetch API definitions
            logger.info("STEP 1: Fetching ComfyUI API...")
            api_success, api_msg = self.fetch_node_defs(server_url)

            # STEP 2: Load workflow
            logger.info("STEP 2: Loading workflow JSON...")
            if hasattr(file, "name"):
                with open(file.name, "r", encoding="utf-8") as f:
                    self.workflow = json.load(f)
            else:
                if file is None:
                    return None, "❌ No file uploaded", []
                self.workflow = json.loads(
                    file.decode("utf-8") if isinstance(file, bytes) else file
                )

            logger.info(f"✅ Loaded workflow with {len(self.workflow)} nodes")

            # STEP 3: Extract parameters
            logger.info("STEP 3: Analyzing parameters...")
            self.parameters = []
            self.nodes_by_category = {}

            for node_id, node_data in self.workflow.items():
                class_type = node_data.get("class_type", "")
                inputs = node_data.get("inputs", {})
                title = node_data.get("_meta", {}).get("title", class_type)

                logger.debug(f"🔍 Node {node_id}: {class_type} ({title})")

                for input_name, input_value in inputs.items():
                    # Skip connections
                    if isinstance(input_value, list):
                        continue

                    # Get API options and description
                    api_options, has_upload, upload_type = (
                        self.get_dropdown_options_from_api(class_type, input_name)
                    )
                    description = self.get_input_description(class_type, input_name)

                    # Log for debugging specific nodes
                    if (
                        "TextEncode" in class_type
                        or "Audio" in class_type
                        or "language" in input_name.lower()
                        or has_upload
                    ):
                        logger.info(
                            f"🔍 Processing: {class_type}.{input_name} - Options: {api_options is not None} ({len(api_options) if api_options else 0} items), Upload: {has_upload} ({upload_type})"
                        )

                    # Fallback to hardcoded
                    if not api_options:
                        api_options = self.get_dropdown_options(input_name)

                    # Detect type - pass upload_type instead of has_image_upload
                    param_type, detected_upload_type = self.smart_detect_type(
                        input_name,
                        input_value,
                        class_type,
                        api_options,
                        has_upload,
                        upload_type,
                    )
                    category = self.categorize(class_type, input_name, title)

                    # Use detected upload type if available, otherwise keep API value
                    final_upload_type = (
                        detected_upload_type if detected_upload_type else upload_type
                    )

                    param = {
                        "node_id": node_id,
                        "node_title": title,
                        "node_class": class_type,
                        "input_name": input_name,
                        "value": input_value,
                        "type": param_type,
                        "options": api_options,
                        "category": category,
                        "description": description,
                        "has_upload": has_upload or (detected_upload_type is not None),
                        "upload_type": final_upload_type,
                    }

                    self.parameters.append(param)

                    if category not in self.nodes_by_category:
                        self.nodes_by_category[category] = set()
                    self.nodes_by_category[category].add(node_id)

            # Build checkbox options
            options = []
            for i, param in enumerate(self.parameters):
                opts_info = (
                    f" [{len(param['options'])} opts]" if param["options"] else ""
                )
                label = f"{param['category']} | {param['node_title']} → {param['input_name']} ({param['type']}{opts_info})"
                options.append((label, i))

            logger.info("=" * 60)
            logger.info(f"✅ COMPLETE: {len(self.parameters)} parameters extracted")
            logger.info(f"📂 {len(self.nodes_by_category)} categories detected")
            logger.info("=" * 60)

            info = api_msg + "\n"
            info += f"✅ Loaded {len(self.parameters)} parameters from {len(self.workflow)} nodes\n"
            info += f"📂 {len(self.nodes_by_category)} categories detected"

            return (
                gr.update(choices=options, value=list(range(len(options)))),
                info,
                list(range(len(options))),
            )

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return gr.update(choices=[], value=[]), error_msg, []

    def smart_detect_type(
        self,
        input_name: str,
        value,
        class_type: str,
        api_options: Optional[List],
        has_upload: bool = False,
        upload_type: Optional[str] = None,
    ):
        """Enhanced type detection with API priority - returns (param_type, upload_type)"""
        name_lower = input_name.lower()

        # Priority #0: Upload fields (image or audio) from API flags
        if has_upload:
            if upload_type == "audio":
                return "audio_upload", "audio"
            else:
                return "image_upload", "image"

        # Priority #0.5: Hardcoded upload fields for nodes without proper API flags
        if class_type in self.UPLOAD_FIELDS:
            if input_name in self.UPLOAD_FIELDS[class_type]:
                field_type = self.UPLOAD_FIELDS[class_type][input_name]
                return f"{field_type}_upload", field_type

        # Priority #1: API dropdown
        if api_options and len(api_options) > 0:
            return "dropdown", None

        # Check hardcoded dropdown
        if input_name in self.DROPDOWN_OPTIONS or name_lower in self.DROPDOWN_OPTIONS:
            return "dropdown", None

        # Type detection from value
        if isinstance(value, bool):
            return "toggle", None
        elif isinstance(value, int):
            if "seed" in name_lower and value > 1000:
                return "seed", None
            return "number", None
        elif isinstance(value, float):
            return ("slider_small" if value <= 2.0 else "slider"), None
        elif isinstance(value, str):
            try:
                float_val = float(value)
                return ("slider_small" if float_val <= 2.0 else "slider"), None
            except:
                pass

        if len(value) > 100 or "\n" in value:
            return "textarea", None

        if any(
            ext in value for ext in [".safetensors", ".ckpt", ".gguf", ".pth", ".pt"]
        ):
            return "file_selector", None

        if "/" in value or "\\" in value:
            return "path", None

        return "text", None

    def get_dropdown_options(self, input_name: str) -> Optional[List[str]]:
        """Fallback to hardcoded dropdown options"""
        if input_name in self.DROPDOWN_OPTIONS:
            return self.DROPDOWN_OPTIONS[input_name]

        name_lower = input_name.lower()
        if name_lower in self.DROPDOWN_OPTIONS:
            return self.DROPDOWN_OPTIONS[name_lower]

        for key in self.DROPDOWN_OPTIONS.keys():
            if key in name_lower:
                return self.DROPDOWN_OPTIONS[key]

        return None

    def categorize(self, class_type: str, input_name: str, title: str):
        """Smart categorization with emoji icons"""
        class_lower = class_type.lower()
        input_lower = input_name.lower()
        title_lower = title.lower()

        if any(w in class_lower for w in ["loader", "load"]):
            if (
                "model" in class_lower
                or "checkpoint" in class_lower
                or "gguf" in class_lower
            ):
                return "🤖 Models"
            if "vae" in class_lower:
                return "🎨 VAE"
            if "clip" in class_lower:
                return "📝 CLIP"
            if "lora" in class_lower:
                return "✨ LoRA"
            return "📂 Loaders"

        if any(
            w in class_lower for w in ["sampler", "ksampler", "sample", "scheduler"]
        ):
            return "⚙️ Sampling"

        if "resolution" in class_lower or "resolution" in title_lower:
            return "📐 Resolution"

        if any(w in class_lower for w in ["condition", "encode"]):
            if "text" in class_lower or "prompt" in input_lower:
                return "📝 Prompts"
            return "🎯 Conditioning"

        if "seed" in input_lower or "noise" in input_lower:
            return "🎲 Seeds"

        if any(w in input_lower for w in ["steps", "cfg", "denoise"]):
            return "⚡ Generation"

        if any(w in class_lower for w in ["image", "resize", "scale", "upscale"]):
            return "🖼️ Images"

        if any(w in class_lower for w in ["video", "frame", "fps"]):
            return "🎬 Video"

        if "batch" in class_lower or "batch" in title_lower:
            return f"📦 Batch"

        if any(w in class_lower for w in ["audio", "sound", "tts"]):
            return "🔊 Audio"

        if any(w in class_lower for w in ["save", "output", "preview", "combine"]):
            return "💾 Output"

        return f"🔧 {title}"

    def generate_html(
        self, selected_indices, app_name, server_url, output_path, enable_features
    ):
        """Generate enhanced HTML with modern features"""
        if not selected_indices:
            return "❌ Please select at least one parameter", None

        selected = [
            self.parameters[i] for i in selected_indices if i < len(self.parameters)
        ]

        # Group by category
        grouped = {}
        for param in selected:
            cat = param["category"]
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(param)

        # Parse enabled features
        features = {
            "dark_mode": "Dark Mode" in enable_features,
            "presets": "Preset System" in enable_features,
            "gallery": "Enhanced Gallery" in enable_features,
            "progress": "Progress Tracking" in enable_features,
            "tooltips": "Tooltips" in enable_features,
            "keyboard": "Keyboard Shortcuts" in enable_features,
            "autosave": "Auto-save Parameters" in enable_features,
            "batch": "Batch Generation" in enable_features,
        }

        html = self.build_enhanced_html(
            app_name, server_url, output_path, grouped, self.workflow, features
        )

        filename = f"{app_name.replace(' ', '_').replace('/', '_')}.html"
        filepath = Path(filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"✅ Generated: {filename} ({len(html)} bytes)")

        result = f"✅ Generated: {filename}\n"
        result += f"📊 Parameters: {len(selected)}\n"
        result += f"📂 Categories: {len(grouped)}\n"
        result += f"🎨 Features: {', '.join([k for k, v in features.items() if v])}\n"
        result += f"📦 Size: {len(html) // 1024}KB\n"
        result += f"📁 Location: {str(filepath.absolute())}"

        return result, str(filepath.absolute())

    def build_enhanced_html(
        self, app_name, server_url, output_path, grouped, workflow, features
    ):
        """Build modern, feature-rich HTML"""

        # Generate parameter inputs HTML
        inputs_html = ""
        param_map = []
        bypass_toggles = []

        for category, params in sorted(grouped.items()):
            cat_id = (
                category.replace(" ", "_")
                .replace(":", "_")
                .replace("🤖", "")
                .replace("📝", "")
                .replace("⚙️", "")
                .replace("🎨", "")
                .replace("✨", "")
                .replace("📂", "")
                .replace("📐", "")
                .replace("🎯", "")
                .replace("🎲", "")
                .replace("⚡", "")
                .replace("🖼️", "")
                .replace("🎬", "")
                .replace("📦", "")
                .replace("🔊", "")
                .replace("💾", "")
                .replace("🔧", "")
                .strip()
            )
            bypass_id = f"bypass_{cat_id}"

            cat_nodes = set(p["node_id"] for p in params)
            bypass_toggles.append({"id": bypass_id, "nodes": list(cat_nodes)})

            inputs_html += f'''
<div class="category-section" id="section_{cat_id}">
    <div class="category-header" onclick="toggleCategory('{cat_id}')">
        <h3>{category}</h3>
        <div class="category-controls">
            <label class="bypass-toggle" title="Bypass this entire category">
                <input type="checkbox" id="{bypass_id}" onchange="handleBypass('{bypass_id}')">
                <span>Bypass</span>
            </label>
            <span class="collapse-icon" id="collapse_{cat_id}">▼</span>
        </div>
    </div>
    <div class="category-content" id="content_{cat_id}">
'''

            for param in params:
                param_id = f"param_{param['node_id']}_{param['input_name']}"
                param_map.append(
                    {
                        "id": param_id,
                        "node_id": param["node_id"],
                        "input_name": param["input_name"],
                        "type": param["type"],
                        "has_upload": param.get("has_upload", False),
                        "upload_type": param.get("upload_type", None),
                    }
                )

                tooltip_html = ""
                if features["tooltips"] and param["description"]:
                    tooltip_html = f'<span class="info-icon" title="{param["description"]}">ℹ️</span>'

                label_html = f'<label for="{param_id}">{param["node_title"]} → {param["input_name"]}{tooltip_html}</label>'

                input_html = self.generate_input_html(param, param_id)

                inputs_html += f"""
        <div class="form-group">
            {label_html}
            {input_html}
        </div>
"""

            inputs_html += """
    </div>
</div>
"""

        # Build feature sections conditionally
        preset_section = ""
        if features["presets"]:
            preset_section = """
                    <div class="preset-section mb-3">
                        <label><i class="fas fa-save me-2"></i>Presets</label>
                        <div class="preset-controls">
                            <select id="presetSelect" onchange="loadPreset()">
                                <option value="">Select preset...</option>
                            </select>
                            <button onclick="savePreset()" title="Save current settings"><i class="fas fa-plus"></i></button>
                            <button onclick="deletePreset()" title="Delete selected preset"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
"""

        batch_section = ""
        if features["batch"]:
            batch_section = """
                    <div class="batch-section mb-3">
                        <label class="d-flex align-items-center">
                            <input type="checkbox" id="batchMode" onchange="toggleBatchMode()" class="me-2">
                            <i class="fas fa-layer-group me-2"></i>Batch Mode
                        </label>
                        <div class="batch-controls" id="batchControls">
                            <label>Number of generations:</label>
                            <input type="number" id="batchCount" value="3" min="1" max="20" class="form-control">
                            <label class="mt-2">
                                <input type="checkbox" id="batchRandomSeed" checked class="me-2">
                                Randomize seed each time
                            </label>
                        </div>
                    </div>
"""

        progress_section = ""
        if features["progress"]:
            progress_section = """
                    <div class="progress-container" id="progressContainer">
                        <div class="progress-bar-custom">
                            <div class="progress-bar-fill" id="progressBar">0%</div>
                        </div>
                        <p class="text-center mt-2 mb-0" id="progressText">Initializing...</p>
                    </div>
"""

        theme_toggle = ""
        if features["dark_mode"]:
            theme_toggle = '<button class="theme-toggle" onclick="toggleTheme()"><i class="fas fa-moon"></i> <span id="theme-text">Dark</span></button>'

        shortcuts_toggle = ""
        if features["keyboard"]:
            shortcuts_toggle = '<button class="theme-toggle" onclick="toggleShortcutsHelp()"><i class="fas fa-keyboard"></i> Shortcuts</button>'

        gallery_section = ""
        if features["gallery"]:
            gallery_section = """
                <div class="gallery">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h3 class="mb-0"><i class="fas fa-images me-2"></i>Gallery</h3>
                        <div>
                            <button onclick="clearGallery()" class="btn-sm btn-outline-danger" title="Clear gallery">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="gallery-grid" id="galleryGrid">
                        <div class="text-center text-muted">No images yet. Click Generate!</div>
                    </div>
                </div>
"""

        shortcuts_help = ""
        if features["keyboard"]:
            shortcuts_help = """
    <div class="shortcuts-help" id="shortcutsHelp">
        <h4>Keyboard Shortcuts</h4>
        <p><kbd>Ctrl</kbd> + <kbd>Enter</kbd> - Generate</p>
        <p><kbd>Ctrl</kbd> + <kbd>R</kbd> - Reset</p>
        <p><kbd>Ctrl</kbd> + <kbd>S</kbd> - Save Preset</p>
        <p><kbd>?</kbd> - Toggle this help</p>
    </div>
"""

        # Generate complete HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{app_name} - Professional ComfyUI Interface">
    <meta name="generator" content="ComfyUI HTML Generator v{self.VERSION}">
    <title>{app_name}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- GLightbox for image viewer -->
    <link href="https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/css/glightbox.min.css" rel="stylesheet">
    
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1f2937;
            --darker: #111827;
            --light: #f9fafb;
            --border: #e5e7eb;
            --shadow: rgba(0, 0, 0, 0.1);
            --shadow-lg: rgba(0, 0, 0, 0.2);
        }}
        
        [data-theme="dark"] {{
            --primary: #818cf8;
            --primary-dark: #6366f1;
            --secondary: #a78bfa;
            --success: #34d399;
            --danger: #f87171;
            --warning: #fbbf24;
            --dark: #f9fafb;
            --darker: #ffffff;
            --light: #111827;
            --border: #374151;
            --shadow: rgba(255, 255, 255, 0.1);
            --shadow-lg: rgba(255, 255, 255, 0.2);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--light);
            color: var(--dark);
            transition: background 0.3s, color 0.3s;
        }}
        
        [data-theme="dark"] body {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: var(--dark);
        }}
        
        /* Header */
        .app-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 1.5rem 0;
            box-shadow: 0 4px 6px var(--shadow-lg);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .app-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .header-controls {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}
        
        /* Theme toggle */
        .theme-toggle {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            color: white;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .theme-toggle:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }}
        
        /* Container */
        .main-container {{
            max-width: 1400px;
            margin: 1.5rem auto;
            padding: 0 1.5rem;
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 1.5rem;
        }}
        
        @media (max-width: 1024px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Category sections */
        .category-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px var(--shadow);
            margin-bottom: 1rem;
            overflow: hidden;
            transition: all 0.3s;
        }}
        
        [data-theme="dark"] .category-section {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .category-section:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px var(--shadow-lg);
        }}
        
        .category-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 1rem 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }}
        
        .category-header h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
        }}
        
        .category-controls {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}
        
        .bypass-toggle {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            cursor: pointer;
        }}
        
        .bypass-toggle input {{
            cursor: pointer;
        }}
        
        .collapse-icon {{
            transition: transform 0.3s;
            font-size: 1.2rem;
        }}
        
        .collapsed .collapse-icon {{
            transform: rotate(-90deg);
        }}
        
        .category-content {{
            padding: 1.25rem;
            max-height: 2000px;
            overflow: hidden;
            transition: max-height 0.3s ease-out, padding 0.3s;
        }}
        
        .category-content.collapsed {{
            max-height: 0;
            padding: 0 1.25rem;
        }}
        
        /* Form elements */
        .form-group {{
            margin-bottom: 1rem;
        }}
        
        .form-group label {{
            display: block;
            font-weight: 500;
            margin-bottom: 0.375rem;
            color: var(--dark);
            font-size: 0.9375rem;
        }}
        
        .form-group input[type="text"],
        .form-group input[type="number"],
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 0.625rem 0.75rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 0.9375rem;
            transition: all 0.3s;
            background: var(--light);
            color: var(--dark);
        }}
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}
        
        .form-group textarea {{
            min-height: 100px;
            resize: vertical;
            font-family: 'Monaco', 'Consolas', monospace;
        }}
        
        /* Range sliders */
        input[type="range"] {{
            min-height: 100px;
            resize: vertical;
            font-family: 'Monaco', 'Consolas', monospace;
        }}
        
        /* Range sliders */
        input[type="range"] {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: linear-gradient(to right, var(--primary) 0%, var(--primary) 50%, var(--border) 50%, var(--border) 100%);
            outline: none;
            transition: background 0.3s;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
            box-shadow: 0 2px 4px var(--shadow);
            transition: all 0.3s;
        }}
        
        input[type="range"]::-webkit-slider-thumb:hover {{
            background: var(--primary-dark);
            transform: scale(1.2);
        }}
        
        .slider-value {{
            display: inline-block;
            min-width: 60px;
            padding: 0.25rem 0.75rem;
            background: var(--primary);
            color: white;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            text-align: center;
            margin-left: 0.5rem;
        }}
        
        /* Toggle switches */
        .toggle-switch {{
            position: relative;
            display: inline-block;
            width: 60px;
            height: 30px;
        }}
        
        .toggle-switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}
        
        .slider-toggle {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: 0.4s;
            border-radius: 30px;
        }}
        
        .slider-toggle:before {{
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: 0.4s;
            border-radius: 50%;
        }}
        
        input:checked + .slider-toggle {{
            background-color: var(--primary);
        }}
        
        input:checked + .slider-toggle:before {{
            transform: translateX(30px);
        }}
        
        /* Buttons */
        .btn-primary {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 6px var(--shadow);
            width: 100%;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px var(--shadow-lg);
        }}
        
        .btn-primary:active {{
            transform: translateY(0);
        }}
        
        .btn-primary:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }}
        
        .btn-secondary {{
            background: white;
            color: var(--primary);
            border: 2px solid var(--primary);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            margin-top: 0.5rem;
        }}
        
        .btn-secondary:hover {{
            background: var(--primary);
            color: white;
        }}
        
        /* Sidebar */
        .sidebar {{
            position: sticky;
            top: 100px;
            height: fit-content;
        }}
        
        .control-panel {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px var(--shadow);
            margin-bottom: 1.5rem;
        }}
        
        [data-theme="dark"] .control-panel {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        /* Gallery */
        .gallery {{
            background: white;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 2px 8px var(--shadow);
        }}
        
        [data-theme="dark"] .gallery {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 0.75rem;
            margin-top: 1rem;
        }}
        
        .gallery-item {{
            position: relative;
            aspect-ratio: 1;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 4px var(--shadow);
        }}
        
        .gallery-item:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 8px var(--shadow-lg);
        }}
        
        .gallery-item img,
        .gallery-item video {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .gallery-item video.video-thumb.loading {{
            opacity: 0;
        }}

        .gallery-item video.video-thumb {{
            background: #1a1a2e;
        }}

        .gallery-item .video-overlay {{
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            color: rgba(255,255,255,0.85);
            text-shadow: 0 2px 8px rgba(0,0,0,0.6);
            pointer-events: none;
            opacity: 0.85;
            transition: opacity 0.2s;
        }}

        .gallery-item:hover .video-overlay {{
            opacity: 0.0;
        }}
        .gallery-item-info {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
            color: white;
            padding: 0.5rem;
            font-size: 0.8rem;
            transform: translateY(100%);
            transition: transform 0.3s;
        }}
        
        .gallery-item:hover .gallery-item-info {{
            transform: translateY(0);
        }}
        
        /* Progress bar */
        .progress-container {{
            margin: 1rem 0;
            display: none;
        }}
        
        .progress-container.active {{
            display: block;
        }}
        
        .progress-bar-custom {{
            width: 100%;
            height: 30px;
            background: var(--border);
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        /* Presets */
        .preset-controls {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .preset-controls select {{
            flex: 1;
            padding: 0.5rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            background: var(--light);
            color: var(--dark);
        }}
        
        .preset-controls button {{
            padding: 0.5rem 1rem;
            border: 2px solid var(--primary);
            border-radius: 8px;
            background: white;
            color: var(--primary);
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .preset-controls button:hover {{
            background: var(--primary);
            color: white;
        }}
        
        /* Info icon */
        .info-icon {{
            display: inline-block;
            width: 18px;
            height: 18px;
            line-height: 18px;
            text-align: center;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            font-size: 12px;
            cursor: help;
            margin-left: 0.5rem;
        }}
        
        /* Status messages */
        .status-message {{
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            display: none;
        }}
        
        .status-message.show {{
            display: block;
        }}
        
        .status-message.success {{
            background: rgba(16, 185, 129, 0.1);
            border: 2px solid var(--success);
            color: var(--success);
        }}
        
        .status-message.error {{
            background: rgba(239, 68, 68, 0.1);
            border: 2px solid var(--danger);
            color: var(--danger);
        }}
        
        .status-message.warning {{
            background: rgba(245, 158, 11, 0.1);
            border: 2px solid var(--warning);
            color: var(--warning);
        }}
        
        /* Batch mode */
        .batch-controls {{
            display: none;
            margin-top: 1rem;
            padding: 1rem;
            border: 2px dashed var(--border);
            border-radius: 8px;
        }}
        
        .batch-controls.active {{
            display: block;
        }}
        
        /* Keyboard shortcuts help */
        .shortcuts-help {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            display: none;
            z-index: 2000;
        }}
        
        .shortcuts-help.show {{
            display: block;
        }}
        
        .shortcuts-help h4 {{
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
        }}
        
        .shortcuts-help kbd {{
            background: #555;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: monospace;
        }}
        
        /* Loading spinner */
        .spinner {{
            border: 3px solid var(--border);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
            display: none;
        }}
        
        .spinner.active {{
            display: block;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .app-header h1 {{
                font-size: 1.5rem;
            }}
            
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            
            .sidebar {{
                position: static;
            }}
            
            .gallery-grid {{
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            }}
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease-out;
        }}
        
        .input-group {{
            display: flex;
            gap: 0.5rem;
        }}
        
        .input-group input {{
            flex: 1;
        }}
        
        .btn-sm {{
            padding: 0.25rem 0.5rem;
            font-size: 0.875rem;
        }}
        
        .btn-outline-danger {{
            border: 1px solid var(--danger);
            background: transparent;
            color: var(--danger);
            border-radius: 4px;
            cursor: pointer;
        }}
        
        .btn-outline-danger:hover {{
            background: var(--danger);
            color: white;
        }}
        
        .slider-container {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .slider-container input[type="range"] {{
            flex: 1;
        }}
        
        /* Image Upload Widget */
        .image-upload-widget {{
            width: 100%;
        }}
        
        .image-upload-widget .input-group {{
            display: flex;
            gap: 0.5rem;
            align-items: stretch;
        }}
        
        .image-upload-widget .btn-outline-primary {{
            background: transparent;
            border: 2px dashed var(--primary);
            color: var(--primary);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .image-upload-widget .btn-outline-primary:hover {{
            background: var(--primary);
            color: white;
            border-style: solid;
        }}
        
        .image-upload-widget select.form-control {{
            flex: 1;
            min-width: 150px;
        }}
        
        .image-preview-container {{
            background: var(--light);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        
        [data-theme="dark"] .image-preview-container {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .image-preview-container img, .image-preview-container audio {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px var(--shadow);
        }}
        
        .image-preview-container .btn-outline-danger {{
            background: transparent;
            border: 1px solid var(--danger);
            color: var(--danger);
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 0.5rem;
        }}
        
        .image-preview-container .btn-outline-danger:hover {{
            background: var(--danger);
            color: white;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="app-header">
        <div class="container-fluid">
            <div class="d-flex justify-content-between align-items-center">
                <h1><i class="fas fa-magic me-2"></i>{app_name}</h1>
                <div class="header-controls">
                    {theme_toggle}
                    {shortcuts_toggle}
                </div>
            </div>
        </div>
    </header>
    
    <!-- Main Content -->
    <div class="main-container">
        <div class="status-message" id="statusMessage"></div>
        
        <div class="content-grid">
            <!-- Left: Parameters -->
            <div class="parameters-section">
                {inputs_html}
            </div>
            
            <!-- Right: Controls & Gallery -->
            <div class="sidebar">
                <!-- Control Panel -->
                <div class="control-panel">
                    <h3 class="mb-3"><i class="fas fa-sliders-h me-2"></i>Controls</h3>
                    
                    {preset_section}
                    
                    {batch_section}
                    
                    <button class="btn-primary" onclick="generate()" id="generateBtn">
                        <i class="fas fa-play me-2"></i>Generate
                    </button>
                    
                    <button class="btn-secondary" onclick="resetParameters()">
                        <i class="fas fa-undo me-2"></i>Reset All
                    </button>
                    
                    {progress_section}
                    
                    <div class="spinner" id="loadingSpinner"></div>
                </div>
                
                <!-- Gallery -->
                {gallery_section}
            </div>
        </div>
    </div>
    
    <!-- Keyboard Shortcuts Help -->
    {shortcuts_help}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- GLightbox JS -->
    <script src="https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/js/glightbox.min.js"></script>
    
    <script>
        // Configuration
        const CONFIG = {{
            serverUrl: {json.dumps(server_url)},
            outputPath: {json.dumps(output_path)},
            features: {json.dumps(features)},
            pollInterval: 1000
        }};
        
        // Workflow template
        const workflowTemplate = {json.dumps(workflow, indent=4)};
        
        // Parameter mapping
        const paramMap = {json.dumps(param_map, indent=4)};
        
        // Bypass toggles
        const bypassToggles = {json.dumps(bypass_toggles, indent=4)};
        
        // State
        let currentPromptId = null;
        let pollTimer = null;
        let galleryItems = [];

        // Client/session identifiers (for WebSocket progress routing)
        const clientId = (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() : ('client_' + Math.random().toString(16).slice(2));
        let ws = null;
        let wsConnected = false;
        let lastProgressTs = 0;

        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🚀 {app_name} v{self.VERSION} initialized');
            
            // Load saved theme
            if (CONFIG.features.dark_mode) loadTheme();
            
            // Load autosaved parameters
            if (CONFIG.features.autosave) loadAutosave();
            
            // Load presets
            if (CONFIG.features.presets) loadPresetsList();
            
            // Setup keyboard shortcuts
            if (CONFIG.features.keyboard) setupKeyboardShortcuts();
            
            // Update slider displays
            updateAllSliders();
            
            // Setup GLightbox + gallery preload
            if (CONFIG.features.gallery) {{
                setupLightbox();
                loadExistingFiles(); // auto-load existing outputs on page load
            }}

            // Connect WebSocket for real-time progress updates
            if (CONFIG.features.progress) {{
                connectWebSocket();
            }}

            // Initialize any existing video thumbnails (if any)
            initAllVideoThumbnails();
        }});

        // --- Progress UI helpers ---
        function updateProgressUI(percent, text) {{
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            if (progressBar) {{
                const p = Math.max(0, Math.min(100, Math.round(percent)));
                progressBar.style.width = p + '%';
                progressBar.textContent = p + '%';
            }}
            if (progressText && typeof text === 'string') {{
                progressText.textContent = text;
            }}
            lastProgressTs = Date.now();
        }}

        function makeWsUrl(httpUrl) {{
            try {{
                const u = new URL(httpUrl);
                const proto = (u.protocol === 'https:') ? 'wss:' : 'ws:';
                return `${{proto}}//${{u.host}}/ws?clientId=${{encodeURIComponent(clientId)}}`;
            }} catch (e) {{
                // Fallback: naive replace
                const proto = httpUrl.startsWith('https') ? 'wss' : 'ws';
                return httpUrl.replace(/^https?/, proto) + `/ws?clientId=${{encodeURIComponent(clientId)}}`;
            }}
        }}

        // --- WebSocket progress (ComfyUI /ws) ---
        function connectWebSocket() {{
            if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

            const wsUrl = makeWsUrl(CONFIG.serverUrl);
            console.log('🔌 Connecting WebSocket:', wsUrl);

            try {{
                ws = new WebSocket(wsUrl);
            }} catch (e) {{
                console.warn('WebSocket init failed:', e);
                wsConnected = false;
                return;
            }}

            ws.onopen = () => {{
                wsConnected = true;
                console.log('✅ WebSocket connected');
            }};

            ws.onclose = () => {{
                wsConnected = false;
                console.warn('⚠️ WebSocket closed. Reconnecting soon...');
                setTimeout(connectWebSocket, 1500);
            }};

            ws.onerror = (err) => {{
                wsConnected = false;
                console.warn('WebSocket error:', err);
            }};

            ws.onmessage = (evt) => {{
                let msg;
                try {{ msg = JSON.parse(evt.data); }} catch {{ return; }}
                if (!msg || !msg.type) return;

                const data = msg.data || {{}};
                const pid = data.prompt_id || data.promptId || null;
                if (currentPromptId && pid && pid !== currentPromptId) return; // ignore other prompts

                if (msg.type === 'progress') {{
                    // {{ value, max }}
                    const v = Number(data.value);
                    const mx = Number(data.max);
                    if (isFinite(v) && isFinite(mx) && mx > 0) {{
                        const pct = (v / mx) * 100;
                        updateProgressUI(pct, `Generating... ${{Math.round(pct)}}%`);
                    }}
                }} else if (msg.type === 'executing') {{
                    // When node is null, execution finished for prompt
                    if (data.node === null && currentPromptId && (pid === currentPromptId || !pid)) {{
                        updateProgressUI(100, 'Finalizing...');
                    }}
                }} else if (msg.type === 'execution_start') {{
                    updateProgressUI(1, 'Starting...');
                }} else if (msg.type === 'execution_cached') {{
                    // Treat as progress bump
                    if (currentPromptId) updateProgressUI(5, 'Using cache...');
                }} else if (msg.type === 'execution_success') {{
                    updateProgressUI(100, 'Done');
                }} else if (msg.type === 'execution_error') {{
                    updateProgressUI(0, 'Error');
                }}
            }};
        }}

        // --- Auto-load existing outputs into gallery ---
        async function loadExistingFiles() {{
            const galleryGrid = document.getElementById('galleryGrid');
            if (!galleryGrid) return;

            
            // Remove placeholder message if present
            const placeholder = galleryGrid.querySelector('.text-muted');
            if (placeholder) galleryGrid.innerHTML = '';
try {{
                const resp = await fetch(`${{CONFIG.serverUrl}}/history`);
                if (!resp.ok) throw new Error(`history HTTP ${{resp.status}}`);
                const history = await resp.json();

                const promptIds = Object.keys(history || {{}});
                if (!promptIds.length) return;

                // Newest first (prompt ids are usually sortable as strings)
                promptIds.sort().reverse();

                const seen = new Set(galleryItems.map(x => (x.file && x.file.filename) ? x.file.filename : ''));
                let added = 0;

                for (const pid of promptIds.slice(0, 30)) {{
                    const promptData = history[pid];
                    if (!promptData || !promptData.outputs) continue;

                    const outputs = promptData.outputs || {{}};
                    for (const out of Object.values(outputs)) {{
                        if (out.images) {{
                            for (const img of out.images) {{
                                if (img && img.filename && !seen.has(img.filename)) {{
                                    addToGallery(img, 'image', false);
                                    seen.add(img.filename);
                                    added++;
                                }}
                            }}
                        }}
                        if (out.gifs) {{
                            for (const gif of out.gifs) {{
                                if (gif && gif.filename && !seen.has(gif.filename)) {{
                                    addToGallery(gif, 'gif', false);
                                    seen.add(gif.filename);
                                    added++;
                                }}
                            }}
                        }}
                        if (out.videos) {{
                            for (const vid of out.videos) {{
                                if (vid && vid.filename && !seen.has(vid.filename)) {{
                                    addToGallery(vid, 'video', false);
                                    seen.add(vid.filename);
                                    added++;
                                }}
                            }}
                        }}
                        if (out.audio) {{
                            for (const aud of out.audio) {{
                                if (aud && aud.filename && !seen.has(aud.filename)) {{
                                    addToGallery(aud, 'audio', false);
                                    seen.add(aud.filename);
                                    added++;
                                }}
                            }}
                        }}
                    }}
                    if (added >= 50) break;
                }}

                if (added > 0) {{
                    // Clear placeholder text if present
                    if (galleryGrid.querySelector('.text-muted')) {{
                        galleryGrid.innerHTML = '';
                        // Re-render from galleryItems (they were appended while placeholder existed)
                        // Easiest: just reload page order: remove placeholder already, so items should show.
                    }}
                    setupLightbox();
                    initAllVideoThumbnails();
                }}
            }} catch (e) {{
                console.warn('Failed to load existing files:', e);
            }}
        }}

        // --- Video thumbnail handling ---
        function initAllVideoThumbnails() {{
            document.querySelectorAll('video.video-thumb').forEach(v => initVideoThumbnail(v));
        }}

        function initVideoThumbnail(video) {{
            if (!video || video.dataset.thumbInit === '1') return;
            video.dataset.thumbInit = '1';

            // Best-effort first-frame thumbnail (works even when HTML is opened via file://)
            video.muted = true;
            video.playsInline = true;
            video.preload = 'auto';
            video.classList.add('video-thumb');
            video.classList.add('loading');

            let hasError = false;
            let thumbTime = 0.1;

            const computeThumbTime = () => {{
                const d = Number(video.duration);
                if (!isFinite(d) || d <= 0) return 0.1;
                // 0.1s or ~1% into the clip; keep inside [0, d-0.05]
                const t = Math.max(0.1, d * 0.01);
                return Math.min(t, Math.max(0, d - 0.05));
            }};

            const applyThumbTime = (t) => {{
                try {{
                    video.dataset.thumbTime = String(t);
                    thumbTime = t;
                    // Seeking needs the media pipeline ready
                    video.currentTime = t;
                }} catch (e) {{}}
            }};

            const showVideo = () => {{
                video.classList.remove('loading');
            }};

            // Handle video loading error - show video anyway with play button overlay
            video.addEventListener('error', () => {{
                hasError = true;
                showVideo();
                console.warn('Video thumbnail error for:', video.src);
            }}, {{ once: true }});

            // When metadata is loaded (duration available)
            video.addEventListener('loadedmetadata', () => {{
                const t = computeThumbTime();
                applyThumbTime(t);
            }}, {{ once: true }});

            // When enough data is loaded to render the current frame
            video.addEventListener('loadeddata', () => {{
                if (!hasError) {{
                    const t = computeThumbTime();
                    applyThumbTime(t);
                }}
            }}, {{ once: true }});

            // After seeking, pause on that frame as the thumbnail
            video.addEventListener('seeked', () => {{
                video.pause();
                showVideo();
            }});

            // Fallback: if video takes too long, show it anyway
            setTimeout(() => {{
                if (video.classList.contains('loading')) {{
                    showVideo();
                    // If video is still not showing (possibly due to CORS), trigger error display
                    if (video.videoWidth === 0 && video.readyState < 2) {{
                        hasError = true;
                        const fallback = video.nextElementSibling;
                        if (fallback && fallback.classList.contains('video-fallback')) {{
                            fallback.style.display = 'flex';
                            video.style.display = 'none';
                        }}
                    }}
                }}
            }}, 5000);

            // Trigger load in case the element was added dynamically
            try {{ video.load(); }} catch {{}}

            // Hover-to-play with restore thumbnail on leave
            const parent = video.closest('.gallery-item') || video;

            parent.addEventListener('mouseenter', () => {{
                if (!hasError) {{
                    video.play().catch(() => {{}});
                }}
            }});

            parent.addEventListener('mouseleave', () => {{
                video.pause();
                if (!hasError) {{
                    try {{ video.currentTime = thumbTime; }} catch {{}}
                }}
            }});
        }}
// Theme toggle
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            const themeText = document.getElementById('theme-text');
            if (themeText) themeText.textContent = newTheme === 'dark' ? 'Light' : 'Dark';
        }}
        
        function loadTheme() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            const themeText = document.getElementById('theme-text');
            if (themeText) themeText.textContent = savedTheme === 'dark' ? 'Light' : 'Dark';
        }}
        
        // Category collapse
        function toggleCategory(categoryId) {{
            const content = document.getElementById('content_' + categoryId);
            const icon = document.getElementById('collapse_' + categoryId);
            const section = document.getElementById('section_' + categoryId);
            
            if (content.classList.contains('collapsed')) {{
                content.classList.remove('collapsed');
                section.classList.remove('collapsed');
            }} else {{
                content.classList.add('collapsed');
                section.classList.add('collapsed');
            }}
        }}
        
        // Bypass handling
        function handleBypass(bypassId) {{
            const checkbox = document.getElementById(bypassId);
            const toggle = bypassToggles.find(t => t.id === bypassId);
            
            if (toggle) {{
                console.log(`${{checkbox.checked ? 'Bypassing' : 'Enabling'}} nodes:`, toggle.nodes);
            }}
        }}
        
        // Slider updates
        function updateSlider(sliderId) {{
            const slider = document.getElementById(sliderId);
            const display = document.getElementById(sliderId + '_value');
            if (slider && display) {{
                display.textContent = slider.value;
                
                // Update slider background gradient
                const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
                slider.style.background = `linear-gradient(to right, var(--primary) 0%, var(--primary) ${{value}}%, var(--border) ${{value}}%, var(--border) 100%)`;
                
                if (CONFIG.features.autosave) autosaveParameters();
            }}
        }}
        
        function updateAllSliders() {{
            document.querySelectorAll('input[type="range"]').forEach(slider => {{
                const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
                slider.style.background = `linear-gradient(to right, var(--primary) 0%, var(--primary) ${{value}}%, var(--border) ${{value}}%, var(--border) 100%)`;
            }});
        }}
        
        // Image upload handling - Actually uploads file to ComfyUI
            async function handleUpload(paramId, fileInput, uploadType = 'image') {{
                const file = fileInput.files[0];
                if (!file) return;

                const previewContainer = document.getElementById(paramId + '_preview');
                const previewImg = document.getElementById(paramId + '_preview_img');
                const previewAudio = document.getElementById(paramId + '_preview_audio');
                const hiddenInput = document.getElementById(paramId + '_uploaded');
                const select = document.getElementById(paramId);

                // Create object URL for preview
                const objectUrl = URL.createObjectURL(file);
                
                // Handle preview based on type
                if (uploadType === 'audio' && previewAudio) {{
                    previewAudio.src = objectUrl;
                }} else if (previewImg) {{
                    previewImg.src = objectUrl;
                }}
                previewContainer.style.display = 'block';

                const typeLabel = uploadType === 'audio' ? 'Audio' : 'Image';
                showStatus(`Uploading "${{file.name}}" to ComfyUI...`, 'success');

                try {{
                    // Upload file to ComfyUI
                    const formData = new FormData();
                    formData.append('image', file);
                    formData.append('type', 'input');
                    formData.append('overwrite', 'true');

                    const uploadResponse = await fetch(`${{CONFIG.serverUrl}}/upload/image`, {{
                        method: 'POST',
                        body: formData
                    }});

                    if (!uploadResponse.ok) {{
                        const errorText = await uploadResponse.text();
                        throw new Error(`Upload failed: ${{uploadResponse.status}} - ${{errorText}}`);
                    }}

                    const uploadResult = await uploadResponse.json();
                    console.log(`✅ ${{typeLabel}} uploaded successfully:`, uploadResult);

                    // Store the uploaded filename (ComfyUI may rename it)
                    const uploadedFilename = uploadResult.name || file.name;
                    hiddenInput.value = uploadedFilename;
                    hiddenInput.dataset.fileData = objectUrl;
                    hiddenInput.dataset.uploaded = 'true';

                    // Update the select dropdown to show the uploaded file
                    if (select) {{
                        // Check if option already exists
                        let option = select.querySelector(`option[value="${{uploadedFilename}}"]`);
                        if (!option) {{
                            // Add new option
                            option = document.createElement('option');
                            option.value = uploadedFilename;
                            option.textContent = uploadedFilename;
                            select.appendChild(option);
                        }}
                        // Select the uploaded file
                        select.value = uploadedFilename;
                    }}

                    showStatus(`${{typeLabel}} "${{uploadedFilename}}" uploaded successfully!`, 'success');
                    if (CONFIG.features.autosave) autosaveParameters();

                }} catch (error) {{
                    console.error(`❌ ${{typeLabel}} upload failed:`, error);
                    showStatus(`Upload failed: ${{error.message}}`, 'error');
                    // Still keep the preview but mark as not uploaded
                    hiddenInput.value = file.name;
                    hiddenInput.dataset.fileData = objectUrl;
                    hiddenInput.dataset.uploaded = 'false';
                    // Still update select to show the filename
                    if (select) {{
                        select.value = file.name;
                    }}
                }}
            }}

            function handleSelect(paramId, value, uploadType = 'image') {{
                if (!value) return;

                const previewContainer = document.getElementById(paramId + '_preview');
                const hiddenInput = document.getElementById(paramId + '_uploaded');

                // Hide preview and clear uploaded file
                previewContainer.style.display = 'none';
                hiddenInput.value = '';
                delete hiddenInput.dataset.fileData;

                const typeLabel = uploadType === 'audio' ? 'Audio' : 'Image';
                showStatus(`${{typeLabel}} "${{value}}" selected from history`, 'success');
            }}

            function clearUpload(paramId, uploadType = 'image') {{
                const fileInput = document.getElementById(paramId + '_file');
                const previewContainer = document.getElementById(paramId + '_preview');
                const previewImg = document.getElementById(paramId + '_preview_img');
                const previewAudio = document.getElementById(paramId + '_preview_audio');
                const hiddenInput = document.getElementById(paramId + '_uploaded');
                const select = document.getElementById(paramId);

                // Clear file input
                fileInput.value = '';

                // Hide preview
                previewContainer.style.display = 'none';
                if (previewImg) previewImg.src = '';
                if (previewAudio) previewAudio.src = '';

                // Clear hidden input and upload status
                hiddenInput.value = '';
                delete hiddenInput.dataset.fileData;
                delete hiddenInput.dataset.uploaded;

                // Reset select to empty
                if (select) {{
                    select.value = '';
                }}

                const typeLabel = uploadType === 'audio' ? 'Audio' : 'Image';
                showStatus(`${{typeLabel}} upload cleared`, 'info');
                if (CONFIG.features.autosave) autosaveParameters();
            }}
        
        // Parameter autosave
        function autosaveParameters() {{
            if (!CONFIG.features.autosave) return;
            
            const params = {{}};
            paramMap.forEach(param => {{
                if (param.has_upload) {{
                    // For upload fields (image or audio), save both select value and uploaded file
                    const selectElement = document.getElementById(param.id);
                    const uploadedInput = document.getElementById(param.id + '_uploaded');
                    params[param.id] = {{
                        selectValue: selectElement ? selectElement.value : '',
                        uploadedFile: uploadedInput ? uploadedInput.value : '',
                        uploadType: param.upload_type || 'image',
                        isUpload: true
                    }};
                }} else {{
                    const element = document.getElementById(param.id);
                    if (element) {{
                        params[param.id] = element.type === 'checkbox' ? element.checked : element.value;
                    }}
                }}
            }});
            
            localStorage.setItem('autosave_params', JSON.stringify(params));
        }}
        
        function loadAutosave() {{
            const saved = localStorage.getItem('autosave_params');
            if (!saved) return;
            
            try {{
                const params = JSON.parse(saved);
                Object.keys(params).forEach(id => {{
                    const value = params[id];
                    
                    // Check if this is an upload field (object with isUpload flag)
                    if (value && typeof value === 'object' && value.isUpload) {{
                        const selectElement = document.getElementById(id);
                        const uploadedInput = document.getElementById(id + '_uploaded');
                        const uploadType = value.uploadType || 'image';
                        
                        if (selectElement && value.selectValue) {{
                            selectElement.value = value.selectValue;
                        }}
                        if (uploadedInput && value.uploadedFile) {{
                            uploadedInput.value = value.uploadedFile;
                            // Note: Cannot restore file object from localStorage, only filename
                        }}
                    }} else {{
                        // Standard parameter handling
                        const element = document.getElementById(id);
                        if (element) {{
                            if (element.type === 'checkbox') {{
                                element.checked = value;
                            }} else {{
                                element.value = value;
                                if (element.type === 'range') {{
                                    updateSlider(id);
                                }}
                            }}
                        }}
                    }}
                }});
                console.log('✅ Loaded autosaved parameters');
            }} catch (e) {{
                console.error('Failed to load autosave:', e);
            }}
        }}
        
        // Reset parameters
        function resetParameters() {{
            if (!confirm('Reset all parameters to default values?')) return;
            
            paramMap.forEach(param => {{
                if (param.has_upload) {{
                    // Reset upload fields (image or audio)
                    const selectElement = document.getElementById(param.id);
                    const uploadedInput = document.getElementById(param.id + '_uploaded');
                    const fileInput = document.getElementById(param.id + '_file');
                    const previewContainer = document.getElementById(param.id + '_preview');
                    
                    if (selectElement && selectElement.dataset.default) {{
                        selectElement.value = selectElement.dataset.default;
                    }}
                    if (uploadedInput) {{
                        uploadedInput.value = '';
                        delete uploadedInput.dataset.fileData;
                    }}
                    if (fileInput) {{
                        fileInput.value = '';
                    }}
                    if (previewContainer) {{
                        previewContainer.style.display = 'none';
                    }}
                }} else {{
                    // Standard parameter handling
                    const element = document.getElementById(param.id);
                    if (element && element.dataset.default) {{
                        if (element.type === 'checkbox') {{
                            element.checked = element.dataset.default === 'true';
                        }} else {{
                            element.value = element.dataset.default;
                            if (element.type === 'range') {{
                                updateSlider(param.id);
                            }}
                        }}
                    }}
                }}
            }});
            
            if (CONFIG.features.autosave) autosaveParameters();
            showStatus('Parameters reset to defaults', 'success');
        }}
        
        // Preset system
        function savePreset() {{
            const name = prompt('Enter preset name:');
            if (!name) return;
            
            const params = {{}};
            paramMap.forEach(param => {{
                if (param.has_upload) {{
                    // For upload fields (image or audio), save select value only (not uploaded files)
                    const selectElement = document.getElementById(param.id);
                    params[param.id] = {{
                        selectValue: selectElement ? selectElement.value : '',
                        uploadType: param.upload_type || 'image',
                        isUpload: true
                    }};
                }} else {{
                    const element = document.getElementById(param.id);
                    if (element) {{
                        params[param.id] = element.type === 'checkbox' ? element.checked : element.value;
                    }}
                }}
            }});
            
            const presets = JSON.parse(localStorage.getItem('presets') || '{{}}');
            presets[name] = params;
            localStorage.setItem('presets', JSON.stringify(presets));
            
            loadPresetsList();
            showStatus(`Preset "${{name}}" saved!`, 'success');
        }}
        
        function loadPreset() {{
            const select = document.getElementById('presetSelect');
            const name = select.value;
            if (!name) return;
            
            const presets = JSON.parse(localStorage.getItem('presets') || '{{}}');
            const params = presets[name];
            
            if (params) {{
                Object.keys(params).forEach(id => {{
                    const value = params[id];
                    
                    // Check if this is an upload field
                    if (value && typeof value === 'object' && value.isUpload) {{
                        const selectElement = document.getElementById(id);
                        if (selectElement && value.selectValue) {{
                            selectElement.value = value.selectValue;
                        }}
                    }} else {{
                        // Standard parameter handling
                        const element = document.getElementById(id);
                        if (element) {{
                            if (element.type === 'checkbox') {{
                                element.checked = value;
                            }} else {{
                                element.value = value;
                                if (element.type === 'range') {{
                                    updateSlider(id);
                                }}
                            }}
                        }}
                    }}
                }});
                showStatus(`Preset "${{name}}" loaded!`, 'success');
            }}
        }}
        
        function deletePreset() {{
            const select = document.getElementById('presetSelect');
            const name = select.value;
            if (!name) return;
            
            if (!confirm(`Delete preset "${{name}}"?`)) return;
            
            const presets = JSON.parse(localStorage.getItem('presets') || '{{}}');
            delete presets[name];
            localStorage.setItem('presets', JSON.stringify(presets));
            
            loadPresetsList();
            showStatus(`Preset "${{name}}" deleted`, 'success');
        }}
        
        function loadPresetsList() {{
            const select = document.getElementById('presetSelect');
            if (!select) return;
            
            const presets = JSON.parse(localStorage.getItem('presets') || '{{}}');
            select.innerHTML = '<option value="">Select preset...</option>';
            
            Object.keys(presets).forEach(name => {{
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
            }});
        }}
        
        // Batch mode
        function toggleBatchMode() {{
            const checkbox = document.getElementById('batchMode');
            const controls = document.getElementById('batchControls');
            if (checkbox.checked) {{
                controls.classList.add('active');
            }} else {{
                controls.classList.remove('active');
            }}
        }}
        
        // Generate
        async function generate() {{
            const btn = document.getElementById('generateBtn');
            const spinner = document.getElementById('loadingSpinner');
            const progressContainer = document.getElementById('progressContainer');
            
            // Check batch mode
            const batchMode = document.getElementById('batchMode')?.checked || false;
            const batchCount = parseInt(document.getElementById('batchCount')?.value || 1);
            
            if (batchMode && batchCount > 1) {{
                await generateBatch(batchCount);
                return;
            }}
            
            btn.disabled = true;
            if (spinner) spinner.classList.add('active');
            if (progressContainer) progressContainer.classList.add('active');
            
            
            if (CONFIG.features.progress) {{ connectWebSocket(); updateProgressUI(0, 'Initializing...'); }}
            try {{
                // Build workflow
                const workflow = JSON.parse(JSON.stringify(workflowTemplate));
                
                // Update parameters
                paramMap.forEach(param => {{
                    let value;
                    
                    // Special handling for upload fields (image or audio)
                    if (param.has_upload) {{
                        const uploadedInput = document.getElementById(param.id + '_uploaded');
                        const selectElement = document.getElementById(param.id);
                        const uploadType = param.upload_type || 'image';
                        
                        if (uploadedInput && uploadedInput.value && uploadedInput.dataset.uploaded === 'true') {{
                            // Use uploaded file name (file was actually uploaded to ComfyUI)
                            value = uploadedInput.value;
                            console.log(`{{uploadType === 'audio' ? '🎵' : '🖼️'}} Using uploaded file for ${{param.input_name}}: ${{value}}`);
                        }} else if (selectElement && selectElement.value) {{
                            // Use selected value from dropdown
                            value = selectElement.value;
                            console.log(`{{uploadType === 'audio' ? '🎵' : '🖼️'}} Using selected file for ${{param.input_name}}: ${{value}}`);
                        }} else if (uploadedInput && uploadedInput.value) {{
                            // File was selected but not uploaded - try to upload now
                            console.warn(`⚠️ File selected but not uploaded for ${{param.input_name}}. Attempting upload...`);
                            throw new Error(`${{uploadType.charAt(0).toUpperCase() + uploadType.slice(1)}} "{{uploadedInput.value}}" needs to be uploaded first. Please re-select the file.`);
                        }} else {{
                            // Fallback to default from workflow template
                            value = workflow[param.node_id]?.inputs?.[param.input_name] || '';
                            console.log(`${{uploadType === 'audio' ? '🎵' : '🖼️'}} Using default for ${{param.input_name}}: ${{value}}`);
                        }}
                    }} else {{
                        // Standard parameter handling
                        const element = document.getElementById(param.id);
                        if (!element) return;
                        
                        if (element.type === 'checkbox') {{
                            value = element.checked;
                        }} else if (element.type === 'number' || element.type === 'range') {{
                            value = parseFloat(element.value);
                            if (isNaN(value)) value = element.value;
                        }} else {{
                            value = element.value;
                        }}
                    }}
                    
                    if (workflow[param.node_id] && workflow[param.node_id].inputs) {{
                        workflow[param.node_id].inputs[param.input_name] = value;
                    }}
                }});
                
                // Validate upload fields
                let missingUploads = [];
                let notUploadedUploads = [];
                paramMap.forEach(param => {{
                    if (param.has_upload) {{
                        const uploadedInput = document.getElementById(param.id + '_uploaded');
                        const selectElement = document.getElementById(param.id);
                        const hasUploadedFile = uploadedInput && uploadedInput.value && uploadedInput.dataset.uploaded === 'true';
                        const hasSelectedFile = selectElement && selectElement.value;
                        const hasFilePendingUpload = uploadedInput && uploadedInput.value && (!uploadedInput.dataset.uploaded || uploadedInput.dataset.uploaded === 'false');
                        const uploadType = param.upload_type || 'image';
                        
                        if (hasFilePendingUpload) {{
                            notUploadedUploads.push(`${{uploadType.charAt(0).toUpperCase() + uploadType.slice(1)}}: ${{uploadedInput.value}}`);
                        }} else if (!hasUploadedFile && !hasSelectedFile) {{
                            missingUploads.push(`${{param.node_title}} → ${{param.input_name}}`);
                        }}
                    }}
                }});
                
                if (notUploadedUploads.length > 0) {{
                    showStatus(`Error: Files not uploaded yet: ${{notUploadedUploads.join(', ')}}. Please wait for upload to complete or re-select.`, 'error');
                    btn.disabled = false;
                    if (spinner) spinner.classList.remove('active');
                    if (progressContainer) progressContainer.classList.remove('active');
                    return;
                }}
                
                if (missingUploads.length > 0) {{
                    showStatus(`Error: Please select or upload a file for: ${{missingUploads.join(', ')}}`, 'error');
                    btn.disabled = false;
                    if (spinner) spinner.classList.remove('active');
                    if (progressContainer) progressContainer.classList.remove('active');
                    return;
                }}
                
                // Apply bypasses
                bypassToggles.forEach(toggle => {{
                    const checkbox = document.getElementById(toggle.id);
                    if (checkbox && checkbox.checked) {{
                        toggle.nodes.forEach(nodeId => {{
                            if (workflow[nodeId]) {{
                                workflow[nodeId].is_bypassed = true;
                            }}
                        }});
                    }}
                }});
                
                console.log('📤 Sending workflow to ComfyUI...');
                
                // Submit to ComfyUI
                const response = await fetch(`${{CONFIG.serverUrl}}/prompt`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ prompt: workflow, client_id: clientId }})
                }});
                
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const result = await response.json();
                currentPromptId = result.prompt_id;
                
                console.log('✅ Workflow submitted. Prompt ID:', currentPromptId);
                showStatus('Generation started! Waiting for results...', 'success');
                
                // Start polling
                if (CONFIG.features.progress) {{
                    startPolling();
                }} else {{
                    setTimeout(() => {{
                        btn.disabled = false;
                        if (spinner) spinner.classList.remove('active');
                    }}, 3000);
                }}
                
            }} catch (error) {{
                console.error('❌ Generation failed:', error);
                showStatus(`Error: ${{error.message}}`, 'error');
                btn.disabled = false;
                if (spinner) spinner.classList.remove('active');
                if (progressContainer) progressContainer.classList.remove('active');
            }}
        }}
        
        // Batch generation
        async function generateBatch(count) {{
            showStatus(`Starting batch generation (${{count}} images)...`, 'success');
            
            const randomizeSeed = document.getElementById('batchRandomSeed')?.checked || false;
            let seedElement = null;
            
            // Find seed parameter
            if (randomizeSeed) {{
                for (const param of paramMap) {{
                    if (param.type === 'seed' || param.input_name.toLowerCase().includes('seed')) {{
                        seedElement = document.getElementById(param.id);
                        break;
                    }}
                }}
            }}
            
            for (let i = 0; i < count; i++) {{
                console.log(`📦 Batch ${{i + 1}}/${{count}}`);
                
                // Randomize seed if enabled
                if (randomizeSeed && seedElement) {{
                    seedElement.value = Math.floor(Math.random() * 999999999999);
                }}
                
                await new Promise((resolve, reject) => {{
                    const originalCallback = window.generationComplete;
                    window.generationComplete = (success) => {{
                        window.generationComplete = originalCallback;
                        if (success) {{
                            resolve();
                        }} else {{
                            reject(new Error('Generation failed'));
                        }}
                    }};
                    
                    generate();
                }});
                
                // Wait between generations
                if (i < count - 1) {{
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }}
            }}
            
            showStatus(`Batch complete! Generated ${{count}} images.`, 'success');
        }}
        
        // Progress polling
        function startPolling() {{
            if (pollTimer) clearInterval(pollTimer);
            
            pollTimer = setInterval(async () => {{
                try {{
                    const response = await fetch(`${{CONFIG.serverUrl}}/history/${{currentPromptId}}`);
                    if (!response.ok) return;
                    
                    const history = await response.json();
                    const promptData = history[currentPromptId];
                    
                    if (promptData) {{
                        if (promptData.status && promptData.status.status_str === 'success') {{
                            console.log('✅ Generation complete!');
                            stopPolling();
                            handleGenerationComplete(promptData);
                        }} else if (promptData.status && promptData.status.status_str === 'error') {{
                            console.error('❌ Generation failed');
                            stopPolling();
                            showStatus('Generation failed. Check ComfyUI console.', 'error');
                        }} else {{
                            // In progress - if WebSocket isn't updating, keep UI alive
                            if (Date.now() - lastProgressTs > 1500) {{
                                updateProgressUI(5, 'Generating...');
                            }}
                        }}
                    }}
                }} catch (error) {{
                    console.error('Polling error:', error);
                }}
            }}, CONFIG.pollInterval);
        }}
        
        function stopPolling() {{
            if (pollTimer) {{
                clearInterval(pollTimer);
                pollTimer = null;
            }}
            
            const btn = document.getElementById('generateBtn');
            const spinner = document.getElementById('loadingSpinner');
            const progressContainer = document.getElementById('progressContainer');
            
            if (btn) btn.disabled = false;
            if (spinner) spinner.classList.remove('active');
            if (progressContainer) progressContainer.classList.remove('active');
        }}
        
        // Handle generation complete
        function handleGenerationComplete(promptData) {{
            showStatus('Generation complete!', 'success');
            
            if (!CONFIG.features.gallery) {{
                if (window.generationComplete) window.generationComplete(true);
                return;
            }}
            
            // Extract outputs
            const outputs = promptData.outputs || {{}};
            const galleryGrid = document.getElementById('galleryGrid');
            
            // Clear "no images" message
            if (galleryItems.length === 0) {{
                galleryGrid.innerHTML = '';
            }}
            
            Object.values(outputs).forEach(output => {{
                if (output.images) {{
                    output.images.forEach(img => {{
                        addToGallery(img, 'image');
                    }});
                }}
                if (output.gifs) {{
                    output.gifs.forEach(gif => {{
                        addToGallery(gif, 'gif');
                    }});
                }}
                if (output.videos) {{
                    output.videos.forEach(video => {{
                        addToGallery(video, 'video');
                    }});
                }}
                if (output.audio) {{
                    output.audio.forEach(audio => {{
                        addToGallery(audio, 'audio');
                    }});
                }}
            }});
            
            setupLightbox();
            initAllVideoThumbnails();
            
            if (window.generationComplete) window.generationComplete(true);
        }}
        
        // Gallery management
        function isVideoFile(filename) {{
            if (!filename) return false;
            const videoExts = ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v', '.3gp', '.ts', '.ogv'];
            const lower = filename.toLowerCase();
            // Check for exact match at end
            for (const ext of videoExts) {{
                if (lower.endsWith(ext)) return true;
            }}
            return false;
        }}

        function isAudioFile(filename) {{
            if (!filename) return false;
            const audioExts = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.opus', '.wma', '.aiff', '.au'];
            const lower = filename.toLowerCase();
            for (const ext of audioExts) {{
                if (lower.endsWith(ext)) return true;
            }}
            return false;
        }}

        function addToGallery(file, type, prepend = true) {{
            const galleryGrid = document.getElementById('galleryGrid');
            if (!galleryGrid) return;
            
            const item = document.createElement('div');
            item.className = 'gallery-item fade-in';
            
            // Force type to 'output' for viewing (not 'temp' or other types)
            // This ensures we always get the final output image, not temporary previews
            const viewType = 'output';
            const url = `${{CONFIG.serverUrl}}/view?filename=${{file.filename}}&type=${{viewType}}&subfolder=${{file.subfolder || ''}}`;
            
            // Auto-detect video and audio files by extension
            console.log('DEBUG file object:', JSON.stringify(file));
            const filename = file && file.filename ? file.filename : '';
            console.log('DEBUG filename:', filename, 'type:', type, 'isVideo:', isVideoFile(filename), 'isAudio:', isAudioFile(filename));
            
            // Check if it's a video by filename, regardless of passed type
            if (isVideoFile(filename)) {{
                console.log('DEBUG: Converting to video type');
                type = 'video';
            }}
            
            // Check if it's an audio file
            if (isAudioFile(filename)) {{
                console.log('DEBUG: Converting to audio type');
                type = 'audio';
            }}
            
            if (type === 'video') {{
                // Check if we're running from file:// protocol
                const isFileProtocol = window.location.protocol === 'file:';
                
                if (isFileProtocol) {{
                    // When opened via file://, show a clickable video card instead
                    item.innerHTML = `
                        <a href="${{url}}" target="_blank" style="display:block; width:100%; height:100%; text-decoration:none;">
                            <div style="width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; background:linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color:#fff; padding:0.5rem; box-sizing:border-box;">
                                <div style="font-size:3rem; margin-bottom:0.5rem;">🎬</div>
                                <div style="font-size:0.75rem; text-align:center; word-break:break-word; line-height:1.3; opacity:0.9;">
                                    <div style="font-weight:600; margin-bottom:0.25rem;">Video</div>
                                    <div style="font-size:0.65rem; opacity:0.7;">${{file.filename}}</div>
                                </div>
                                <div style="margin-top:0.5rem; font-size:0.65rem; background:rgba(99,102,241,0.3); padding:0.25rem 0.5rem; border-radius:12px;">Click to view</div>
                            </div>
                        </a>
                    `;
                }} else {{
                    // Normal HTTP/HTTPS - use video element with clickable link wrapper
                    item.innerHTML = `
                        <a href="${{url}}" target="_blank" style="display:block; width:100%; height:100%; text-decoration:none; position:relative;">
                            <div class="video-container" style="width:100%; height:100%; position:relative; background:linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);">
                                <video class="video-thumb loading" src="${{url}}" muted playsinline preload="auto" crossorigin="anonymous" 
                                    style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; pointer-events:none;"
                                    onloadeddata="this.classList.remove('loading'); console.log('Video loaded:', this.src);"
                                    onerror="console.error('Video error:', this.src); this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                </video>
                                <div class="video-fallback" style="display:none; position:absolute; inset:0; align-items:center; justify-content:center; flex-direction:column; background:inherit; color:#fff; font-size:0.75rem; text-align:center; padding:0.5rem;">
                                    <div style="font-size:2rem; margin-bottom:0.25rem;">🎬</div>
                                    <div style="font-size:0.65rem; opacity:0.8; word-break:break-word;">${{file.filename}}</div>
                                </div>
                            </div>
                            <div class="video-overlay">▶</div>
                            <div class="gallery-item-info">${{file.filename}}</div>
                        </a>
                    `;
                }}
            }} else if (type === 'audio') {{
                // Audio files - show clickable audio card
                item.innerHTML = `
                    <a href="${{url}}" target="_blank" style="display:block; width:100%; height:100%; text-decoration:none;">
                        <div style="width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; background:linear-gradient(135deg, #2d1b4e 0%, #1a1a2e 100%); color:#fff; padding:0.5rem; box-sizing:border-box; border-radius:8px;">
                            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🎵</div>
                            <div style="font-size:0.75rem; text-align:center; word-break:break-word; line-height:1.3; opacity:0.9;">
                                <div style="font-weight:600; margin-bottom:0.25rem;">Audio</div>
                                <div style="font-size:0.65rem; opacity:0.7;">${{file.filename}}</div>
                            </div>
                            <div style="margin-top:0.5rem; font-size:0.65rem; background:rgba(139,92,246,0.3); padding:0.25rem 0.5rem; border-radius:12px;">Click to play</div>
                        </div>
                    </a>
                `;
            }} else {{
                item.innerHTML = `
                    <a href="${{url}}" class="glightbox" data-gallery="gallery">
                        <img src="${{url}}" alt="${{file.filename}}" loading="lazy">
                        <div class="gallery-item-info">${{file.filename}}</div>
                    </a>
                `;
            }}
            
            if (prepend) {{
                galleryGrid.prepend(item);
                galleryItems.unshift({{ file, type, url }});
            }} else {{
                galleryGrid.appendChild(item);
                galleryItems.push({{ file, type, url }});
            }}

            // Initialize video thumbnails immediately
            if (type === 'video') {{
                const v = item.querySelector('video.video-thumb');
                if (v) initVideoThumbnail(v);
            }}

            // Limit gallery size
            if (galleryItems.length > 50) {{
                galleryGrid.lastChild.remove();
                galleryItems.pop();
            }}
        }}
        
        function clearGallery() {{
            if (!confirm('Clear all gallery items?')) return;
            
            const galleryGrid = document.getElementById('galleryGrid');
            if (galleryGrid) {{
                galleryGrid.innerHTML = '<div class="text-center text-muted">No images yet. Click Generate!</div>';
            }}
            galleryItems = [];
        }}
        
        function setupLightbox() {{
            if (typeof GLightbox !== 'undefined') {{
                GLightbox({{
                    selector: '.glightbox',
                    touchNavigation: true,
                    loop: true,
                    autoplayVideos: true
                }});
            }}
        }}
        
        // Status messages
        function showStatus(message, type = 'success') {{
            const statusEl = document.getElementById('statusMessage');
            if (!statusEl) return;
            
            statusEl.textContent = message;
            statusEl.className = `status-message show ${{type}}`;
            
            setTimeout(() => {{
                statusEl.classList.remove('show');
            }}, 5000);
        }}
        
        // Keyboard shortcuts
        function setupKeyboardShortcuts() {{
            document.addEventListener('keydown', function(e) {{
                // Ctrl+Enter: Generate
                if (e.ctrlKey && e.key === 'Enter') {{
                    e.preventDefault();
                    generate();
                }}
                // Ctrl+R: Reset
                else if (e.ctrlKey && e.key === 'r') {{
                    e.preventDefault();
                    resetParameters();
                }}
                // Ctrl+S: Save preset
                else if (e.ctrlKey && e.key === 's') {{
                    e.preventDefault();
                    if (CONFIG.features.presets) savePreset();
                }}
                // ?: Toggle shortcuts help
                else if (e.key === '?') {{
                    toggleShortcutsHelp();
                }}
            }});
        }}
        
        function toggleShortcutsHelp() {{
            const help = document.getElementById('shortcutsHelp');
            if (help) {{
                help.classList.toggle('show');
            }}
        }}
        
        console.log('%c🚀 {
            app_name
        } Ready!', 'color: #6366f1; font-size: 20px; font-weight: bold;');
        console.log('%cPress ? for keyboard shortcuts', 'color: #8b5cf6; font-size: 14px;');
    </script>
</body>
</html>'''

        return html

    def generate_input_html(self, param, param_id):
        """Generate appropriate HTML input for parameter type"""
        value = param["value"]
        ptype = param["type"]
        options = param.get("options")
        upload_type = param.get("upload_type", "image")

        # Safety check: if we have options but type isn't dropdown, fix it
        if (
            options
            and len(options) > 0
            and ptype not in ["dropdown", "toggle", "image_upload", "audio_upload"]
        ):
            ptype = "dropdown"

        if ptype in ["image_upload", "audio_upload"]:
            # Image/audio upload widget with dropdown for existing files
            # Check if current value exists in options
            value_exists = options and str(value) in [str(opt) for opt in options]

            options_html = "".join(
                [
                    f'<option value="{opt}" {"selected" if str(opt) == str(value) else ""}>{opt}</option>'
                    for opt in (options or [])
                ]
            )

            # Warning if value doesn't exist in options
            warning_html = ""
            if value and not value_exists:
                warning_html = f'<div class="text-warning small mt-1">⚠️ Warning: Selected file "{value}" not found in input folder</div>'

            return f'''
                <div class="image-upload-widget">
                    <div class="input-group mb-2">
                        <input type="file" id="{
                param_id
            }_file" class="form-control d-none" accept="{
                ".jpg,.jpeg,.png,.gif"
                if upload_type == "image"
                else ".mp3,.wav,.ogg,.m4a,.aac"
            }" 
                        onchange="handleUpload('{param_id}', this, '{upload_type}')">
                        <button class="btn btn-outline-primary" type="button" onclick="document.getElementById('{
                param_id
            }_file').click()">
                            <i class="fas fa-upload"></i> Upload {
                upload_type.capitalize()
            }
                        </button>
                        {
                f"""<select id="{param_id}" class="form-control" data-default="{value}" value="{value if value_exists else ""}"
                                onchange="handleSelect('{param_id}', this.value, '{upload_type}'); autosaveParameters()">
                            <option value="" disabled {"selected" if not value_exists else ""}>Select existing {upload_type}...</option>
                            {options_html}
                        </select>"""
                if options
                else ""
            }
                    </div>
                    {warning_html}
                    <div id="{
                param_id
            }_preview" class="image-preview-container mt-2" style="display: none;">
                        {
                f'<img id="{param_id}_preview_img" src="" alt="Preview" style="max-width: 200px; max-height: 150px; border-radius: 8px;">'
                if upload_type == "image"
                else ""
            }
                        {
                f'<audio id="{param_id}_preview_audio" controls style="width: 100%; margin-top: 10px;"></audio>'
                if upload_type == "audio"
                else ""
            }
                    <button class="btn btn-sm btn-outline-danger mt-1" onclick="clearUpload('{
                param_id
            }', '{upload_type}')">
                            <i class="fas fa-times"></i> Clear
                        </button>
                    </div>
                    <input type="hidden" id="{param_id}_uploaded" value="">
                </div>
            '''

        elif ptype == "dropdown" and options:
            options_html = "".join(
                [
                    f'<option value="{opt}" {"selected" if str(opt) == str(value) else ""}>{opt}</option>'
                    for opt in options
                ]
            )
            return f'<select id="{param_id}" class="form-control" data-default="{value}" onchange="autosaveParameters()">{options_html}</select>'

        elif ptype == "toggle":
            checked = "checked" if value else ""
            return f'''
                <label class="toggle-switch">
                    <input type="checkbox" id="{param_id}" {checked} data-default="{value}" onchange="autosaveParameters()">
                    <span class="slider-toggle"></span>
                </label>
            '''

        elif ptype == "seed":
            return f'''
                <div class="input-group">
                    <input type="number" id="{param_id}" value="{value}" class="form-control" data-default="{value}" onchange="autosaveParameters()">
                    <button class="btn btn-outline-secondary" onclick="document.getElementById('{param_id}').value = Math.floor(Math.random() * 999999999999); autosaveParameters();">
                        <i class="fas fa-random"></i>
                    </button>
                </div>
            '''

        elif ptype in ["slider", "slider_small"]:
            min_val = 0
            max_val = 100 if ptype == "slider" else 2
            step = 0.1 if isinstance(value, float) else 1
            return f'''
                <div class="slider-container">
                    <input type="range" id="{param_id}" min="{min_val}" max="{max_val}" step="{step}" value="{value}" 
                           oninput="updateSlider('{param_id}')" data-default="{value}">
                    <span class="slider-value" id="{param_id}_value">{value}</span>
                </div>
            '''

        elif ptype == "number":
            return f'<input type="number" id="{param_id}" value="{value}" class="form-control" data-default="{value}" onchange="autosaveParameters()">'

        elif ptype == "textarea":
            return f'<textarea id="{param_id}" rows="5" class="form-control" data-default="{value}" onchange="autosaveParameters()">{value}</textarea>'

        else:  # text, path, file_selector
            return f'<input type="text" id="{param_id}" value="{value}" class="form-control" data-default="{value}" onchange="autosaveParameters()">'


# Gradio Interface
def create_interface():
    """Create enhanced Gradio interface"""
    generator = SmartWorkflowGenerator()

    with gr.Blocks(
        title="ComfyUI HTML Generator v2.0", theme=gr.themes.Soft()
    ) as interface:
        gr.Markdown(f"""
        # 🚀 ComfyUI Workflow to HTML Generator v{generator.VERSION}
        ### Create professional, standalone HTML interfaces for your ComfyUI workflows
        
        **Features:** Modern UI, Dark Mode, Presets, Gallery, Progress Tracking, and more!
        """)

        with gr.Row():
            with gr.Column(scale=2):
                workflow_file = gr.File(
                    label="📁 Upload ComfyUI Workflow JSON", file_types=[".json"]
                )
                server_url = gr.Textbox(
                    label="🌐 ComfyUI Server URL",
                    value="http://127.0.0.1:8188",
                    placeholder="http://127.0.0.1:8188",
                )
                load_btn = gr.Button(
                    "🔍 Load & Analyze Workflow", variant="primary", size="lg"
                )

            with gr.Column(scale=1):
                info_box = gr.Textbox(label="ℹ️ Status", lines=5, interactive=False)

        param_selector = gr.CheckboxGroup(
            label="✅ Select Parameters to Include",
            choices=[],
            value=[],
            interactive=True,
        )

        param_choices_state = gr.State([])
        with gr.Row():
            select_all_btn = gr.Button("✅ Select All")
            select_none_btn = gr.Button("⬜ Select None")

        with gr.Row():
            app_name = gr.Textbox(
                label="📝 App Name",
                value="My ComfyUI Generator",
                placeholder="Enter a name for your HTML app",
            )
            output_path = gr.Textbox(
                label="📂 Output Directory (in ComfyUI)",
                value="output",
                placeholder="output",
            )

        feature_selector = gr.CheckboxGroup(
            label="🎨 Enable Features",
            choices=[
                "Dark Mode",
                "Preset System",
                "Enhanced Gallery",
                "Progress Tracking",
                "Tooltips",
                "Keyboard Shortcuts",
                "Auto-save Parameters",
                "Batch Generation",
            ],
            value=[
                "Dark Mode",
                "Preset System",
                "Enhanced Gallery",
                "Progress Tracking",
                "Tooltips",
                "Keyboard Shortcuts",
                "Auto-save Parameters",
                "Batch Generation",
            ],
        )

        generate_btn = gr.Button("🎨 Generate HTML", variant="primary", size="lg")

        result_text = gr.Textbox(label="✅ Result", lines=10, interactive=False)

        # Event handlers
        load_btn.click(
            fn=generator.load_workflow,
            inputs=[workflow_file, server_url],
            outputs=[param_selector, info_box, param_choices_state],
        )

        select_all_btn.click(
            fn=lambda all_vals: gr.update(value=all_vals),
            inputs=[param_choices_state],
            outputs=[param_selector],
        )

        select_none_btn.click(
            fn=lambda: gr.update(value=[]), inputs=[], outputs=[param_selector]
        )

        def generate_with_error_handling(
            selected_indices, app_name, server_url, output_path, enable_features
        ):
            try:
                result, filepath = generator.generate_html(
                    selected_indices, app_name, server_url, output_path, enable_features
                )
                return result
            except Exception as e:
                import traceback

                error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
                return error_msg

        generate_btn.click(
            fn=generate_with_error_handling,
            inputs=[
                param_selector,
                app_name,
                server_url,
                output_path,
                feature_selector,
            ],
            outputs=[result_text],
        )

        gr.Markdown("""
        ---
        ### 📚 Quick Guide:
        1. **Upload** your ComfyUI workflow JSON file
        2. **Load** to analyze parameters (make sure ComfyUI is running!)
        3. **Select** which parameters to include
        4. **Choose** features you want
        5. **Generate** your professional HTML interface!
        
        ### ⌨️ Pro Tips:
        - Generated HTML works completely standalone
        - Uses Bootstrap 5 + modern CSS
        - Dark mode auto-saves preference
        - Presets stored in browser localStorage
        - Gallery shows last 50 generations
        - Keyboard shortcuts: Ctrl+Enter (generate), Ctrl+R (reset), Ctrl+S (save preset)
        
        **Made with ❤️ for the ComfyUI community**
        """)

    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.queue()
    interface.launch(
        server_name="0.0.0.0", server_port=7860, share=False, inbrowser=True
    )
