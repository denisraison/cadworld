# CADWorld - AI-Driven CAD Workspace

## Skills

### `/cad` - Generate CAD Parts
Generate CadQuery code from text descriptions using the local AI model.

```
/cad A mounting bracket 0.5 units x 0.3 units with 4 M4 holes
```

The skill will:
1. Generate CadQuery code using Text-to-CadQuery model
2. Validate the code
3. Display in OCP Viewer for visual feedback
4. Save to `./generated/latest.py`

### `/slicer` - Analyze & Optimize for Printing
Analyze, optimize, and slice 3D models using Bambu Studio CLI.

**Required workflow:**
```
/cad → STL → Open in Bambu Studio GUI → Save Project As .3mf → /slicer
```

The CLI needs printer/filament profiles that only the GUI provides.

```
/slicer analyze mypart.3mf         # Check current settings
/slicer optimize for strength      # Modifies settings in 3MF
/slicer slice mypart.3mf           # Shows print time/filament estimates
```

The skill will:
1. Find your 3MF file (user must save manually from Bambu Studio)
2. Analyze current print settings
3. Modify 3MF settings programmatically
4. Slice and report print time/filament estimates
5. Output gcode to `/tmp/plate_1.gcode`

**Optimization presets:**
- `fast` - 0.28mm layers, 10% infill, 2 walls (prototypes)
- `balanced` - 0.20mm layers, 15% infill, 3 walls (general use)
- `strong` - 0.16mm layers, 25% infill, 4 walls (functional parts)
- `accurate` - 0.12mm layers, slower speeds (tight tolerances)

## Project Overview

This workspace integrates AI models and MCP servers for generating CAD models from natural language descriptions. Based on research from the Text-to-CadQuery project achieving 69.3% exact match rates with visual feedback loops improving success to 85%+.

## Directory Structure

```
cadworld/
├── models/
│   ├── text2cadquery/          # Fine-tuned qwen2.5-3B-SFT model (6GB)
│   ├── BlenderLLM-7.6B-Q4_K_M.gguf  # BlenderLLM for Blender scripts
│   └── Modelfile.blenderllm    # Ollama modelfile for BlenderLLM
├── cadquery-mcp-server/        # CadQuery MCP server (cloned repo)
├── text2cadquery_inference.py  # Text-to-CadQuery inference script
├── REPORT.md                   # Research findings and recommendations
├── README.md                   # Installation guide
└── CLAUDE.md                   # This file
```

## Models

### Text-to-CadQuery (Primary for CAD generation)
- **Model**: `ricemonster/qwen2.5-3B-SFT`
- **Location**: `./models/text2cadquery/`
- **Size**: 3B parameters, ~6GB on disk
- **Format**: Safetensors (HuggingFace Transformers)
- **Source**: https://huggingface.co/ricemonster/qwen2.5-3B-SFT
- **Paper**: https://arxiv.org/abs/2505.06507
- **Repo**: https://github.com/Text-to-CadQuery/Text-to-CadQuery

**Prompt format**:
```
### Instruction:
{description}

### Response:
```

**Usage** (run from repo root):
```bash
python3 ./text2cadquery_inference.py "A box 0.5 units x 0.3 units x 0.2 units"
python3 ./text2cadquery_inference.py -i  # Interactive mode
python3 ./text2cadquery_inference.py -v "description"  # With validation
```

**Important**: Model uses normalized coordinates (0-1 range). Describe dimensions as fractions or use detailed spatial descriptions.

### BlenderLLM (For Blender Python scripts)
- **Model**: BlenderLLM-7.6B-Q4_K_M
- **Location**: `./models/BlenderLLM-7.6B-Q4_K_M.gguf`
- **Ollama name**: `blenderllm`
- **Source**: https://huggingface.co/BAAI/BlenderLLM (original)
- **Quantized**: https://huggingface.co/bartowski/BlenderLLM-GGUF

**Usage**:
```bash
ollama run blenderllm "Create a table with 4 legs"
```

