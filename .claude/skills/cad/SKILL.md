---
name: cad
description: Generate CAD parts from text descriptions. Use when the user wants to create 3D parts, brackets, enclosures, or mechanical components.
argument-hint: [part description with dimensions]
allowed-tools: Write, Bash(python3 *), Read, mcp__ocp-viewer__*
---

# CAD Part Generator

Generate CadQuery code from natural language descriptions with visual feedback loop.

## Workflow

1. **Name** - Derive a short filename from the part description (e.g., "lid_57mm", "bracket_m4", "enclosure_box")
2. **Generate** - Write CadQuery Python code based on user description
3. **Save** - Write code to `./generated/<part_name>.py`
4. **Validate + View** - Execute and send to OCP Viewer
5. **Screenshot** - Capture viewport for user feedback
6. **Iterate** - Refine based on user feedback

## Step 1: Derive Filename

Create a short, descriptive filename from the part description:
- Use lowercase with underscores
- Include key identifying info (type, size, feature)
- Keep it short (2-4 words max)

Examples:
- "a lid for a 57mm hole" → `lid_57mm.py`
- "mounting bracket with 4 M4 holes" → `bracket_m4.py`
- "enclosure 100x60x40" → `enclosure_100x60.py`
- "gear 20 teeth" → `gear_20t.py`

## Step 2: Generate CadQuery Code

Write clean, parametric CadQuery code:

```python
import cadquery as cq

# [Brief description of what we're building]
# Parameters at top for easy adjustment

param1 = 10.0  # mm - description
param2 = 5.0   # mm - description

result = (
    cq.Workplane("XY")
    .box(param1, param2, ...)
    # ... operations
)
```

**Code guidelines:**
- Use real dimensions (mm) - no normalized units
- Put parameters at the top with comments
- Name the final object `result`
- Keep it simple and readable

## Step 3: Save the Code

```python
# Save to: ./generated/<part_name>.py
```

## Step 4: Validate and Show in Viewer

```bash
python3 -c "
import cadquery as cq
from ocp_vscode import show

exec(open('generated/<part_name>.py').read())
bb = result.val().BoundingBox()
print(f'Dimensions: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm')
show(result)
"
```

## Step 5: Capture Screenshot

Use `mcp__ocp-viewer__capture_ocp_screenshot` to show the user what was generated.

## Step 6: Iterate

Ask user for feedback and refine. Common adjustments:
- Dimensions / tolerances
- Add fillets, chamfers
- Add holes, cutouts
- Change wall thickness

## Example Parts

**Simple lid:**
```python
result = (
    cq.Workplane("XY")
    .circle(15)
    .extrude(2)
    .faces(">Z").workplane()
    .circle(17.5)
    .extrude(1.2)
)
```

**Box with rounded edges:**
```python
result = (
    cq.Workplane("XY")
    .box(50, 30, 20)
    .edges("|Z")
    .fillet(3)
)
```

**Mounting bracket:**
```python
result = (
    cq.Workplane("XY")
    .box(40, 20, 3)
    .faces(">Z").workplane()
    .rect(30, 10, forConstruction=True)
    .vertices()
    .hole(4)  # M4 clearance
)
```

## Output

- Code saved to: `./generated/<part_name>.py`
- STL exported to: `./generated/<part_name>.stl`
- Viewable in OCP Viewer (VSCode extension)
