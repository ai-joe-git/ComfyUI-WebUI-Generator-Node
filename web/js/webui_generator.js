import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

function addButtons(node) {
  if (node.__webuiGenButtonsAdded) return;
  node.__webuiGenButtonsAdded = true;

  node.addWidget("button", "Open Generator UI", null, async () => {
    try {
      const info = await api.fetchApi("/webui-generator/info").then(r => r.json());
      const host = info.host || "127.0.0.1";
      const port = info.port || 7860;

      // Open generator (Gradio) in a new tab
      const url = `http://${host}:${port}`;
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (e) {
      console.error(e);
      alert("Failed to get generator URL. Check ComfyUI console logs.");
    }
  });

  node.addWidget("button", "Open ComfyUI Output Folder", null, async () => {
    try {
      await api.fetchApi("/webui-generator/open-output", { method: "POST" });
    } catch (e) {
      console.error(e);
      alert("Failed to open output folder.");
    }
  });

  node.addWidget("text", "Note", "Upload the *API workflow JSON* in the generator UI.", () => {});
}

app.registerExtension({
  name: "ai.joe.webui_generator_node",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name === "WebUI_Generator_Launcher") {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const r = onNodeCreated?.apply(this, arguments);
        addButtons(this);
        return r;
      };
    }
  }
});
