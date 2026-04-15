import os
import argparse
from dotenv import load_dotenv
from core.engine import PaperReplicator
from utils.file_handler import save_analysis_results

def main():
    # 1. Load environment variables (API Keys, etc.)
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables.")
        return

    # 2. Initialize Command Line Argument Parser
    parser = argparse.ArgumentParser(description="AI Paper Replicator - Professional CLI Tool")
    
    parser.add_argument(
        '--images', 
        nargs='+', 
        required=True, 
        help="Space-separated list of image names or paths"
    )
    
    parser.add_argument(
        '--output', 
        type=str, 
        default="replicated_model.py", 
        help="Desired filename for the generated PyTorch code"
    )
    
    args = parser.parse_args()

    # 3. Pre-process image paths: If the file isn't in root, check the inputs/ folder
    processed_paths = []
    for img_path in args.images:
        if not os.path.exists(img_path):
            alternative_path = os.path.join("inputs", img_path)
            if os.path.exists(alternative_path):
                print(f"📂 Auto-located: {img_path} -> {alternative_path}")
                processed_paths.append(alternative_path)
            else:
                processed_paths.append(img_path) 
        else:
            processed_paths.append(img_path)

    # 4. Initialize the core AI engine (MUST be before calling analyze_paper_set)
    replicator = PaperReplicator(api_key)
    
    print(f"🛠️  Processing {len(processed_paths)} input file(s)...")
    
    # 5. Execute analysis on the PROCESSED image set
    raw_response = replicator.analyze_paper_set(processed_paths)
    
    # 6. Persist the extracted code
    if raw_response:
        print("\n--- Synthesis Complete ---")
        save_analysis_results(raw_response, args.output)
    else:
        print("❌ Failed to generate content. Please check the logs above.")

if __name__ == "__main__":
    main()