## MCP Servers

Configuration in `~/.claude.json`:

### BlenderMCP
- **Command**: `uvx blender-mcp`
- **Repo**: https://github.com/ahujasid/blender-mcp (16,700+ stars)
- **Requires**: Blender running with addon enabled
- **Addon location**: `~/.var/app/org.blender.Blender/config/blender/5.0/scripts/addons/blender_mcp_addon.py`

### CadQuery MCP
- **Command**: `uv run --directory ./cadquery-mcp-server python server.py`
- **Repo**: https://github.com/rishigundakaram/cadquery-mcp-server
- **Features**: Model verification, STL/PNG generation

### OCP Viewer MCP
- **Command**: `python3 -m ocp_viewer_mcp.server`
- **Repo**: https://github.com/dmilad/ocp-viewer-mcp
- **Features**: Screenshot capture from OCP CAD Viewer for visual feedback

### FreeCAD MCP
- **Command**: `uvx freecad-mcp`
- **Repo**: https://github.com/neka-nat/freecad-mcp
- **Note**: Less mature than BlenderMCP, requires FreeCAD running

## Installed Packages

### Python
- `cadquery` 2.6.1 - Parametric CAD library
- `ocp-vscode` 3.0.1 - OCP viewer for VSCode
- `ocp-viewer-mcp` 0.1.0 - MCP server for OCP viewer
- `transformers` - HuggingFace model loading
- `torch` - PyTorch for inference
- `huggingface-hub` - Model downloads

### System
- **Blender**: Flatpak org.blender.Blender 5.0
- **Bambu Studio**: Flatpak com.bambulab.BambuStudio 2.4.0 - 3D printing slicer
- **Ollama**: Local LLM runner

## Ollama Models

```bash
ollama list  # Show installed models
```

| Model | Size | Purpose |
|-------|------|---------|
| blenderllm | 4.7GB | Blender Python generation |

## Quick Reference

### Generate CadQuery code
```bash
# Using fine-tuned Text-to-CadQuery model (run from repo root)
python3 ./text2cadquery_inference.py -v "The design features a rectangular block measuring 0.75 units in length, 0.5 units in width, and 0.25 units in height"

# Interactive mode
python3 ./text2cadquery_inference.py -i
```

### Generate Blender scripts
```bash
ollama run blenderllm "Create a wooden table with 4 legs, 1m x 0.6m top, 0.75m height"
```

### Start services
```bash
# Ollama (if not running)
ollama serve &

# Blender (for BlenderMCP)
flatpak run org.blender.Blender &
# Then enable addon: Edit → Preferences → Add-ons → "Blender MCP"
```

## Research References

- **Text-to-CadQuery paper**: https://arxiv.org/abs/2505.06507
- **BlenderLLM paper**: https://arxiv.org/abs/2412.14203
- **DeepCAD dataset**: Foundation for Text-to-CadQuery training data
- **Visual feedback loops**: 85%+ success rate with render-critique-iterate cycle

## Tips for Best Results

1. **Use detailed descriptions** - "A rectangular block with rounded edges, 0.75 units long" works better than "a box"

2. **Normalized dimensions** - The Text-to-CadQuery model expects 0-1 range coordinates

3. **Effective prompt formula**: `[Part Type] + [Dimensions] + [Features with counts] + [Manufacturing Context]`

4. **Visual feedback** - Use OCP Viewer MCP to see results and iterate

5. **Standard parts work best** - M4 holes, flanges, brackets generate reliably

## Troubleshooting

### Model not loading
```bash
# Check CUDA available
python3 -c "import torch; print(torch.cuda.is_available())"

# Check model files exist (run from repo root)
ls -la ./models/text2cadquery/*.safetensors
```

### MCP server not connecting
```bash
# Restart Claude Code after config changes
# Check Blender addon is enabled (for BlenderMCP)
# Ensure Blender/FreeCAD is running before using their MCPs
```

### Ollama issues
```bash
# Start server
ollama serve

# Check models
ollama list
```
