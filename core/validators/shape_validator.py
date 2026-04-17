import torch
import json
import re
import traceback

class ShapeValidator:
    """
    Automated validation of generated PyTorch code by executing it with 
    synthetic data derived from a Shape Dictionary.
    """

    def __init__(self, default_batch_size=32):
        self.default_batch_size = default_batch_size
        # Mapping for common symbolic dimensions
        self.dim_mapping = {
            'B': 32,
            'N': 64,
            'M': 128,
            'C': 3,
            'H': 224,
            'W': 224,
            'D': 512
        }

    def validate(self, code, shape_dict_json):
        """
        Validates the code by running it with dummy tensors.
        Returns (is_valid, error_message).
        """
        try:
            # 1. Parse Shape Dictionary
            if isinstance(shape_dict_json, str):
                shape_info = json.loads(shape_dict_json)
            else:
                shape_info = shape_dict_json

            func_name = shape_info.get("function_name")
            inputs_config = shape_info.get("inputs", {})

            if not func_name:
                return False, "Missing 'function_name' in shape dictionary."

            # 2. Prepare Dummy Inputs
            dummy_inputs = {}
            for arg_name, shape in inputs_config.items():
                concrete_shape = []
                for dim in shape:
                    if isinstance(dim, int):
                        concrete_shape.append(dim)
                    elif isinstance(dim, str):
                        # Use mapped value or fallback to a default random int
                        concrete_shape.append(self.dim_mapping.get(dim.upper(), 16))
                    else:
                        concrete_shape.append(16)
                dummy_inputs[arg_name] = torch.randn(*concrete_shape)

            # 3. Execute code in a sandboxed namespace
            namespace = {"torch": torch, "torch.nn": torch.nn}
            exec(code, namespace)

            if func_name not in namespace:
                return False, f"Function '{func_name}' not found in the generated code."

            func = namespace[func_name]

            # 4. Run the function
            with torch.no_grad():
                # Call the function with keyword arguments
                func(**dummy_inputs)

            return True, None

        except Exception as e:
            error_msg = traceback.format_exc()
            return False, error_msg

    @staticmethod
    def extract_json_from_text(text):
        """Helper to extract JSON block from markdown text."""
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        # Fallback to finding the first { and last }
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            return match.group(1)
        return None
