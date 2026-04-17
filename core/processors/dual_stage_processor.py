from .base import BaseProcessor
from ..validators.shape_validator import ShapeValidator
from ..validators.logic_validator import LogicValidator
import re
import json

class DualStageProcessor(BaseProcessor):
    """
    Implements the "Two-Stage Prompting" strategy with Dual Validation:
    1. Shape Validation (Runtime check)
    2. Logic Consistency Validation (Structural check)
    """
    
    def __init__(self, engine):
        super().__init__(engine)
        self.shape_validator = ShapeValidator()
        self.logic_validator = LogicValidator()
        
        self.action_a_prompt = (
            "You are a specialized OCR engine for academic papers. Extract the "
            "mathematical formula from this image into raw LaTeX. DO NOT explain the "
            "formula. DO NOT simplify. Ensure all subscripts, superscripts, and Greek "
            "letters are preserved exactly."
        )
        
        self.action_b_template = (
            "Convert the following LaTeX formula into a PyTorch function.\n"
            "Formula: {latex}\n"
            "Requirements:\n"
            "1. Use clear variable names, include docstrings defining tensor shapes.\n"
            "2. Ensure the code logic (Sum, Max, Expectation, etc.) strictly matches the formula.\n"
            "3. Provide two JSON blocks at the very end:\n"
            "\n"
            "A 'Shape Dictionary' for validation:\n"
            "```json\n"
            "{{\"function_name\": \"name\", \"inputs\": {{\"x\": [B, N]}} }}\n"
            "```\n"
            "\n"
            "A 'Logic Specification' of required operators found in the formula:\n"
            "```json\n"
            "{{\"required_operators\": [\"Sum\", \"Max\", \"Exp\"]}}\n"
            "```"
        )

    def process(self, image_path, **kwargs):
        # --- Action A: Vision-to-LaTeX ---
        print(f"[PureRepro] Action A: Extracting LaTeX...")
        raw_latex = self.engine.infer(image_path, self.action_a_prompt)
        latex_output = self.clean_output(raw_latex)
        
        if not latex_output:
            return {"error": "Action A failed."}

        # --- Action B: LaTeX-to-Code with Dual-Loop ---
        current_prompt = self.action_b_template.format(latex=latex_output)
        
        max_corrections = 2
        for attempt in range(max_corrections + 1):
            print(f"[PureRepro] Generation Attempt {attempt + 1}...")
            response = self.engine._generate_with_retry(current_prompt)
            full_response = response.text
            
            code_output = self.clean_output(full_response)
            
            # 1. Shape Validation
            shape_json = ShapeValidator.extract_json_from_text(full_response)
            shape_valid, shape_error = self.shape_validator.validate(code_output, shape_json)
            
            # 2. Logic Validation
            logic_json = self.logic_validator.extract_logic_spec(full_response)
            logic_valid, logic_error = self.logic_validator.validate_consistency(code_output, logic_json)
            
            if shape_valid and logic_valid:
                print("[PureRepro] Dual Validation Success!")
                return {
                    "latex": latex_output, 
                    "code": code_output, 
                    "validated": True
                }
            
            # Feedback Loop
            errors = []
            if not shape_valid: errors.append(f"Dimension Error: {shape_error}")
            if not logic_valid: errors.append(f"Logic Error: {logic_error}")
            
            if attempt < max_corrections:
                feedback = "\n".join(errors)
                print(f"[PureRepro] Validation failed. Sending feedback...")
                current_prompt += f"\n\n--- FEEDBACK ---\n{feedback}\nPlease fix the code to resolve these issues."
            else:
                return {
                    "latex": latex_output, 
                    "code": code_output, 
                    "error": "; ".join(errors),
                    "validated": False
                }
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
