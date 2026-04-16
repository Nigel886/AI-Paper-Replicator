import google.generativeai as genai
import os
import PIL.Image

class PaperReplicator:
    def __init__(self, api_key):
        """
        Initialize the Gemini engine with the stable production model.
        """
        if not api_key:
            print("[Critical] API Key is missing! Check your .env file.")
        
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash: Stable, multimodal, and publicly available.
        # Ensure you run 'pip install -U google-generativeai' to support this model.
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze_paper_set(self, image_paths):
        """
        Analyzes paper images and returns a structured report.
        """
        # Raw string (r"") is used to handle LaTeX backslashes without SyntaxWarnings
        prompt = r"""
        You are a world-class AI research engineer specializing in paper replication.
        I will provide you with images containing parts of a research paper (architecture, formulas, or descriptions).
        
        Your goal is to replicate the core logic into clean, runnable Python code.
        
        STRICT OUTPUT FORMAT:
        You must organize your response into exactly three sections using these exact Markdown headers:
        
        ## 1. Overview
        Provide a concise summary of the paper's core innovation and mathematical objective. Use LaTeX for formulas (e.g., $ \phi $).
        
        ## 2. Implementation Code
        Provide the complete, well-commented Python implementation. Wrap the code in triple backticks: ```python [code] ```.
        
        ## 3. Key Engineering Insights
        List the most critical implementation details, hyperparameters, or training nuances found in the paper as bullet points.
        
        Begin the analysis now.
        """
        
        contents = [prompt]
        
        # 1. Load and Verify Images
        valid_images = 0
        for path in image_paths:
            if os.path.exists(path):
                try:
                    img = PIL.Image.open(path)
                    # Ensuring RGB compatibility for standardized processing
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    contents.append(img)
                    valid_images += 1
                except Exception as e:
                    print(f"[Engine] Error processing image {path}: {e}")
        
        if valid_images == 0:
            return "## 1. Overview\nError: No valid images found.\n\n## 2. Implementation Code\n# No images were processed.\n\n## 3. Key Engineering Insights\n* Please ensure you are uploading valid image files."

        # 2. Call Gemini API with safety handling
        try:
            print(f"[Engine] Sending {valid_images} images to Gemini...")
            response = self.model.generate_content(contents)
            
            if not response.text:
                raise ValueError("Empty response from AI.")
                
            return response.text

        except Exception as e:
            # Detailed error reporting to the frontend UI
            error_details = str(e)
            print(f"[Engine] API Call Failed: {error_details}")
            
            return f"""## 1. Overview
Analysis Failed.

## 2. Implementation Code
# ERROR: {error_details}
# Potential Fixes:
# 1. Run 'pip install -U google-generativeai' to support 1.5 models.
# 2. Check if your API Key has access to 'gemini-1.5-flash' in Google AI Studio.
# 3. Verify your internet connection or proxy settings.

## 3. Key Engineering Insights
* Execution failed at the API layer. Technical details: {error_details[:100]}..."""