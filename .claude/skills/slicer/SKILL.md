---
name: slicer
description: Analyze, optimize, and slice 3D models for printing. Works with 3MF files saved from Bambu Studio GUI. Use when the user wants to check print settings, optimize for speed/strength, or get print estimates.
argument-hint: [3mf file path or "optimize" or "analyze"]
allowed-tools: Bash(flatpak run --filesystem=/tmp com.bambulab.BambuStudio *), Bash(unzip *), Bash(python3 *), Bash(grep *), Bash(mkdir *), Bash(cp *), Bash(head *), Bash(cat *), Read, Write
---

# Bambu Studio Slicer Integration

Analyze, optimize, and slice 3D models using Bambu Studio CLI.

## Required Workflow

**IMPORTANT**: Bambu Studio CLI requires a 3MF file with printer/filament profiles.

```
/cad → generates STL to ./generated/<name>.stl
         ↓
User opens STL in Bambu Studio GUI → File → Save Project As → .3mf
         ↓
/slicer → analyzes, modifies settings, slices, shows estimates
```

**User must save 3MF manually** - Bambu Studio doesn't auto-save like OrcaSlicer.

If user asks to slice an STL directly, tell them:
> "Please open the STL in Bambu Studio first and save as 3MF. The CLI needs printer/filament profiles that the GUI provides."

## Capabilities

- **Analyze** - Get model geometry and current print settings
- **Optimize** - Adjust settings for speed, strength, or quality
- **Slice** - Generate gcode with time/filament estimates

## Finding User's 3MF File

```bash
# Find recently saved 3MF files
find ~ -name "*.3mf" -mmin -60 -type f 2>/dev/null | head -10
```

## Commands

### Analyze Model Geometry (works with STL)

```bash
flatpak run --filesystem=/tmp com.bambulab.BambuStudio --info /path/to/model.stl
```

### Check Current Settings (3MF only)

```bash
# Copy to /tmp for flatpak access
cp /path/to/model.3mf /tmp/

# Extract and show settings
unzip -p /tmp/model.3mf "Metadata/project_settings.config" 2>/dev/null | python3 -c "
import json, sys
try:
    s = json.load(sys.stdin)
    print(f'Layer height: {s.get(\"layer_height\", \"N/A\")}mm')
    print(f'Walls: {s.get(\"wall_loops\", \"N/A\")}')
    print(f'Infill: {s.get(\"sparse_infill_density\", \"N/A\")}')
    print(f'Brim: {s.get(\"brim_type\", \"N/A\")}')
    print(f'Support: {s.get(\"enable_support\", \"N/A\")}')
except:
    print('Could not parse settings')
"
```

### Slice and Get Estimates (3MF only)

```bash
# Copy 3MF to /tmp for flatpak sandbox access
cp /path/to/model.3mf /tmp/model.3mf

# Slice
flatpak run --filesystem=/tmp com.bambulab.BambuStudio \
  --slice 0 \
  --outputdir /tmp \
  /tmp/model.3mf

# Show print estimates
head -50 /tmp/plate_1.gcode | grep -E "(time|filament|layer)"
```

### Optimize Settings (3MF only)

```python
import json, zipfile, shutil, os, tempfile

input_3mf = '/tmp/input.3mf'
output_3mf = '/tmp/optimized.3mf'

# Copy original
shutil.copy(input_3mf, output_3mf)

# Extract, modify, repack
with tempfile.TemporaryDirectory() as tmpdir:
    with zipfile.ZipFile(output_3mf, 'r') as z:
        z.extractall(tmpdir)

    config_path = f'{tmpdir}/Metadata/project_settings.config'
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Apply optimization (example: strong preset)
    config.update({
        'layer_height': '0.16',
        'wall_loops': '4',
        'sparse_infill_density': '25%',
        'bottom_shell_layers': '4',
        'top_shell_layers': '5'
    })

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    os.remove(output_3mf)
    with zipfile.ZipFile(output_3mf, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(tmpdir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, tmpdir)
                z.write(filepath, arcname)

print(f'Saved: {output_3mf}')
```

## Optimization Presets

| Preset | Layer | Walls | Infill | Use Case |
|--------|-------|-------|--------|----------|
| fast | 0.28 | 2 | 10% | Prototypes |
| balanced | 0.20 | 3 | 15% | General use |
| strong | 0.16 | 4 | 25% | Functional parts |
| accurate | 0.12 | 3 | 20% | Tight tolerances |

## File Locations

- **Generated STL**: `./generated/<name>.stl`
- **User's 3MF**: Where user saves it (ask or search with `find`)
- **Sliced gcode**: `/tmp/plate_1.gcode`
- **Bambu config**: `~/.var/app/com.bambulab.BambuStudio/config/BambuStudio/`

## Example Workflow

User: `/slicer analyze lid1_bambu.3mf`

1. Find the file: `find ~ -name "lid1_bambu.3mf" -type f 2>/dev/null`
2. Copy to /tmp: `cp /path/to/lid1_bambu.3mf /tmp/`
3. Extract settings and show to user
4. Slice: `flatpak run --filesystem=/tmp com.bambulab.BambuStudio --slice 0 --outputdir /tmp /tmp/lid1_bambu.3mf`
5. Show estimates from gcode header

## Printer Profiles Available

Bambu Studio includes profiles for:
- Bambu Lab X1 Carbon / X1 / X1E
- Bambu Lab P1P / P1S
- Bambu Lab A1 / A1 mini
- And more in `~/.var/app/com.bambulab.BambuStudio/config/BambuStudio/system/BBL/machine/`
