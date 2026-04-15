import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

# 1. Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Initialize Client
client = genai.Client(api_key=API_KEY)

print("--- Available Models ---")
try:
    for m in client.models.list():
        print(f"Model ID: {m.name}")
except Exception as e:
    print(f"List models failed: {e}")
print("------------------------\n")

def analyze_with_new_sdk(image_path):
    if not os.path.exists(image_path):
        print(f"❌ Bro, image not found: {image_path}")
        return

    try:
        print("🚀 Engaging Gemini via New SDK...")
        img = Image.open(image_path)
        
        response = client.models.generate_content(
            model="models/gemini-flash-latest", 
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
        else:
            print("⚠️ Response is empty, bro. Check your safety settings or image.")
        
    except Exception as e:
        print(f"❌ Something went wrong, bro: {e}")

# 3. Execution
if __name__ == "__main__":
    analyze_with_new_sdk('paper_shot.png')