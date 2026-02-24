from .server import ensure_generator_running


class WebUIGeneratorLauncher:
    """
    A tiny 'utility' node whose UI button is implemented in web/js.
    The backend only ensures the generator server is running.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {}
        }

    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "utils"

    def run(self):
        ensure_generator_running()
        return ()


NODE_CLASS_MAPPINGS = {
    "WebUI_Generator_Launcher": WebUIGeneratorLauncher,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WebUI_Generator_Launcher": "ComfyUI WebUI Generator (Open)",
}
