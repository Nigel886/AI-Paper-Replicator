import time
from PIL import Image
from google import genai
from google.genai import types

class PaperReplicator:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "models/gemini-flash-latest"

    def analyze_paper_set(self, image_paths):
        """Analyze a list of images and return the raw text response."""
        valid_images = []
        for path in image_paths:
            try:
                valid_images.append(Image.open(path))
            except Exception as e:
                print(f"⚠️ Warning: Could not open {path}: {e}")

        if not valid_images:
            return None

        # --- Your High-Standard Prompt Stays Here ---
        prompt = (
            "You are a Senior AI Research Engineer specializing in computer vision and deep learning. "
            "Your mission is to analyze academic paper screenshots and provide high-quality, "
            "production-ready PyTorch code. \n\n"
            "Rules:\n"
            "1. Focus on the core model architecture (layers, forward pass, activation functions).\n"
            "2. Always include tensor shape comments for each major operation (e.g., # [B, 64, 56, 56]).\n"
            "3. Use modular design (subclassing nn.Module).\n"
            "4. If multiple interpretations exist, choose the most standard one in modern research."
        )

        for attempt in range(3):
            try:
                print(f"🚀 [Attempt {attempt+1}] Analyzing {len(valid_images)} images...")
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[prompt] + valid_images
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "503" in str(e):
                    wait = (attempt + 1) * 15
                    print(f"⏳ Server busy, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise e
        return None