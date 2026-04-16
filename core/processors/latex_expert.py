from .base import BaseProcessor

class LatexExpert(BaseProcessor):
    """
    Expert processor dedicated to high-precision LaTeX OCR extraction.
    This class acts as a domain-specific logic layer on top of the core engine.
    """
    def __init__(self, engine):
        super().__init__(engine)
        # Fixed high-fidelity prompt to ensure structural integrity of mathematical symbols
        self.system_prompt = (
            "You are a LaTeX OCR expert. Convert the formula in the image to raw LaTeX code. "
            "Ensure all subscripts, superscripts, and Greek letters are preserved exactly. "
            "Output ONLY the LaTeX string without any markdown code blocks."
        )

    def process(self, image_path):
        """
        Executes the extraction task using the underlying engine.
        :param image_path: Local path to the formula image.
        :return: Post-processed LaTeX string.
        """
        # Leverage the engine's inference capability while providing task-specific instructions
        raw_result = self.engine.infer(image_path, self.system_prompt)
        return self.post_process(raw_result)

    def post_process(self, text):
        """
        Cleans the model output by removing markdown artifacts and whitespace.
        :param text: Raw output string from the model.
        :return: Clean LaTeX code snippet.
        """
        if not text:
            return ""
        # Remove common markdown wrappers to ensure the output is pure LaTeX code
        return text.replace("```latex", "").replace("```", "").strip()