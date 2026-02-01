# AI-driven CAD workflows that actually work in 2025

**The AI-CAD landscape has shifted dramatically since early 2024.** Your frustration with neka-nat's freecad-mcp reflects a broader reality: FreeCAD has the weakest AI integration of any major CAD tool. The breakthrough solution is switching to **BlenderMCP** (16,700+ GitHub stars) combined with **BlenderLLM** or **CadQuery-based pipelines**—all of which run comfortably on your 24GB GPU and dramatically outperform FreeCAD workflows. For DIY projects like frames and platforms, the winning combination is specialized fine-tuned models generating CadQuery/OpenSCAD code with visual feedback loops that achieve **85-95% success rates** compared to the ~50% you're likely experiencing now.

## Local CAD models that fit your 24GB GPU

The most practical breakthrough is **BlenderLLM**, a 7B parameter model released December 2024 that benchmarks higher than GPT-4-Turbo and Claude-3.5-Sonnet on CAD generation. It uses only **15-17GB VRAM** in FP16 (or ~4GB quantized) and achieves a **3.4% syntax error rate** compared to 15-18% for frontier models. The model generates Blender Python scripts directly executable in Blender, trained on 12,000 instruction/script pairs.

**Text-to-CadQuery** represents the best pure text-to-CAD pipeline for your hardware. Fine-tuned versions of Qwen2.5-3B achieve **69.3% exact match** on CadQuery generation—and Mistral-7B variants achieve **1.32% invalid syntax rates**. The project provides 170,000 text-CadQuery training pairs and all models are available on HuggingFace. The 3B model uses only ~7GB VRAM, leaving headroom for other processes.

**CAD-Coder** from MIT offers something unique: image-to-CAD generation. This vision-language model can take a photograph or rendered image and generate valid CadQuery code with **100% syntax validity**. It fits on 24GB with optimization and can generalize from real-world photos—useful for recreating existing objects.

| Model | Parameters | VRAM (FP16) | Output Format | Best For |
|-------|-----------|-------------|---------------|----------|
| BlenderLLM | 7B | ~15GB | Blender Python | General 3D/CAD |
| Text-to-CadQuery (Qwen2.5-3B) | 3B | ~7GB | CadQuery | Parametric parts |
| CAD-Coder | ~7B VLM | ~18GB | CadQuery | Image-to-CAD |
| DeepSeek-R1-Distill-Qwen-7B | 7B | ~15GB | Various | Training-free approach |

For your DeepSeek interest, **Seek-CAD** demonstrates a training-free approach using DeepSeek-R1 with visual feedback for self-refinement—the distilled 7B versions run easily on your hardware.

## BlenderMCP completely outclasses FreeCAD integration

The single biggest improvement you can make is switching from neka-nat/freecad-mcp to **ahujasid/blender-mcp**, which has **16,700+ GitHub stars** versus minimal FreeCAD MCP adoption. This isn't marginal—it's a generation ahead.

BlenderMCP provides full Claude integration via socket-based communication with capabilities including object creation/modification/deletion, material control, scene inspection, Python code execution, and integration with Poly Haven assets (HDRIs, textures, models). It also connects to **Hyper3D Rodin** for AI 3D model generation and Sketchfab for model downloads. Setup is straightforward: `uvx blender-mcp` with Claude Desktop configuration.

For CadQuery specifically, **rishigundakaram/cadquery-mcp-server** provides model validation and SVG generation for visual feedback. For OpenSCAD, **jhacksman/OpenSCAD-MCP-Server** offers multi-view reconstruction, AI image generation through Gemini/Venice.ai APIs, and CUDA-accelerated processing.

**CQAsk** (github.com/OpenOrion/CQAsk) is an open-source web UI for text-to-CadQuery generation with 171 stars. It currently requires an OpenAI API key but can be modified for local LLM backends. The interface handles STL/STEP export directly.

## Visual feedback loops that achieve 85%+ success rates

A working proof-of-concept documented by practitioners demonstrates a **5-step iterative visual feedback cycle**: AI writes OpenSCAD code → system renders orthographic views → AI examines rendered images → AI critiques the design ("legs too thin," "proportions wrong") → AI modifies code and repeats. This improved accuracy by approximately **15%** compared to text-only systems.

The **CADialogue research** achieved **95.71% success rate** through self-correction with human-in-the-loop refinement. Text plus image input significantly improved performance on semantically complex prompts. The key insight: caching confirmed macros yielded an **85.71% speedup** on repeated executions.

For practical implementation, use **OCP Viewer MCP** (dmilad/ocp-viewer-mcp) to capture screenshots from OCP CAD Viewer, enabling Claude to "see" CadQuery/Build123d models directly. This creates the visual feedback loop: generate → render → AI examines → iterate.

The **Text-to-CadQuery** research quantified this precisely: initial execution success rate was only 53%, but with self-correction feedback loops it jumped to **85%**. Shape verification using Blender rendering confirmed geometric accuracy.

