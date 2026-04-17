from .base import BaseProcessor
from ..validators.shape_validator import ShapeValidator
import re

class DualStageProcessor(BaseProcessor):
    """
    Implements the "Two-Stage Prompting" strategy with Shape Validation:
    Action A: Vision-to-LaTeX (The 'Typist' phase)
    Action B: LaTeX-to-Code (The 'Programmer' phase)
    Post-processing: Shape Validation & Self-Correction
    """
    
    def __init__(self, engine):
        super().__init__(engine)
        self.validator = ShapeValidator()
        # Specific prompts as requested by the user
        self.action_a_prompt = (
            "You are a specialized OCR engine for academic papers. Extract the "
            "mathematical formula from this image into raw LaTeX. DO NOT explain the "
            "formula. DO NOT simplify. Ensure all subscripts, superscripts, and Greek "
            "letters are preserved exactly."
        )
        
        self.action_b_template = (
            "Convert the following LaTeX formula into a PyTorch function.\n"
            "Formula: {latex}\n"
            "Context: It belongs to a Reinforcement Learning agent.\n"
            "Requirements:\n"
            "1. Use clear variable names, include docstrings defining tensor shapes.\n"
            "2. At the very end, provide a 'Shape Dictionary' in a JSON block with this structure: "
            "```json\n"
            "{{\"function_name\": \"name_of_function\", \"inputs\": {{\"arg1\": [B, N], \"arg2\": [N, M]}} }}\n"
            "```\n"
            "Use symbolic dimensions like B, N, M or integers."
        )

    def process(self, image_path, **kwargs):
        """
        Executes the two-stage prompting flow with automated shape validation.
        """
        # --- Action A: Vision-to-LaTeX ---
        print(f"[DualStage] Action A: Extracting LaTeX from {image_path}...")
        raw_latex = self.engine.infer(image_path, self.action_a_prompt)
        latex_output = self.clean_output(raw_latex)
        
        if not latex_output:
            return {"error": "Failed to extract LaTeX in Action A."}

        # --- Action B: LaTeX-to-Code with Feedback Loop ---
        print(f"[DualStage] Action B: Converting LaTeX to PyTorch code...")
        current_prompt = self.action_b_template.format(latex=latex_output)
        
        max_corrections = 2
        for attempt in range(max_corrections + 1):
            try:
                print(f"[DualStage] Generation Attempt {attempt + 1}...")
                response = self.engine._generate_with_retry(current_prompt)
                full_response = response.text
                
                # Extract code and shape dictionary
                code_output = self.clean_output(full_response)
                shape_json_str = ShapeValidator.extract_json_from_text(full_response)
                
                if not shape_json_str:
                    print("[DualStage] Warning: No Shape Dictionary found in response.")
                    # If we can't find JSON, we can't validate, so we return what we have
                    return {"latex": latex_output, "code": code_output, "validated": False}

                # Validate dimensions
                is_valid, error_log = self.validator.validate(code_output, shape_json_str)
                
                if is_valid:
                    print("[DualStage] Validation Success! Code is dimensionally sound.")
                    return {
                        "latex": latex_output, 
                        "code": code_output, 
                        "shape_dict": shape_json_str,
                        "validated": True
                    }
                else:
                    print(f"[DualStage] Validation Failed on attempt {attempt + 1}.")
                    if attempt < max_corrections:
                        # Feed back the error to the model
                        feedback_prompt = (
                            f"The code you generated failed validation with the following error:\n"
                            f"```\n{error_log}\n```\n"
                            f"Please fix the code (e.g., check for missing transposes or dimension mismatches) "
                            f"and provide the corrected version along with the Shape Dictionary."
                        )
                        current_prompt = f"{current_prompt}\n\n---\nFEEDBACK:\n{feedback_prompt}"
                    else:
                        print("[DualStage] Max corrections reached. Returning last attempt.")
                        return {
                            "latex": latex_output, 
                            "code": code_output, 
                            "error": error_log,
                            "validated": False
                        }

            except Exception as e:
                print(f"[DualStage] Action B Error: {e}")
                return {"latex": latex_output, "error": str(e), "validated": False}

    def clean_output(self, text):
        """
        Cleans model output by extracting the actual code/content.
        Prioritizes extracting from triple backticks if present.
        """
        if not text:
            return ""
        
        # Try to find a code block (e.g., ```python ... ```)
        match = re.search(r"```(?:python|latex)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # Fallback to simple stripping
        return text.strip()
