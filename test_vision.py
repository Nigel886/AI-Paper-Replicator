import os
import re
import time
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

class PaperReplicator:
    def __init__(self):
        # Initialize Client
        self.client = genai.Client(api_key=API_KEY)
        self.model_id = "models/gemini-flash-latest"

    def analyze_with_new_sdk(self, image_path, output_file="replicated_model.py"):
        if not os.path.exists(image_path):
            print(f"❌ Bro, image not found: {image_path}")
            return

        # --- 1. Added automatic retry logic (core modification) ---
        for attempt in range(3):
            try:
                print(f"🚀 [Attempt {attempt+1}] Engaging Gemini via New SDK...")
                img = Image.open(image_path)
                
                # 这里完全保留你写的原版提示词，一字不差
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[
                        "You are a Senior AI Research Engineer specializing in computer vision and deep learning. "
                        "Your mission is to analyze academic paper screenshots and provide high-quality, "
                        "production-ready PyTorch code. \n\n"
                        "Rules:\n"
                        "1. Focus on the core model architecture (layers, forward pass, activation functions).\n"
                        "2. Always include tensor shape comments for each major operation (e.g., # [B, 64, 56, 56]).\n"
                        "3. Use modular design (subclassing nn.Module).\n"
                        "4. If multiple interpretations exist, choose the most standard one in modern research.",
                        img
                    ]
                )
                
                print("\n--- The Moment of Truth (New SDK) ---")
                if response.text:
                    print(response.text)
                    # --- 2. Automatic Code Extraction & Persistence ---
                    self._extract_and_save(response.text, output_file)
                else:
                    print("⚠️ Response is empty, bro. Check your safety settings or image.")
                
                return response.text

            except Exception as e:
                # Exponential backoff for rate limiting
                if "429" in str(e) or "503" in str(e):
                    wait = (attempt + 1) * 15
                    print(f"⏳ Server busy, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"❌ Something went wrong, bro: {e}")
                    break
        return None

    def _extract_and_save(self, text, filename):
        """Extract code blocks using regular expressions and save them to a local file"""
        code_match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
        if code_match:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code_match.group(1))
            print(f"\n✅ Code successfully extracted and saved to: {filename}")
        else:
            print("\n⚠️ No Python code block found to save.")

# 3. Execution
if __name__ == "__main__":
    replicator = PaperReplicator()
    replicator.analyze_with_new_sdk('paper_shot.png')