## Practical workflows makers are actually using

The **Claude + OpenSCAD workflow** has emerged as the most popular practical approach among makers and engineers. Successful documented use cases include custom replacement parts, electronics enclosures, robotics brackets, workshop jigs, and storage systems. The workflow: describe part in natural language → Claude generates OpenSCAD code → preview → iterate with Claude → export STL.

**OpenSCAD Studio** (github.com/zacharyfmarion/openscad-studio) provides a Cursor-like IDE for OpenSCAD with built-in AI copilot supporting Claude/GPT, live preview, and dedicated 2D/SVG mode for laser cutting. The developer noted they "found myself plugging OpenSCAD code into ChatGPT to scaffold starting points."

What works exceptionally well: standard mechanical parts. As one HackerNews practitioner noted, "It's almost like the model was trained on the entire McMaster-Carr catalog"—M4 cap screws, pipe flanges, and catalog parts generate reliably. Quick brackets, enclosures, and basic gear profiles succeed consistently.

What fails: complex custom designs require "paragraphs of metes-and-bounds language," organic shapes "go sideways fast," and parts requiring tight tolerances for multi-part assemblies remain problematic. Your dog pool platform frame would work well; complex interlocking joinery would struggle.

## Prompt engineering formulas that dramatically improve results

Zoo.dev's documentation provides before/after comparisons demonstrating the difference between failed and successful prompts:

| Failing Prompt | Working Prompt |
|----------------|----------------|
| "a manhole cover" | "a manhole cover with cuts for lifting, 600mm diameter, 50mm thick, with a 200mm hole in the middle" |
| "PDU faceplate" | "PDU faceplate, 1 switch, 11 european plugs, 6 wide keyhole slots, standard size in mm" |

The **effective prompt formula** is: `[Part Type] + [Dimensions] + [Features with counts] + [Manufacturing Context]`

Critical elements that improve success rates:
- **Explicit dimensions**: Always include mm/inches, never rely on "standard" or "normal"
- **Feature counts**: "4 mounting holes," "2 slots," specific quantities
- **Standards references**: "M4 holes," "114.3mm PCD," industry terminology
- **Manufacturing context**: "for 3D printing," "for CNC milling"

For OpenSCAD specifically, request parametric code with customization variables, separate modules for distinct components, and clear comments. A practitioner studying Claude Code for 20 hours found that pulling library sources (like BOSL2) into the working directory lets Claude grep and learn from existing code patterns.

**Effective prompt example**: "L-bracket, 100mm x 80mm x 3mm thick aluminum, 4 countersunk M4 mounting holes at 25mm spacing, fillet all edges 2mm, for CNC milling"

## The best tool stack for your specific use cases

For **wall frames and platforms**, CadQuery with parametric dimensions will serve you best. Generate structural members as separate parametric components with explicit interface dimensions, then assemble manually. AI handles individual parts well; assemblies require human coordination.

For **visualizing part connections**, use BlenderMCP to import generated parts and position them in scene. The Poly Haven integration provides realistic materials and environments. Zoo.dev's Text-to-CAD produces editable STEP files with B-Rep geometry (not meshes), which import cleanly for assembly visualization.

**Recommended tool stack for your hardware**:
1. **BlenderLLM** (local, 7B) for Blender Python generation
2. **Text-to-CadQuery Qwen2.5-3B** (local, 3B) for parametric parts
3. **BlenderMCP** for Claude integration and scene management
4. **Zoo.dev** (40 free minutes/month) for quick text-to-STEP when needed
5. **OpenSCAD Studio** for code-first parametric work with AI copilot

## Cost and complexity comparison

| Approach | Monthly Cost | Setup Complexity | Success Rate |
|----------|-------------|------------------|--------------|
| BlenderLLM + BlenderMCP | ~$20 (Claude Pro) | Medium | High |
| Text-to-CadQuery local | $0 | Medium-High | High |
| OpenSCAD + Claude | ~$20 | Low | Medium-High |
| Zoo.dev | Free (40 min) | Very Low | High |
| FreeCAD + neka-nat MCP | $0 | Low | Low |

The investment in switching from FreeCAD to Blender/CadQuery pays off immediately. BlenderMCP's 16,700 stars versus FreeCAD's minimal MCP ecosystem reflects real community validation—the tooling, documentation, and integration quality are simply better.

## Conclusion

Your path forward involves three changes: replace FreeCAD with **Blender + BlenderMCP** or **CadQuery** for dramatically better AI integration; run **BlenderLLM or Text-to-CadQuery** locally on your 24GB GPU for specialized CAD generation that outperforms GPT-4; and implement visual feedback loops where the AI renders and critiques its own output. For your DIY projects, generate individual parametric components (frame members, platform pieces) separately with explicit dimensions, then assemble manually. The technology now supports reliable single-part generation—complex assemblies remain the frontier. Start with Zoo.dev's free tier to validate text-to-CAD quality, then migrate to local models for unlimited generation without API costs.