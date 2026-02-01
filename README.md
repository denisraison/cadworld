# CADWorld Setup Guide

This guide covers installation of all dependencies for the CADWorld AI-driven CAD workspace.

## Prerequisites

- **GPU**: NVIDIA GPU with 8GB+ VRAM (tested on RTX 3090)
- **Python**: 3.10+
- **Blender**: 4.0+ (for BlenderMCP)
- **Bambu Studio**: 2.0+ (for 3D printing slicer integration)

## Quick Start

```bash
# 1. Clone the repo
git clone git@github.com:denisraison/cadworld.git
cd cadworld

# 2. Install Python dependencies
pip install cadquery ocp-vscode transformers torch huggingface-hub

# 3. Download the AI model (see below)

# 4. Clone MCP servers (see below)

# 5. Configure Claude Code (see below)
```

## 1. AI Models

### Text-to-CadQuery (Primary - Required)

Download the fine-tuned Qwen2.5-3B model for CadQuery generation:

```bash
mkdir -p models/text2cadquery
cd models/text2cadquery

# Download from HuggingFace (requires huggingface-cli)
pip install huggingface-hub
huggingface-cli download ricemonster/qwen2.5-3B-SFT --local-dir .

# Or use Python
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('ricemonster/qwen2.5-3B-SFT', local_dir='.')
"
```

**Model details:**
- Size: ~6GB
- Source: https://huggingface.co/ricemonster/qwen2.5-3B-SFT
- Paper: https://arxiv.org/abs/2505.06507

### BlenderLLM (Optional - for Blender scripts)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download BlenderLLM GGUF
cd models
wget https://huggingface.co/bartowski/BlenderLLM-GGUF/resolve/main/BlenderLLM-7.6B-Q4_K_M.gguf

# Create Ollama Modelfile
cat > Modelfile.blenderllm << 'EOF'
FROM ./BlenderLLM-7.6B-Q4_K_M.gguf
TEMPLATE """{{ .Prompt }}"""
PARAMETER stop "<|endoftext|>"
PARAMETER num_ctx 4096
EOF

# Register with Ollama
ollama create blenderllm -f Modelfile.blenderllm
```

**Model details:**
- Size: ~4.7GB
- Source: https://huggingface.co/bartowski/BlenderLLM-GGUF

## 2. MCP Servers

### Required MCP Servers

Clone these repositories for MCP server functionality:

```bash
# CadQuery MCP - Code generation and validation
git clone https://github.com/rishigundakaram/cadquery-mcp-server.git
cd cadquery-mcp-server && pip install -e . && cd ..

# OCP Viewer MCP - Visual feedback screenshots
pip install ocp-viewer-mcp
```

### Optional MCP Servers

```bash
# BlenderMCP - Blender integration (install via uvx, no clone needed)
# Configured in ~/.claude.json as: uvx blender-mcp

# FreeCAD MCP - FreeCAD integration (install via uvx, no clone needed)
# Configured in ~/.claude.json as: uvx freecad-mcp

# Bambu MCP Agent - 3D printer slicer integration
git clone https://github.com/dmilad/bambu-mcp-agent.git
cd bambu-mcp-agent && pip install -e . && cd ..
```

## 3. Claude Code Configuration

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "uvx",
      "args": ["blender-mcp"]
    },
    "freecad-mcp": {
      "command": "uvx",
      "args": ["freecad-mcp"]
    },
    "cadquery-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "<path-to-cadworld>/cadquery-mcp-server", "python", "server.py"]
    },
    "ocp-viewer": {
      "command": "python3",
      "args": ["-m", "ocp_viewer_mcp.server"]
    }
  }
}
```

Restart Claude Code after updating configuration.

## 4. Application Setup

### Blender (for BlenderMCP)

```bash
# Install Blender (Ubuntu/Debian)
flatpak install flathub org.blender.Blender

# Or download from blender.org
```

Enable the BlenderMCP addon:
1. Launch Blender
2. Edit → Preferences → Add-ons
3. Install addon from BlenderMCP repo's addon folder
4. Enable "Blender MCP"
5. In 3D Viewport sidebar (N) → BlenderMCP → Start Server

### Bambu Studio (for slicer integration)

```bash
# Install Bambu Studio
flatpak install flathub com.bambulab.BambuStudio
```

## 5. Python Dependencies

```bash
# Core CAD libraries
pip install cadquery ocp-vscode

# AI model inference
pip install torch transformers huggingface-hub

# MCP servers
pip install ocp-viewer-mcp
```

## Verification

```bash
# Check Text-to-CadQuery model
python3 text2cadquery_inference.py -v "A box 0.5 units x 0.3 units x 0.2 units"

# Check CadQuery
python3 -c "import cadquery as cq; print('CadQuery OK')"

# Check Ollama (if using BlenderLLM)
ollama list

# Check repo size (should be <1MB without models)
du -sh .
```

## Directory Structure

After setup, your directory should look like:

```
cadworld/
├── CLAUDE.md                   # Main documentation
├── SETUP.md                    # This file
├── REPORT.md                   # Research findings
├── text2cadquery_inference.py  # Inference script
├── .claude/skills/             # Skill definitions
├── examples/
│   ├── l_bracket.py            # Example CadQuery code
│   └── l_bracket.stl           # Example output
├── models/                     # Downloaded separately
│   └── text2cadquery/          # Qwen2.5-3B-SFT model
├── cadquery-mcp-server/        # Cloned separately
└── ocp-viewer-mcp/             # Cloned separately (or pip installed)
```

## Troubleshooting

### Model not loading
```bash
# Check CUDA
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check model files
ls -la models/text2cadquery/*.safetensors
```

### MCP server not connecting
- Restart Claude Code after config changes
- Ensure Blender/FreeCAD is running before using their MCPs
- Check port availability: `lsof -i :9876`

### Ollama issues
```bash
ollama serve  # Start server
ollama list   # Check models
```

## Resources

- [Text-to-CadQuery Paper](https://arxiv.org/abs/2505.06507)
- [Text-to-CadQuery GitHub](https://github.com/Text-to-CadQuery/Text-to-CadQuery)
- [BlenderLLM Paper](https://arxiv.org/abs/2412.14203)
- [CadQuery Documentation](https://cadquery.readthedocs.io/)
- [BlenderMCP GitHub](https://github.com/ahujasid/blender-mcp)
