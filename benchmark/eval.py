import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv  # Ensure you have 'python-dotenv' installed

# 1. Path Configuration
# Add the project root to sys.path to ensure 'core' can be imported correctly
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
sys.path.append(project_root)

# Load environment variables from the .env file in the root directory
load_dotenv(os.path.join(project_root, ".env"))

# 2. Core Module Imports
try:
    from core.engine import PaperReplicator 
    from core.processors.latex_expert import LatexExpert
except ImportError as e:
    print(f"Error: Could not import core modules. Please verify file structure. {e}")
    sys.exit(1)

def run_benchmark():
    """
    Main execution script for the PureRepro precision benchmark.
    """
    # 3. Directory Setup
    # Using absolute paths based on project_root for maximum robustness
    samples_dir = os.path.join(project_root, "benchmark", "samples")
    log_dir = os.path.join(project_root, "benchmark", "logs")
    
    if not os.path.exists(samples_dir):
        print(f"Error: Samples directory not found at {samples_dir}")
        return

    os.makedirs(log_dir, exist_ok=True)

    # 4. Initialization with Environment Variables
    # Fetch API key from .env. Change "GEMINI_API_KEY" if your key has a different name.
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: 'GEMINI_API_KEY' not found in .env file.")
        return

    # Dependency Injection: Expert relies on the Engine
    try:
        engine = PaperReplicator(api_key=api_key) 
        expert = LatexExpert(engine)
    except Exception as e:
        print(f"Error initializing Engine/Expert: {e}")
        return

    results = []
    print(f"--- PureRepro Precision Evaluation Started ---")

    # 5. Processing Loop
    image_files = [f for f in os.listdir(samples_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"No images found in: {samples_dir}")
        return

    for img_name in sorted(image_files): # Sort to maintain order sample_01, 02...
        img_path = os.path.join(samples_dir, img_name)
        print(f"Processing: {img_name}...")
        
        try:
            # High-precision task-specific logic handled by the Expert
            latex_output = expert.process(img_path)
            
            results.append({
                "filename": img_name,
                "prediction": latex_output,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            print(f"✅ Successfully processed {img_name}")
            
        except Exception as e:
            print(f"❌ Failed to process {img_name}: {str(e)}")
            results.append({
                "filename": img_name,
                "error": str(e),
                "status": "failed"
            })

    # 6. Report Generation
    timestamp = datetime.now().strftime("%m%d_%H%M")
    report_name = f"eval_report_{timestamp}.json"
    report_path = os.path.join(log_dir, report_name)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n--- Evaluation Complete ---")
    print(f"Total processed: {len(results)}")
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    run_benchmark()