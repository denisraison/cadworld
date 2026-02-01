#!/usr/bin/env python3
"""
Text-to-CadQuery Inference Script
Uses the fine-tuned ricemonster/qwen2.5-3B-SFT model for CadQuery code generation.

Prompt format from official repo:
### Instruction:
{description}

### Response:
"""

import argparse
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model path relative to this script's location
SCRIPT_DIR = Path(__file__).parent.resolve()
MODEL_PATH = SCRIPT_DIR / "models" / "text2cadquery"

def load_model(model_path: str = MODEL_PATH):
    """Load the fine-tuned model and tokenizer."""
    print(f"Loading model from {model_path}...")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    tokenizer.padding_side = "left"
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )

    print(f"Model loaded on {next(model.parameters()).device}")
    return model, tokenizer


def generate_cadquery(prompt: str, model, tokenizer, max_new_tokens: int = 512) -> str:
    """Generate CadQuery code from a text description."""

    # Official prompt format from Text-to-CadQuery repo
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
            max_new_tokens=max_new_tokens,
            do_sample=False,  # Deterministic output as per official code
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id
        )

    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract response after "### Response:"
    if "### Response:" in generated:
        code = generated.split("### Response:")[-1].strip()
    else:
        code = generated[len(formatted_prompt):].strip()

    # Clean up the code
    code = clean_generated_code(code)

    return code


def clean_generated_code(code: str) -> str:
    """Clean up generated code - remove duplicates, exports, etc."""
    lines = code.split('\n')
    clean_lines = []
    seen_result = False
    result_line_idx = -1

    for i, line in enumerate(lines):
        # Skip export statements (training artifact)
        if 'cq.exporters.export' in line:
            continue
        # Skip visualization imports
        if 'from cadquery.vis import' in line:
            continue
        # Skip duplicate imports after first occurrence
        if line.strip().startswith('import cadquery') and any('import cadquery' in l for l in clean_lines):
            continue

        # Track when we hit "result = " or "assembly = " - this typically ends the code
        stripped = line.strip()
        is_final_assignment = (
            stripped.startswith('result = ') or stripped.startswith('result=') or
            stripped.startswith('assembly = ') or stripped.startswith('assembly=')
        )
        if is_final_assignment:
            if seen_result:
                # Second result/assembly = means we're in duplicate territory
                break
            seen_result = True
            result_line_idx = len(clean_lines)

        clean_lines.append(line)

    # If we found a result, include it and stop
    if result_line_idx >= 0:
        clean_lines = clean_lines[:result_line_idx + 1]

    code = '\n'.join(clean_lines).strip()

    # Ensure it starts with import
    if not code.startswith('import'):
        code = 'import cadquery as cq\n\n' + code

    return code


def validate_cadquery(code: str) -> tuple[bool, str]:
    """Validate CadQuery code by attempting to execute it."""
    try:
        import cadquery as cq
        exec_globals = {"cq": cq}
        exec(code, exec_globals)

        # Check if 'result' variable exists
        if 'result' in exec_globals:
            return True, "Valid CadQuery code - 'result' object created"
        else:
            return True, "Code executed but no 'result' variable found"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Generate CadQuery code from text descriptions")
    parser.add_argument("prompt", nargs="?", help="Text description of the CAD model")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--validate", "-v", action="store_true", help="Validate generated code")
    parser.add_argument("--output", "-o", help="Save code to file")
    parser.add_argument("--model-path", default=MODEL_PATH, help="Path to model")
    args = parser.parse_args()

    model, tokenizer = load_model(args.model_path)

    if args.interactive:
        print("\n" + "="*50)
        print("Text-to-CadQuery Interactive Mode")
        print("Fine-tuned qwen2.5-3B-SFT model")
        print("Type 'quit' to exit")
        print("="*50 + "\n")

        while True:
            prompt = input("Describe your part: ").strip()
            if prompt.lower() in ['quit', 'exit', 'q']:
                break
            if not prompt:
                continue

            print("\nGenerating CadQuery code...\n")
            code = generate_cadquery(prompt, model, tokenizer)
            print("```python")
            print(code)
            print("```")

            if args.validate:
                valid, msg = validate_cadquery(code)
                status = "✓" if valid else "✗"
                print(f"\n{status} {msg}")

            print("\n" + "="*50 + "\n")

    elif args.prompt:
        code = generate_cadquery(args.prompt, model, tokenizer)
        print(code)

        if args.validate:
            valid, msg = validate_cadquery(code)
            print(f"\n# {msg}", file=__import__('sys').stderr)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(code)
            print(f"\n# Saved to {args.output}", file=__import__('sys').stderr)

    else:
        parser.print_help()
        print("\nExamples:")
        print('  python text2cadquery_inference.py "A box with dimensions 50mm x 30mm x 20mm"')
        print('  python text2cadquery_inference.py -i  # Interactive mode')
        print('  python text2cadquery_inference.py -v "L-bracket with 4 M4 holes"  # With validation')


if __name__ == "__main__":
    main()
