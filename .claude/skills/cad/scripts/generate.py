#!/usr/bin/env python3
"""
CAD Part Generator - Text to CadQuery using fine-tuned model
"""

import sys
import torch
from pathlib import Path

# Paths relative to cadworld repo root
REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
MODEL_PATH = REPO_ROOT / "models" / "text2cadquery"
OUTPUT_DIR = REPO_ROOT / "generated"

def load_model():
    """Load the fine-tuned Text-to-CadQuery model."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print("Loading Text-to-CadQuery model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    tokenizer.padding_side = "left"
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    return model, tokenizer


def generate_code(prompt: str, model, tokenizer) -> str:
    """Generate CadQuery code from description."""
    formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"

    inputs = tokenizer(
        formatted_prompt,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )

    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "### Response:" in generated:
        code = generated.split("### Response:")[-1].strip()
    else:
        code = generated[len(formatted_prompt):].strip()

    return clean_code(code)


def clean_code(code: str) -> str:
    """Clean up generated code."""
    lines = code.split('\n')
    clean_lines = []
    seen_result = False

    for line in lines:
        if 'cq.exporters.export' in line:
            continue
        if 'from cadquery.vis import' in line:
            continue
        if line.strip().startswith('import cadquery') and any('import cadquery' in l for l in clean_lines):
            continue

        stripped = line.strip()
        is_final = stripped.startswith('result = ') or stripped.startswith('assembly = ')
        if is_final:
            if seen_result:
                break
            seen_result = True

        clean_lines.append(line)

    code = '\n'.join(clean_lines).strip()

    if not code.startswith('import'):
        code = 'import cadquery as cq\n\n' + code

    return code


def validate_code(code: str) -> tuple[bool, str, object]:
    """Validate and execute CadQuery code."""
    try:
        import cadquery as cq
        exec_globals = {"cq": cq}
        exec(code, exec_globals)

        result = exec_globals.get('result') or exec_globals.get('assembly')
        if result:
            bb = result.val().BoundingBox()
            return True, f"Valid! Dimensions: {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f}", result
        return True, "Code executed but no result variable", None
    except Exception as e:
        return False, f"Error: {str(e)}", None


def show_in_viewer(result):
    """Send result to OCP Viewer."""
    try:
        from ocp_vscode import show
        show(result)
        print("Sent to OCP Viewer!")
        return True
    except Exception as e:
        print(f"Could not show in viewer: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <part description>")
        sys.exit(1)

    description = ' '.join(sys.argv[1:])
    print(f"\n{'='*60}")
    print(f"Generating: {description}")
    print('='*60)

    # Load model
    model, tokenizer = load_model()

    # Generate code
    print("\nGenerating CadQuery code...")
    code = generate_code(description, model, tokenizer)

    print("\n--- Generated Code ---")
    print(code)
    print("--- End Code ---\n")

    # Validate
    valid, msg, result = validate_code(code)
    print(f"Validation: {msg}")

    if valid and result:
        # Save code
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / "latest.py"
        output_file.write_text(code)
        print(f"Saved to: {output_file}")

        # Show in viewer
        show_in_viewer(result)

    print('='*60)


if __name__ == "__main__":
    main()
