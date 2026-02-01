import cadquery as cq

# --- L-shaped Mounting Bracket ---
# Dimensions in normalized units (multiply by 100 for mm)

sketch_scale = 0.75
extrude_depth = 0.05

# Base plate: 0.75 x 0.4 x 0.05
# Vertical arm: 0.5 tall from one end

# Sketch points for L-shape profile
base_length = 0.75 * sketch_scale
base_width = 0.4 * sketch_scale
arm_height = 0.5 * sketch_scale
thickness = 0.05

# Create L-bracket as two joined boxes
# Horizontal base
base = (
    cq.Workplane("XY")
    .box(base_length, base_width, thickness)
)

# Vertical arm (at one end)
arm = (
    cq.Workplane("XZ")
    .center(-base_length/2 + thickness/2, thickness/2)
    .box(thickness, arm_height, base_width)
    .translate((0, 0, arm_height/2))
)

# Combine
bracket = base.union(arm)

# Add mounting holes
hole_diameter = 0.03 * sketch_scale
hole_radius = hole_diameter / 2

# Holes on base (2 holes)
bracket = (
    bracket.faces(">Z").workplane()
    .pushPoints([
        (base_length/2 - 0.08, base_width/2 - 0.08),
        (base_length/2 - 0.08, -base_width/2 + 0.08)
    ])
    .hole(hole_diameter)
)

# Holes on vertical arm (2 holes)
bracket = (
    bracket.faces("<X").workplane()
    .pushPoints([
        (0.1, arm_height/2 - 0.05),
        (0.1, arm_height/2 + 0.15)
    ])
    .hole(hole_diameter)
)

result = bracket

# For OCP Viewer
if __name__ == "__main__":
    from ocp_vscode import show
    show(result)
